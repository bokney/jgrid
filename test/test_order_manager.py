
import pytest
from src.order_manager import OrderManager


@pytest.fixture
def order_manager():
    return OrderManager()


@pytest.fixture
def dummy_order_store(monkeypatch):
    class DummyOrderStore:
        def store_closed_order(self, order):
            pass
        def load_closed_order(self, order_key):
            return None
    monkeypatch.setattr(OrderManager, "_order_store", DummyOrderStore())
    return DummyOrderStore()


@pytest.fixture
def dummy_jupiter_api(monkeypatch):
    class DummyJupiterAPI:
        def place_order(self, order):
            return True
        def cancel_order(self, order):
            return True
    monkeypatch.setattr(OrderManager, "_jupiter_api", DummyJupiterAPI())
    return DummyJupiterAPI()
