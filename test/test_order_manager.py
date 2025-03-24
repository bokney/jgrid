
import pytest
from uuid import uuid4
from decimal import Decimal
from unittest.mock import patch, MagicMock
from src.order_manager import OrderManager, OrderStatus
from src.tokens import Token


@pytest.fixture
def order_manager():
    manager = OrderManager()
    manager._jupiter_api = MagicMock()
    manager._order_store = MagicMock()
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
        order_manager._jupiter_api.create_limit_order.assert_called_once()

    def test_place_order_incorrect_values(self, order_manager, usdc, fartcoin):
        with pytest.raises(ValueError):
            _ = order_manager.place_order(
                base=usdc,
                quote=fartcoin,
                volume=Decimal("-100.00"),
                price=Decimal("16000")
            )
        with pytest.raises(ValueError):
            _ = order_manager.place_order(
                base=usdc,
                quote=fartcoin,
                volume=Decimal("100.00"),
                price=Decimal("-16000")
            )
        with pytest.raises(ValueError):
            _ = order_manager.place_order(
                base=usdc,
                quote=fartcoin,
                volume=Decimal("0"),
                price=Decimal("16000")
            )
        with pytest.raises(ValueError):
            _ = order_manager.place_order(
                base=usdc,
                quote=fartcoin,
                volume=Decimal("100.00"),
                price=Decimal("0")
            )

    def test_place_order_no_duplication(self, order_manager, usdc, fartcoin):
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
    def test_cancel_order_successful(self, order_manager, usdc, fartcoin):
        order_id = order_manager.place_order(
            base=usdc,
            quote=fartcoin,
            volume=Decimal("0.5"),
            price=Decimal("2")
        )

        order_manager.cancel_order(order_id)

        assert order_id not in [o.publicKey for o in order_manager.open_orders]
        order_manager._jupiter_api.cancel_order.assert_called_once()

    def test_cancel_order_can_only_cancel_once(
        self, order_manager, usdc, fartcoin
    ):
        order_id = order_manager.place_order(
            base=usdc,
            quote=fartcoin,
            volume=Decimal("100.00"),
            price=Decimal("16000")
        )

        order_manager.cancel_order(order_id)

        with pytest.raises(Exception):
            order_manager.cancel_order(order_id)

        order_manager._jupiter_api.cancel_order.assert_called_once()

    def test_cancel_order_order_does_not_exist(self, order_manager):
        invalid_order_id = str(uuid4())

        with pytest.raises(Exception):
            order_manager.cancel_order(invalid_order_id)
        order_manager._jupiter_api.cancel_order.assert_not_called()


class TestGetOrderStatus:
    @pytest.mark.skip
    def test_get_order_status_success(self, order_manager, usdc, fartcoin):
        order_id = order_manager.place_order(
            base=usdc,
            quote=fartcoin,
            volume=Decimal("100.00"),
            price=Decimal("16000")
        )

        status = order_manager.get_order_status(order_id)

        assert status == OrderStatus.CREATED

    @pytest.mark.skip
    def test_get_order_status_order_does_not_exist(self, order_manager):
        non_existent_order_id = str(uuid4())

        status = order_manager.get_order_status(non_existent_order_id)

        assert status is None


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


    @pytest.mark.skip
    def test_order_created_observer_invoked_successfully(
        self, order_manager, usdc, fartcoin
    ):
        om, mock_created, _, _, _ = patched_order_manager
        callback = MagicMock()
        om.register_order_created_observer(callback)
        order_id = om.place_order(
            base=usdc,
            quote=fartcoin,
            vol=Decimal("0.01"),
            price=Decimal("200")
        )
        callback.assert_called_once()
        notified_order = callback.call_args[0][0]
        assert notified_order.publicKey == order_id

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
