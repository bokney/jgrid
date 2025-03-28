
import pytest
from uuid import uuid4
from decimal import Decimal
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.order_manager import OrderManager, OrderStatus
from src.order_models import OpenOrder, ClosedOrder
from src.order_store import OrderStore
from src.tokens import Token
from mock_api_responses import (
    MOCK_GET_ORDER_HISTORY_PAGE_1,
    MOCK_GET_ORDER_HISTORY_PAGE_2
)


@pytest.fixture
def order_manager(tmp_path):
    db_path = tmp_path / "test_orders.db"
    order_store = OrderStore(db_path)

    om = OrderManager()
    om._jupiter_api = MagicMock()
    om._order_store = order_store

    yield om


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
    def test_get_order_status_open(self, order_manager, usdc, fartcoin):
        order_id = order_manager.place_order(
            base=usdc,
            quote=fartcoin,
            volume=Decimal("100.00"),
            price=Decimal("16000")
        )
        status = order_manager.get_order_status(order_id)
        assert status == OrderStatus.OPEN

    def test_get_order_status_partially_filled(
        self, order_manager, usdc, fartcoin
    ):
        order_id = order_manager.place_order(
            base=usdc,
            quote=fartcoin,
            volume=Decimal("100.00"),
            price=Decimal("16000")
        )
        order = next(
            o for o in order_manager.open_orders if o.publicKey == order_id
        )
        order.makingAmount = Decimal("60.00")
        status = order_manager.get_order_status(order_id)
        assert status == OrderStatus.PARTIALLY_FILLED

    def test_get_order_status_closed(self, order_manager, usdc, fartcoin):
        closed_order = ClosedOrder(
            userPubkey="user_pubkey",
            orderKey="order_key",
            inputMint=usdc.address,
            outputMint=fartcoin.address,
            makingAmount=Decimal("1.0"),
            takingAmount=Decimal("2.0"),
            remainingMakingAmount=Decimal("0.0"),
            remainingTakingAmount=Decimal("0.0"),
            expiredAt=None,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            status="closed",
            openTx="OPENTX123",
            closeTx="CLOSETX456",
            programVersion="v1.0",
            trades=[],
        )

        with patch.object(
            order_manager._order_store,
            "load_closed_order",
            return_value=closed_order
        ):
            status = order_manager.get_order_status("order_key")

        assert status == OrderStatus.CLOSED

    def test_get_order_status_cancelled(self, order_manager, usdc, fartcoin):
        closed_order = ClosedOrder(
            userPubkey="user_pubkey",
            orderKey="order_key",
            inputMint=usdc.address,
            outputMint=fartcoin.address,
            makingAmount=Decimal("1.0"),
            takingAmount=Decimal("2.0"),
            remainingMakingAmount=Decimal("0.5"),
            remainingTakingAmount=Decimal("1.0"),
            expiredAt=None,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            status="cancelled",
            openTx="OPENTX123",
            closeTx="CLOSETX456",
            programVersion="v1.0",
            trades=[],
        )

        with patch.object(
            order_manager._order_store,
            "load_closed_order",
            return_value=closed_order
        ):
            status = order_manager.get_order_status("order_key")

        assert status == OrderStatus.CANCELLED

    def test_get_order_status_order_does_not_exist(self, order_manager):
        non_existent_order_id = str(uuid4())
        status = order_manager.get_order_status(non_existent_order_id)
        assert status is None


