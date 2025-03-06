
import threading
from src.solana_rpc import SolanaRPC


class MockClient:
    def __init__(self, rpc_url):
        self._rpc_url = rpc_url


class TestSolanaRPC:
    def setup_method(self):
        SolanaRPC._client = None

    def test_get_client_returns_client(self, monkeypatch):
        monkeypatch.setattr("src.solana_rpc.Client", MockClient)
        client = SolanaRPC.get_client()
        assert isinstance(client, MockClient)
        assert client._rpc_url == SolanaRPC._rpc_url

    def test_client_is_singleton(self, monkeypatch):
        monkeypatch.setattr("src.solana_rpc.Client", MockClient)
        client_1 = SolanaRPC.get_client()
        client_2 = SolanaRPC.get_client()
        assert client_1 is client_2

    def test_client_thread_safety(self, monkeypatch):
        monkeypatch.setattr("src.solana_rpc.Client", MockClient)

        instances = []

        def get_instance():
            instances.append(SolanaRPC.get_client())

        threads = [threading.Thread(target=get_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(instance is instances[0] for instance in instances)
