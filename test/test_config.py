
import pytest
import threading
from src.config import Config


class TestConfig:
    @pytest.fixture(autouse=True)
    def reset_config_singleton(self, monkeypatch):
        monkeypatch.setattr("src.config.load_dotenv", lambda: None)
        monkeypatch.setattr(Config, "_instance", None)

    def test_config_is_singleton(self, monkeypatch):
        monkeypatch.setenv("KEY_A", "key_a_contents")
        monkeypatch.setenv("KEY_B", "key_b_contents")

        config1 = Config()
        config2 = Config()
        assert config1 is config2

    def test_config_thread_safety(self):
        instances = []

        def get_instance():
            instances.append(Config())

        threads = [threading.Thread(target=get_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(instance is instances[0] for instance in instances)

    def test_valid_env(self, monkeypatch):
        monkeypatch.setenv("SOL_WALLET_PVT_KEY", "test_key")

        config = Config()
        assert config.solana_wallet_private_key == "test_key"

    def test_missing_env(self, monkeypatch):
        monkeypatch.delenv("SOL_WALLET_PVT_KEY", raising=False)

        with pytest.raises(OSError):
            config = Config()
            config.solana_wallet_private_key
