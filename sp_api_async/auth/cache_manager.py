import os
import logging
from pathlib import Path
from typing import Optional, Any
from abc import ABC, abstractmethod
from cachetools import TTLCache

try:
    import diskcache  # type: ignore
except ImportError:
    diskcache = None

logger = logging.getLogger(__name__)

# 缓存类注册表
_cache_factories: dict[str, type["BaseCache"]] = {}


class BaseCache(ABC):
    """
    缓存接口抽象基类，定义统一的缓存操作接口。

    继承此类的子类会自动注册为可用的缓存类型。
    子类必须定义 cache_type_name 类属性来指定注册名称。

    示例:
        class MyCache(BaseCache):
            cache_type_name = "my_custom_cache"  # 必选，指定注册名

            def __init__(self, maxsize, ttl, cache_name):
                # 实现初始化
                pass

            def get(self, key):
                # 实现获取逻辑
                pass

            def set(self, key, value):
                # 实现设置逻辑
                pass

            def clear(self):
                # 实现清空逻辑
                pass
    """

    def __init_subclass__(cls, **kwargs):
        """
        子类初始化钩子，自动注册继承 BaseCache 的类。

        要求子类必须定义 cache_type_name 类属性，否则会抛出 TypeError。
        """
        super().__init_subclass__(**kwargs)

        # 检查 cache_type_name 是否定义
        cache_type_name = getattr(cls, "cache_type_name", None)
        if cache_type_name is None:
            raise TypeError(
                f"Class '{cls.__name__}' must define 'cache_type_name' class attribute. "
                f"Example: cache_type_name = 'my_cache'"
            )

        # 自动注册（直接注册类本身，类是可调用的）
        if cache_type_name in _cache_factories:
            logger.warning(f"Cache type '{cache_type_name}' already registered, overwriting with '{cls.__name__}'")

        _cache_factories[cache_type_name] = cls
        logger.debug(f"Auto-registered cache type '{cache_type_name}' from class '{cls.__name__}'")

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值，不存在返回 None"""

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """设置缓存值"""

    @abstractmethod
    def clear(self) -> None:
        """清空缓存"""


class MemoryCache(BaseCache):
    """内存缓存实现，基于 cachetools.TTLCache"""

    cache_type_name = "memory"

    def __init__(self, maxsize: int = 10, ttl: int = 3200, cache_name: str = ""):
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
        logger.debug("Using memory cache")

    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value

    def clear(self) -> None:
        self._cache.clear()


class DiskCache(BaseCache):
    """磁盘缓存实现，基于 diskcache，支持进程间持久化"""

    cache_type_name = "disk"

    def __init__(self, maxsize: int = 10, ttl: int = 3200, cache_name: str = "amazon_sp_api_cache"):
        if diskcache is None:
            raise ImportError("diskcache is not installed. Install it with: uv add diskcache")

        cache_dir = os.environ.get("SP_API_CACHE_DIR", str(Path.home() / ".sp_api_cache"))
        # 在路径中包含 maxsize 和 ttl 以确保不同配置的实例使用不同的磁盘路径
        cache_path = Path(cache_dir) / cache_name / f"maxsize_{maxsize}_ttl_{ttl}"
        cache_path.mkdir(parents=True, exist_ok=True)
        self._cache = diskcache.Cache(str(cache_path), size_limit=maxsize * 1024 * 1024)
        self._ttl = ttl
        logger.debug(f"Using disk cache at {cache_path}")

    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key, default=None)

    def set(self, key: str, value: Any) -> None:
        self._cache.set(key, value, expire=self._ttl)

    def clear(self) -> None:
        self._cache.clear()

    def close(self) -> None:
        if hasattr(self._cache, "close"):
            self._cache.close()


# 单例缓存实例存储
_cache_instances: dict[str, BaseCache] = {}


def get_cache_manager(
    maxsize: int = 10,
    ttl: int = 3200,
    cache_name: str = "default",
    cache_type: Optional[str] = None,
) -> BaseCache:
    """
    获取缓存管理器实例（单例模式）。

    根据环境变量或参数自动选择缓存实现，相同配置返回同一实例。

    通过环境变量 SP_API_CACHE_TYPE 或 cache_type 参数控制缓存类型：
    - disk: 使用磁盘缓存，支持进程间持久化（如果 diskcache 已安装）
    - memory: 使用内存缓存
    - 其他已注册的自定义缓存类型名称

    如果没有指定 cache_type 且未设置环境变量，则：
    - 如果 diskcache 已安装，默认使用 disk
    - 否则默认使用 memory

    :param maxsize: 缓存最大大小
    :param ttl: 缓存过期时间（秒）
    :param cache_name: 缓存名称，用于区分不同的缓存实例
    :param cache_type: 缓存类型名称，如果提供则优先使用，否则从环境变量读取
    :return: BaseCache 实例
    """
    # 确定缓存类型：优先使用参数，其次环境变量，最后根据 diskcache 是否可用决定默认值
    if cache_type is None:
        cache_type = os.environ.get("SP_API_CACHE_TYPE")
        if cache_type is None:
            # 如果 diskcache 可用，默认使用 disk，否则使用 memory
            cache_type = "disk" if diskcache is not None else "memory"
    cache_type = cache_type.lower()

    # 生成唯一键：{cache_type}:{cache_name}:{maxsize}:{ttl}
    config_key = f"{cache_type}:{cache_name}:{maxsize}:{ttl}"

    # 如果已存在相同配置的实例，直接返回
    if config_key in _cache_instances:
        return _cache_instances[config_key]

    # 创建新实例
    cache_class = _cache_factories.get(cache_type)
    if cache_class is None:
        logger.warning(f"Cache type '{cache_type}' not found, falling back to memory cache")
        cache_class = MemoryCache

    try:
        cache_instance = cache_class(maxsize=maxsize, ttl=ttl, cache_name=cache_name)
    except Exception as e:
        logger.warning(f"Failed to initialize cache '{cache_type}': {e}, falling back to memory cache")
        cache_instance = MemoryCache(maxsize=maxsize, ttl=ttl, cache_name=cache_name)

    _cache_instances[config_key] = cache_instance
    return cache_instance
