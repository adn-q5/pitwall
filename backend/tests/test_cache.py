from app.data.cache import Cache


def test_cache_roundtrip(tmp_path):
    c = Cache(tmp_path / "test.db")
    assert c.get("k") is None            # miss
    c.set("k", [{"a": 1}])
    assert c.get("k") == [{"a": 1}]      # hit