class TestUpdateOrders:
    def test_update_orders_triggers_order_closed_observer(self, order_manager):
        preloaded_order = {
            "account": {
                "borrowMakingAmount": "0",
                "createdAt":
                    datetime.fromisoformat("2024-03-06 11:58:19+00:00"),
                "expiredAt":
                    datetime.fromisoformat("2024-03-09 11:58:13+00:00"),
                "makingAmount": Decimal("1665"),
                "oriMakingAmount": Decimal("1665"),
                "takingAmount": Decimal("67.4325"),
                "oriTakingAmount": Decimal("67.4325"),
                "uniqueId": 0,
                "updatedAt":
                    datetime.fromisoformat("2024-03-06 11:59:16+00:00"),
                "feeAccount": "",
                "inputMint": "6ogzHhzdrQr9Pgv6hZ2MNze7UrzBMAFyBBWUYp1Fhitx",
                "inputMintReserve": "",
                "inputTokenProgram": "",
                "maker": "B2QXpgPZA1FAxcNwfe2SdBeTkNeMqhVPurpoUxQ9P1Qt",
                "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGKwyTDt1v",
                "outputTokenProgram": "",
                "feeBps": 0,
                "bump": 0,
            },
            "publicKey": "2Y2g4DimTfAaSc95B5GGYAVz8nhUB2X7p21uUTY226Jd"
        }

        account_data = preloaded_order["account"]
        public_key = preloaded_order["publicKey"]

        order_data = {**account_data, "publicKey": public_key}
        open_order = OpenOrder(**order_data)

        order_manager.open_orders = [open_order]

        order_manager._jupiter_api.get_open_orders.return_value = []

        order_manager._jupiter_api.get_order_history.return_value = (
            MOCK_GET_ORDER_HISTORY_PAGE_2
        )

        with patch.object(
            order_manager, "_notify_order_closed"
        ) as mock_notify:
            order_manager.update_orders()
            expected_call_count = len(MOCK_GET_ORDER_HISTORY_PAGE_2["orders"])
            assert mock_notify.call_count == expected_call_count

            notified_keys = [call[0][0] for call in mock_notify.call_args_list]
            expected_keys = [
                order["orderKey"]
                for order in MOCK_GET_ORDER_HISTORY_PAGE_2["orders"]
            ]
            assert set(notified_keys) == set(expected_keys)

    def test_update_orders_paginates_order_history(self, order_manager):
        order_manager._jupiter_api.get_open_orders.return_value = []
        order_manager._jupiter_api.get_order_history.side_effect = [
            MOCK_GET_ORDER_HISTORY_PAGE_1,
            MOCK_GET_ORDER_HISTORY_PAGE_2
        ]

        order_manager.update_orders()

        assert order_manager._jupiter_api.get_order_history.call_count == 2

    def test_update_orders_ignores_orders_already_closed_or_cancelled(
        self, order_manager
    ):
        preloaded_order = {
            "account": {
                "borrowMakingAmount": "0",
                "createdAt":
                    datetime.fromisoformat("2024-03-06 11:58:19+00:00"),
                "expiredAt":
                    datetime.fromisoformat("2024-03-09 11:58:13+00:00"),
                "makingAmount": Decimal("1665"),
                "oriMakingAmount": Decimal("1665"),
                "takingAmount": Decimal("67.4325"),
                "oriTakingAmount": Decimal("67.4325"),
                "uniqueId": 0,
                "updatedAt":
                    datetime.fromisoformat("2024-03-06 11:59:16+00:00"),
                "feeAccount": "",
                "inputMint": "6ogzHhzdrQr9Pgv6hZ2MNze7UrzBMAFyBBWUYp1Fhitx",
                "inputMintReserve": "",
                "inputTokenProgram": "",
                "maker": "B2QXpgPZA1FAxcNwfe2SdBeTkNeMqhVPurpoUxQ9P1Qt",
                "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGKwyTDt1v",
                "outputTokenProgram": "",
                "feeBps": 0,
                "bump": 0,
            },
            "publicKey": "2Y2g4DimTfAaSc95B5GGYAVz8nhUB2X7p21uUTY226Jd"
        }

        account_data = preloaded_order["account"]
        public_key = preloaded_order["publicKey"]

        order_data = {**account_data, "publicKey": public_key}
        open_order = OpenOrder(**order_data)

        order_manager.open_orders = [open_order]

        order_manager._jupiter_api.get_open_orders.return_value = [
            preloaded_order
        ]

        closed_order_data = {
            "orderKey": "ORDER_KEY_123",
            "userPubkey": "B2QXpgPZA1FAxcNwfe2SdBeTkNeMqhVPurpoUxQ9P1Qt",
            "inputMint": "6ogzHhzdrQr9Pgv6h2MNze7UrzBMAFyBBWUYp1Fhitx",
            "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGKwyTDt1v",
            "makingAmount": "1665",
            "takingAmount": "67.4325",
            "remainingMakingAmount": "0",
            "remainingTakingAmount": "0",
            "expiredAt": "2024-03-09 11:58:13+00:00",
            "createdAt": "2024-03-06 11:58:19+00:00",
            "updatedAt": "2024-03-06 11:59:16+00:00",
            "status": "cancelled",
            "openTx": "SOME_OPENTX",
            "closeTx": "SOME_CLOSETX",
            "programVersion": "v1.0",
            "trades": []
        }
        order_manager._jupiter_api.get_order_history.return_value = {
            "hasMoreData": "false",
            "orders": [closed_order_data]
        }

        order_manager._order_store.order_exists = MagicMock(return_value=True)

        with patch.object(
            order_manager, "_notify_order_closed"
        ) as mock_notify:
            order_manager.update_orders()
            mock_notify.assert_not_called()

        remaining_open_keys = {o.publicKey for o in order_manager.open_orders}
        assert (
            "2Y2g4DimTfAaSc95B5GGYAVz8nhUB2X7p21uUTY226Jd"
            in remaining_open_keys
        )


class TestOrderClosedObserver:
    def test_order_closed_observer_invoked_successfully(
        self, order_manager, usdc, fartcoin
    ):
        notifications = []

        def observer():
            notifications.append("order123")

        order_manager._order_closed_observer.register("order123", observer)

        order_manager._notify_order_closed("order123")
        assert "order123" in notifications

    def test_order_closed_observer_replaces_previous(
        self, order_manager, usdc, fartcoin
    ):
        notifications1 = []
        notifications2 = []

        def observer1():
            notifications1.append("order456")

        def observer2():
            notifications2.append("order456")

        order_manager._order_closed_observer.register("order456", observer1)
        order_manager._order_closed_observer.register("order456", observer2)

        order_manager._notify_order_closed("order456")

        assert "order456" not in notifications1
        assert "order456" in notifications2

    def test_order_closed_observer_no_observers(
        self, order_manager, usdc, fartcoin
    ):
        try:
            order_manager._notify_order_closed("order789")
        except Exception as e:
            pytest.fail(f"_notify_order_closed raised an exception: {e}")
