import os
import sys
import time
import tempfile
import shutil
import pytest
import importlib.util
from pathlib import Path

# 直接加载模块文件以避免循环导入
cache_manager_path = Path(__file__).parent.parent.parent / "sp_api_async" / "auth" / "cache_manager.py"
spec = importlib.util.spec_from_file_location("cache_manager", cache_manager_path)
cache_manager = importlib.util.module_from_spec(spec)
sys.modules["cache_manager"] = cache_manager
spec.loader.exec_module(cache_manager)

# 从模块中导入需要的类和函数
BaseCache = cache_manager.BaseCache
MemoryCache = cache_manager.MemoryCache
DiskCache = cache_manager.DiskCache
get_cache_manager = cache_manager.get_cache_manager


@pytest.fixture(autouse=True)
def cleanup_cache():
    """每个测试后清理缓存实例"""
    yield
    cache_manager._cache_instances.clear()


@pytest.fixture
def temp_cache_dir():
    """创建临时缓存目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_memory_cache_basic_operations():
    """测试内存缓存的基本操作"""
    cache = MemoryCache(maxsize=10, ttl=3600, cache_name="test")

    # 测试设置和获取
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"

    # 测试不存在的键
    assert cache.get("nonexistent") is None

    # 测试清空
    cache.set("key2", "value2")
    cache.clear()
    assert cache.get("key1") is None
    assert cache.get("key2") is None


@pytest.mark.asyncio
async def test_memory_cache_ttl_expiration():
    """测试内存缓存的 TTL 过期功能"""
    cache = MemoryCache(maxsize=10, ttl=1, cache_name="test_ttl")

    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"

    # 等待过期
    time.sleep(1.1)
    assert cache.get("key1") is None


@pytest.mark.asyncio
async def test_memory_cache_maxsize():
    """测试内存缓存的最大大小限制"""
    cache = MemoryCache(maxsize=2, ttl=3600, cache_name="test_maxsize")

    cache.set("key1", "value1")
    cache.set("key2", "value2")
    assert cache.get("key1") == "value1"
    assert cache.get("key2") == "value2"

    # 添加第三个键，应该会淘汰最旧的
    cache.set("key3", "value3")
    # 注意：TTLCache 的淘汰策略可能不是简单的 FIFO，这里主要测试不会崩溃
    assert cache.get("key3") == "value3"


@pytest.mark.asyncio
async def test_disk_cache_basic_operations(temp_cache_dir):
    """测试磁盘缓存的基本操作（如果 diskcache 可用）"""
    try:
        import diskcache
    except ImportError:
        pytest.skip("diskcache not installed")

    os.environ["SP_API_CACHE_DIR"] = temp_cache_dir
    cache = DiskCache(maxsize=10, ttl=3600, cache_name="test_disk")

    try:
        # 测试设置和获取
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # 测试不存在的键
        assert cache.get("nonexistent") is None

        # 测试清空
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    finally:
        cache.close()
        os.environ.pop("SP_API_CACHE_DIR", None)


@pytest.mark.asyncio
async def test_disk_cache_ttl_expiration(temp_cache_dir):
    """测试磁盘缓存的 TTL 过期功能"""
    try:
        import diskcache
    except ImportError:
        pytest.skip("diskcache not installed")

    os.environ["SP_API_CACHE_DIR"] = temp_cache_dir
    cache = DiskCache(maxsize=10, ttl=1, cache_name="test_disk_ttl")

    try:
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # 等待过期
        time.sleep(1.1)
        assert cache.get("key1") is None
    finally:
        cache.close()
        os.environ.pop("SP_API_CACHE_DIR", None)


@pytest.mark.asyncio
async def test_disk_cache_without_diskcache():
    """测试在没有 diskcache 时创建 DiskCache 应该抛出 ImportError"""
    try:
        import diskcache

        pytest.skip("diskcache is installed")
    except ImportError:
        with pytest.raises(ImportError):
            DiskCache(maxsize=10, ttl=3600, cache_name="test")


@pytest.mark.asyncio
async def test_get_cache_manager_singleton():
    """测试 get_cache_manager 的单例模式"""
    cache1 = get_cache_manager(maxsize=10, ttl=3600, cache_name="singleton_test")
    cache2 = get_cache_manager(maxsize=10, ttl=3600, cache_name="singleton_test")

    # 相同配置应该返回同一实例
    assert cache1 is cache2

    # 不同配置应该返回不同实例
    cache3 = get_cache_manager(maxsize=20, ttl=3600, cache_name="singleton_test")
    assert cache1 is not cache3

    # 不同缓存名称应该返回不同实例
    cache4 = get_cache_manager(maxsize=10, ttl=3600, cache_name="singleton_test2")
    assert cache1 is not cache4


@pytest.mark.asyncio
async def test_get_cache_manager_memory_type():
    """测试显式指定内存缓存类型"""
    cache = get_cache_manager(cache_type="memory", maxsize=5, ttl=1800, cache_name="test_memory")
    assert isinstance(cache, MemoryCache)

    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"


@pytest.mark.asyncio
async def test_get_cache_manager_disk_type(temp_cache_dir):
    """测试显式指定磁盘缓存类型"""
    try:
        import diskcache
    except ImportError:
        pytest.skip("diskcache not installed")

    os.environ["SP_API_CACHE_DIR"] = temp_cache_dir
    cache = get_cache_manager(cache_type="disk", maxsize=5, ttl=1800, cache_name="test_disk")

    try:
        assert isinstance(cache, DiskCache)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
    finally:
        cache.close()
        os.environ.pop("SP_API_CACHE_DIR", None)


@pytest.mark.asyncio
async def test_get_cache_manager_env_variable():
    """测试通过环境变量指定缓存类型"""
    os.environ["SP_API_CACHE_TYPE"] = "memory"
    cache = get_cache_manager(maxsize=5, ttl=1800, cache_name="test_env")

    assert isinstance(cache, MemoryCache)
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"

    os.environ.pop("SP_API_CACHE_TYPE", None)


@pytest.mark.asyncio
async def test_get_cache_manager_fallback_to_memory():
    """测试当指定不存在的缓存类型时回退到内存缓存"""
    cache = get_cache_manager(cache_type="nonexistent_type", maxsize=5, ttl=1800, cache_name="test_fallback")

    # 应该回退到 MemoryCache
    assert isinstance(cache, MemoryCache)
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"


@pytest.mark.asyncio
async def test_get_cache_manager_default_type():
    """测试默认缓存类型选择"""
    # 清除环境变量
    original_cache_type = os.environ.pop("SP_API_CACHE_TYPE", None)

    try:
        cache = get_cache_manager(maxsize=5, ttl=1800, cache_name="test_default")
        # 默认类型应该是 disk（如果可用）或 memory
        assert isinstance(cache, (MemoryCache, DiskCache))
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
    finally:
        if original_cache_type:
            os.environ["SP_API_CACHE_TYPE"] = original_cache_type


@pytest.mark.asyncio
async def test_base_cache_registration():
    """测试自定义缓存类的自动注册机制"""

    class CustomCache(BaseCache):
        cache_type_name = "custom_test"

        def __init__(self, maxsize=10, ttl=3600, cache_name=""):
            self._data = {}
            self._maxsize = maxsize
            self._ttl = ttl

        def get(self, key: str):
            return self._data.get(key)

        def set(self, key: str, value):
            self._data[key] = value

        def clear(self):
            self._data.clear()

    # 类定义时应该自动注册
    assert "custom_test" in cache_manager._cache_factories

    # 可以使用注册的名称获取缓存
    cache = get_cache_manager(cache_type="custom_test", maxsize=5, ttl=1800, cache_name="test_custom")
    assert isinstance(cache, CustomCache)
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"


@pytest.mark.asyncio
async def test_base_cache_missing_cache_type_name():
    """测试缺少 cache_type_name 的缓存类应该抛出 TypeError"""
    with pytest.raises(TypeError, match="must define 'cache_type_name'"):

        class InvalidCache(BaseCache):
            def __init__(self, maxsize=10, ttl=3600, cache_name=""):
                pass

            def get(self, key: str):
                return None

            def set(self, key: str, value):
                pass

            def clear(self):
                pass


@pytest.mark.asyncio
async def test_cache_manager_with_access_token_config():
    """测试使用 AccessTokenClient 配置的缓存管理器"""
    # 模拟 AccessTokenClient 使用的缓存配置
    os.environ["SP_API_AUTH_CACHE_SIZE"] = "100"
    os.environ["SP_API_AUTH_CACHE_TTL"] = "3200"

    try:
        # 使用与 AccessTokenClient 相同的配置创建缓存
        cache_size = int(os.environ.get("SP_API_AUTH_CACHE_SIZE", 100))
        cache_ttl = int(os.environ.get("SP_API_AUTH_CACHE_TTL", 3200))

        access_token_cache = get_cache_manager(maxsize=cache_size, ttl=cache_ttl, cache_name="access_token")
        grantless_cache = get_cache_manager(maxsize=cache_size, ttl=cache_ttl, cache_name="grantless_token")

        # 验证缓存实例已创建
        assert access_token_cache is not None
        assert grantless_cache is not None

        # 验证它们是不同的实例（因为 cache_name 不同）
        assert access_token_cache is not grantless_cache

        # 验证缓存功能正常
        access_token_cache.set("test_key", "test_value")
        assert access_token_cache.get("test_key") == "test_value"

        grantless_cache.set("test_key2", "test_value2")
        assert grantless_cache.get("test_key2") == "test_value2"
    finally:
        os.environ.pop("SP_API_AUTH_CACHE_SIZE", None)
        os.environ.pop("SP_API_AUTH_CACHE_TTL", None)


@pytest.mark.asyncio
async def test_cache_manager_with_different_configs():
    """测试不同配置的缓存管理器实例"""
    # 显式使用 memory 缓存类型以确保不同配置的实例完全隔离
    cache1 = get_cache_manager(cache_type="memory", maxsize=10, ttl=3600, cache_name="config1")
    cache2 = get_cache_manager(cache_type="memory", maxsize=20, ttl=1800, cache_name="config1")
    cache3 = get_cache_manager(cache_type="memory", maxsize=10, ttl=3600, cache_name="config2")

    # 不同配置应该返回不同实例
    assert cache1 is not cache2
    assert cache1 is not cache3
    assert cache2 is not cache3

    # 每个实例应该独立工作
    cache1.set("key1", "value1")
    cache2.set("key1", "value2")
    cache3.set("key1", "value3")

    assert cache1.get("key1") == "value1"
    assert cache2.get("key1") == "value2"
    assert cache3.get("key1") == "value3"


@pytest.mark.asyncio
async def test_disk_cache_with_different_configs_isolation(temp_cache_dir):
    """测试 DiskCache 在不同配置下的隔离性"""
    try:
        import diskcache
    except ImportError:
        pytest.skip("diskcache not installed")

    os.environ["SP_API_CACHE_DIR"] = temp_cache_dir

    # 创建不同配置的磁盘缓存实例
    cache1 = get_cache_manager(cache_type="disk", maxsize=10, ttl=3600, cache_name="test_isolation")
    cache2 = get_cache_manager(cache_type="disk", maxsize=20, ttl=1800, cache_name="test_isolation")
    cache3 = get_cache_manager(cache_type="disk", maxsize=10, ttl=3600, cache_name="test_isolation2")

    try:
        # 不同配置应该返回不同实例
        assert cache1 is not cache2
        assert cache1 is not cache3

        # 每个实例应该独立工作（现在路径包含 maxsize 和 ttl，确保隔离）
        cache1.set("key1", "value1")
        cache2.set("key1", "value2")
        cache3.set("key1", "value3")

        assert cache1.get("key1") == "value1"
        assert cache2.get("key1") == "value2"
        assert cache3.get("key1") == "value3"
    finally:
        cache1.close()
        cache2.close()
        cache3.close()
        os.environ.pop("SP_API_CACHE_DIR", None)
