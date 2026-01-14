import os
import logging
from pathlib import Path
from typing import Optional, Any, Callable
from abc import ABC, abstractmethod, ABCMeta
from cachetools import TTLCache

try:
    import diskcache

    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False

logger = logging.getLogger(__name__)

# 缓存工厂函数注册表
_cache_factories: dict[str, Callable[[int, int, str], "BaseCache"]] = {}


class CacheMeta(ABCMeta):
    """
    缓存元类，自动注册继承 BaseCache 的类。

    如果类定义了 cache_type_name 类属性，则使用该名称注册；
    否则使用类名的小写形式（去除 'Cache' 后缀）作为注册名。
    """

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        # 跳过抽象基类 BaseCache 本身（通过类名和抽象方法检查）
        if name == "BaseCache":
            return cls

        # 检查是否是 BaseCache 的子类（通过检查 bases）
        is_basecache_subclass = any(
            base.__name__ == "BaseCache" or "BaseCache" in [b.__name__ for b in base.__mro__] for base in bases
        )

        # 跳过抽象类（有未实现的抽象方法）
        has_abstract_methods = bool(getattr(cls, "__abstractmethods__", None))

        # 只注册非抽象的 BaseCache 子类
        if is_basecache_subclass and not has_abstract_methods:
            # 确定注册名称
            cache_type_name = getattr(cls, "cache_type_name", None)
            if cache_type_name is None:
                # 使用类名的小写形式，去除末尾的 'Cache' 后缀
                name_lower = name.lower()
                if name_lower.endswith("cache"):
                    cache_type_name = name_lower[:-5].strip("_")
                else:
                    cache_type_name = name_lower
                if not cache_type_name:
                    cache_type_name = name_lower

            # 创建工厂函数
            def factory(maxsize: int, ttl: int, cache_name: str) -> BaseCache:
                return cls(maxsize=maxsize, ttl=ttl, cache_name=cache_name)

            # 自动注册
            if cache_type_name in _cache_factories:
                logger.warning(f"Cache type '{cache_type_name}' already registered, " f"overwriting with '{name}'")

            _cache_factories[cache_type_name] = factory
            logger.debug(f"Auto-registered cache type '{cache_type_name}' from class '{name}'")

        return cls


class BaseCache(ABC, metaclass=CacheMeta):
    """
    缓存接口抽象基类，定义统一的缓存操作接口。

    继承此类的子类会自动注册为可用的缓存类型。
    可以通过设置 cache_type_name 类属性来指定注册名称，
    否则将使用类名的小写形式（去除 'Cache' 后缀）作为注册名。

    示例:
        class MyCache(BaseCache):
            cache_type_name = "my_custom_cache"  # 可选，指定注册名

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

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值，不存在返回 None"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """设置缓存值"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """清空缓存"""
        pass


class MemoryCache(BaseCache):
    """内存缓存实现，基于 cachetools.TTLCache"""

    cache_type_name = "memory"

    def __init__(self, maxsize: int = 10, ttl: int = 3200, cache_name: str = ""):
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
        logger.debug("Using memory cache")

    def get(self, key: str) -> Optional[Any]:
        try:
            return self._cache[key]
        except KeyError:
            return None

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value

    def clear(self) -> None:
        self._cache.clear()


class DiskCache(BaseCache):
    """磁盘缓存实现，基于 diskcache，支持进程间持久化"""

    cache_type_name = "disk"

    def __init__(self, maxsize: int = 10, ttl: int = 3200, cache_name: str = "amazon_sp_api_cache"):
        if not DISKCACHE_AVAILABLE:
            raise ImportError("diskcache is not installed. Install it with: uv add diskcache")

        cache_dir = os.environ.get("SP_API_CACHE_DIR", str(Path.home() / ".sp_api_cache"))
        cache_path = Path(cache_dir) / cache_name
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
    获取缓存管理器实例（工厂函数，单例模式）。

    根据环境变量或参数自动选择缓存实现，相同配置返回同一实例。

    通过环境变量 SP_API_CACHE_TYPE 或 cache_type 参数控制缓存类型：
    - memory: 使用内存缓存（默认）
    - disk: 使用磁盘缓存，支持进程间持久化
    - 其他已注册的自定义缓存类型名称

    :param maxsize: 缓存最大大小
    :param ttl: 缓存过期时间（秒）
    :param cache_name: 缓存名称，用于区分不同的缓存实例
    :param cache_type: 缓存类型名称，如果提供则优先使用，否则从环境变量读取
    :return: BaseCache 实例
    """
    # 确定缓存类型：优先使用参数，其次环境变量，最后默认 disk
    if cache_type is None:
        cache_type = os.environ.get("SP_API_CACHE_TYPE", "disk")
    cache_type = cache_type.lower()

    # 生成唯一键：{cache_type}:{cache_name}:{maxsize}:{ttl}
    config_key = f"{cache_type}:{cache_name}:{maxsize}:{ttl}"

    # 如果已存在相同配置的实例，直接返回
    if config_key in _cache_instances:
        return _cache_instances[config_key]

    # 创建新实例
    cache_instance: BaseCache

    # 检查注册的工厂函数
    try:
        cache_instance = _cache_factories[cache_type](maxsize=maxsize, ttl=ttl, cache_name=cache_name)
    except Exception as e:
        logger.warning(f"Failed to initialize cache '{cache_type}': {e}, " "falling back to memory cache")
        cache_instance = MemoryCache(maxsize=maxsize, ttl=ttl, cache_name=cache_name)

    _cache_instances[config_key] = cache_instance
    return cache_instance
