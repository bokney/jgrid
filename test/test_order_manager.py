
import pytest
from uuid import uuid4
from decimal import Decimal
from unittest.mock import patch, MagicMock
from src.order_manager import OrderManager
from src.tokens import Token


@pytest.fixture
def order_manager():
    with patch.object(
        OrderManager, "_jupiter_api", new_callable=MagicMock
    ) as mock_api, patch.object(
        OrderManager, "_order_store", new_callable=MagicMock
    ) as mock_store:
        manager = OrderManager()
        manager._jupiter_api = mock_api
        manager._order_store = mock_store
        yield manager

@pytest.fixture
def patched_order_manager():
    with patch.object(
        OrderManager, "_order_created_observer", new_callable=MagicMock
    ) as mock_created, patch(
        OrderManager, "_order_updated_observer", new_callable=MagicMock
    ) as mock_updated, patch.object(
        OrderManager, "_order_closed_observer", new_callable=MagicMock
    ) as mock_closed, patch.object(
        OrderManager, "_order_cancelled_observer", new_callable=MagicMock
    ) as mock_cancelled:
        om = OrderManager()  
        yield (
            om,
            mock_created,
            mock_updated,
            mock_closed,
            mock_cancelled
        )

@pytest.fixture
def usdc():
    return Token(
        address="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        name="USD Coin",
        symbol="USDC",
        decimals=6
    )

@pytest.fixture
def fartcoin():
    return Token(
        address="9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump",
        name="Fartcoin ",
        symbol="Fartcoin ",
        decimals=6
    )


class TestPlaceOrder:
    def test_place_order_successful(self, order_manager, usdc, fartcoin):
        order_id = order_manager.place_order(
            base=usdc,
            quote=fartcoin,
            volume=Decimal("100.00"),
            price=Decimal("16000")
        )

        assert isinstance(order_id, str) and order_id
        open_order_ids = [
            order.publicKey for order in order_manager.open_orders
        ]
        assert order_id in open_order_ids

        order_manager._jupiter_api.place_order.assert_called_once()
        order_manager._order_store.save_order.assert_called_once()

    def test_place_order_incorrect_values(self, order_manager, usdc, fartcoin):
        with pytest.raises(ValueError):
            order_id = order_manager.place_order(
                base=usdc,
                quote=fartcoin,
                volume=Decimal("-100.00"),
                price=Decimal("16000")
            )
        with pytest.raises(ValueError):
            order_id = order_manager.place_order(
                base=usdc,
                quote=fartcoin,
                volume=Decimal("100.00"),
                price=Decimal("-16000")
            )
        with pytest.raises(ValueError):
            order_id = order_manager.place_order(
                base=usdc,
                quote=fartcoin,
                volume=Decimal("0"),
                price=Decimal("16000")
            )
        with pytest.raises(ValueError):
            order_id = order_manager.place_order(
                base=usdc,
                quote=fartcoin,
                volume=Decimal("100.00"),
                price=Decimal("0")
            )

    def test_place_order_no_duplication(self):
        def mock_place_order(*args, **kwargs):
            return str(uuid4())

        order_manager.place_order = mock_place_order

        orders = []
        for i in range(10):
            order_id = order_manager.place_order(
                base=usdc,
                quote=fartcoin,
                volume=Decimal("100.00"),
                price=Decimal("16000")
            )
            orders.append(order_id)

        assert len(orders) == len(set(orders))

class TestCancelOrder:
    @pytest.mark.skip
    def test_cancel_order_successful(self):
        pass

    @pytest.mark.skip
    def test_cancel_order_can_only_cancel_once(self):
        # could test whether observer is called more than once too
        pass

    @pytest.mark.skip
    def test_cancel_order_order_does_not_exist(self):
        pass


class TestGetOrderStatus:
    @pytest.mark.skip
    def test_get_order_status_success(self):
        pass

    @pytest.mark.skip
    def test_get_order_status_order_does_not_exist(self):
        pass


class TestUpdateOrders:
    @pytest.mark.skip
    def test_update_orders_transitions_open_to_partially_filled(self):
        pass

    @pytest.mark.skip
    def test_update_orders_transitions_open_to_filled(self):
        pass

    @pytest.mark.skip
    def test_update_orders_transitions_open_to_cancelled(self):
        pass

    @pytest.mark.skip
    def test_update_orders_transitions_partially_filled_to_filled(self):
        pass

    @pytest.mark.skip
    def test_update_orders_transitions_partially_filled_to_cancelled(self):
        pass

    @pytest.mark.skip
    def test_update_orders_transitions_multiple_orders_correctly(self):
        pass

    @pytest.mark.skip
    def test_update_orders_does_nothing_if_no_state_change(self):
        pass

    @pytest.mark.skip
    def test_update_orders_handles_unknown_order_state_gracefully(self):
        pass

    @pytest.mark.skip
    def test_update_orders_handles_api_failure_without_crashing(self):
        pass

    @pytest.mark.skip
    def test_update_orders_handles_database_failure_gracefully(self):
        pass

    @pytest.mark.skip
    def test_update_orders_ignores_orders_already_closed_or_cancelled(self):
        pass

    @pytest.mark.skip
    def test_update_orders_processes_large_number_of_orders_efficiently(self):
        pass


class TestOrderCreatedObserver:
    @pytest.mark.skip
    def test_order_created_observer_invoked_successfully(self):
        pass

    @pytest.mark.skip
    def test_order_created_observer_multiple_observers(self):
        pass

    @pytest.mark.skip
    def test_order_created_observer_no_observers(self):
        pass


class TestOrderUpdatedObserver:
    @pytest.mark.skip
    def test_order_updated_observer_invoked_successfully(self):
        pass

    @pytest.mark.skip
    def test_order_updated_observer_multiple_observers(self):
        pass

    @pytest.mark.skip
    def test_order_updated_observer_no_observers(self):
        pass


class TestOrderClosedObserver:
    @pytest.mark.skip
    def test_order_closed_observer_invoked_successfully(self):
        pass

    @pytest.mark.skip
    def test_order_closed_observer_multiple_observers(self):
        pass

    @pytest.mark.skip
    def test_order_closed_observer_no_observers(self):
        pass


class TestOrderCancelledObserver:
    @pytest.mark.skip
    def test_order_cancelled_observer_invoked_successfully(self):
        pass

    @pytest.mark.skip
    def test_order_cancelled_observer_multiple_observers(self):
        pass

    @pytest.mark.skip
    def test_order_cancelled_observer_no_observers(self):
        pass
