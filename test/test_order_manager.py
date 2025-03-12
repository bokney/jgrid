
import pytest
import sqlite3
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timezone
from src.order_store import OrderStore
from src.orders import ClosedOrder, Trade


@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_closed_orders.db"
    yield str(db_file)


@pytest.fixture
def order_store(test_db):
    return OrderStore(db_path=Path(test_db))


class TestOrderStore:
    @pytest.mark.skip
    def test_get_order_retrieves_stored_order(self):
        pass

    @pytest.mark.skip
    def test_get_order_returns_correct_trades(self):
        pass

    @pytest.mark.skip
    def test_get_order_returns_none_for_missing_order(self):
        pass

    @pytest.mark.skip
    def test_store_closed_order_saves_to_db(self):
        pass

    @pytest.mark.skip
    def test_store_closed_order_with_no_trades_succeeds(self):
        pass

    @pytest.mark.skip
    def test_store_closed_order_duplicate_closed_order_fails(self):
        pass

    @pytest.mark.skip
    def test_store_closed_order_trade_missing_closed_order_fails(self):
        pass

    @pytest.mark.skip
    def test_store_closed_order_datetime_fields_converted_to_iso(self):
        pass

    @pytest.mark.skip
    def test_store_closed_order_atomicity_rolls_back_on_trade_failure(self):
        pass

    @pytest.mark.skip
    def test_order_exists_returns_true_for_stored_order(self):
        pass

    @pytest.mark.skip
    def test_order_exists_returns_false_for_missing_order(self):
        pass

    @pytest.mark.skip
    def test_multiple_connections_can_access_db(self):
        pass
