
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
    yield Path(db_file)


@pytest.fixture
def order_store(test_db):
    return OrderStore(db_path=Path(test_db))


class TestOrderStore:
    def test_get_order_retrieves_stored_order(self, order_store):
        trade1 = Trade(
            orderKey="order_key",
            keeper="keeper",
            inputMint="input_mint",
            outputMint="output_mint",
            inputAmount=Decimal("10.0"),
            outputAmount=Decimal("9.5"),
            feeMint="fee_mint",
            feeAmount=Decimal("0.5"),
            txId="TX123",
            confirmedAt=datetime.now(),
            action="sell",
            productMeta="Metadata for trade 1"
        )
        trade2 = Trade(
            orderKey="order_key",
            keeper="keeper",
            inputMint="input_mint",
            outputMint="output_mint",
            inputAmount=Decimal("5.0"),
            outputAmount=Decimal("4.8"),
            feeMint="fee_mint",
            feeAmount=Decimal("0.2"),
            txId="TX456",
            confirmedAt=datetime.now(),
            action="sell",
            productMeta="Metadata for trade 2"
        )

        total_input = trade1.inputAmount + trade2.inputAmount 
        total_output = trade1.outputAmount + trade2.outputAmount

        closed_order = ClosedOrder(
            userPubkey="user_pubkey",
            orderKey="order_key",
            inputMint="input_mint",
            outputMint="output_mint",
            makingAmount=total_input,
            takingAmount=total_output,
            remainingMakingAmount=Decimal("0.0"),
            remainingTakingAmount=Decimal("0.0"),
            expiredAt=None,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            status="closed",
            openTx="OPENTX123",
            closeTx="CLOSETX456",
            programVersion="v1.0",
            trades=[trade1, trade2]
        )

        order_store.store_closed_order(closed_order)
        retrieved_order = order_store.get_order("order_key")

        assert retrieved_order is not None
        assert isinstance(retrieved_order, ClosedOrder)

        assert retrieved_order.userPubkey == "user_pubkey"
        assert retrieved_order.orderKey == "order_key"
        assert retrieved_order.makingAmount == total_input
        assert retrieved_order.takingAmount == total_output
        assert retrieved_order.status == "closed"
        assert retrieved_order.openTx == "OPENTX123"
        assert retrieved_order.closeTx == "CLOSETX456"

        assert len(retrieved_order.trades) == 2
        assert retrieved_order.trades[0].txId == "TX123"
        assert retrieved_order.trades[1].txId == "TX456"
        assert retrieved_order.trades[0].inputAmount == Decimal("10.0")
        assert retrieved_order.trades[1].inputAmount == Decimal("5.0")
        assert retrieved_order.trades[0].outputAmount == Decimal("9.5")
        assert retrieved_order.trades[1].outputAmount == Decimal("4.8")

    def test_get_order_returns_correct_trades(self, order_store):
        trade1 = Trade(
            orderKey="order_key",
            keeper="keeperA",
            inputMint="input_mint",
            outputMint="output_mint",
            inputAmount=Decimal("3.0"),
            outputAmount=Decimal("2.9"),
            feeMint="fee_mint",
            feeAmount=Decimal("0.1"),
            txId="TX001",
            confirmedAt=datetime.now(),
            action="sell",
            productMeta="Trade A"
        )
        trade2 = Trade(
            orderKey="order_key",
            keeper="keeperB",
            inputMint="input_mint",
            outputMint="output_mint",
            inputAmount=Decimal("4.0"),
            outputAmount=Decimal("3.8"),
            feeMint="fee_mint",
            feeAmount=Decimal("0.2"),
            txId="TX002",
            confirmedAt=datetime.now(),
            action="sell",
            productMeta="Trade B"
        )
        trade3 = Trade(
            orderKey="order_key",
            keeper="keeperC",
            inputMint="input_mint",
            outputMint="output_mint",
            inputAmount=Decimal("5.0"),
            outputAmount=Decimal("4.7"),
            feeMint="fee_mint",
            feeAmount=Decimal("0.3"),
            txId="TX003",
            confirmedAt=datetime.now(),
            action="sell",
            productMeta="Trade C"
        )

        trades = [trade1, trade2, trade3]

        total_input = sum(t.inputAmount for t in trades)
        total_output = sum(t.outputAmount for t in trades)

        closed_order = ClosedOrder(
            userPubkey="user_pubkey",
            orderKey="order_key",
            inputMint="input_mint",
            outputMint="output_mint",
            makingAmount=total_input,
            takingAmount=total_output,
            remainingMakingAmount=Decimal("0.0"),
            remainingTakingAmount=Decimal("0.0"),
            expiredAt=None,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            status="closed",
            openTx="OPENTX123",
            closeTx="CLOSETX456",
            programVersion="v1.0",
            trades=trades
        )
        order_store.store_closed_order(closed_order)
        retrieved_order = order_store.get_order("order_key")

        assert len(retrieved_order.trades) == 3
        retrieved_txids = {trade.txId for trade in retrieved_order.trades}
        expected_txids = {"TX001", "TX002", "TX003"}
        assert retrieved_txids == expected_txids

    def test_get_order_returns_none_for_missing_order(self, order_store):
        missing_key = "nonexistent_order"
        retrieved_order = order_store.get_order(missing_key)
        assert retrieved_order is None

    def test_store_closed_order_saves_to_db(self, order_store, test_db):
        closed_order = ClosedOrder(
            userPubkey="user_pubkey",
            orderKey="order_key",
            inputMint="input_mint",
            outputMint="output_mint",
            makingAmount=Decimal("20.0"),
            takingAmount=Decimal("19.5"),
            remainingMakingAmount=Decimal("0.0"),
            remainingTakingAmount=Decimal("0.0"),
            expiredAt=None,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            status="closed",
            openTx="OPENTX123",
            closeTx="CLOSETX456",
            programVersion="v1.0",
            trades=[]
        )
        order_store.store_closed_order(closed_order)
        with sqlite3.connect(test_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM closed_orders WHERE orderKey = ?", ("order_key",)
            )
            row = cursor.fetchone()
            assert row is not None
            assert row["userPubkey"] == "user_pubkey"

    def test_store_closed_order_with_no_trades_succeeds(self, order_store):
        closed_order = ClosedOrder(
            userPubkey="user_pubkey",
            orderKey="order_key",
            inputMint="input_mint",
            outputMint="output_mint",
            makingAmount=Decimal("0.0"),
            takingAmount=Decimal("0.0"),
            remainingMakingAmount=Decimal("0.0"),
            remainingTakingAmount=Decimal("0.0"),
            expiredAt=None,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            status="closed",
            openTx="OPENTX123",
            closeTx="CLOSETX456",
            programVersion="v1.0",
            trades=[]
        )
        order_store.store_closed_order(closed_order)
        retrieved_order = order_store.get_order("order_key")
        assert retrieved_order is not None
        assert retrieved_order.trades == []

    def test_store_closed_order_duplicate_closed_order_fails(
        self, order_store
    ):
        closed_order = ClosedOrder(
            userPubkey="user_pubkey",
            orderKey="order_key",
            inputMint="input_mint",
            outputMint="output_mint",
            makingAmount=Decimal("15.0"),
            takingAmount=Decimal("14.5"),
            remainingMakingAmount=Decimal("0.0"),
            remainingTakingAmount=Decimal("0.0"),
            expiredAt=None,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            status="closed",
            openTx="OPENTX123",
            closeTx="CLOSETX456",
            programVersion="v1.0",
            trades=[]
        )
        order_store.store_closed_order(closed_order)
        with pytest.raises(sqlite3.IntegrityError):
            order_store.store_closed_order(closed_order)

    @pytest.mark.skip()
    def test_store_closed_order_trade_missing_closed_order_fails(
        self, order_store, test_db
    ):
        trade = Trade(
            orderKey="non_existent_order_key",
            keeper="keeper",
            inputMint="input_mint",
            outputMint="output_mint",
            inputAmount=Decimal("10.0"),
            outputAmount=Decimal("9.5"),
            feeMint="fee",
            feeAmount=Decimal("0.5"),
            txId="TX123",
            confirmedAt=datetime.now(),
            action="sell",
            productMeta="Meta"
        )

        closed_order = ClosedOrder(
            userPubkey="user_pubkey",
            orderKey="existing_order_key",
            inputMint="input_mint",
            outputMint="output_mint",
            makingAmount=Decimal("10.12345678"),
            takingAmount=Decimal("9.87654321"),
            remainingMakingAmount=Decimal("0.0"),
            remainingTakingAmount=Decimal("0.0"),
            expiredAt=None,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            status="closed",
            openTx="OPENTX123",
            closeTx="CLOSETX456",
            programVersion="v1.0",
            trades=[trade]
        )

        with pytest.raises(sqlite3.IntegrityError):
            order_store.store_closed_order(closed_order)

        with sqlite3.connect(test_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM trades WHERE orderKey = ?",
                ("non_existent_order_key",)
            )
            trade_row = cursor.fetchone()
            assert trade_row is None, "Trade should not be inserted for a non-existent orderKey."

    def test_store_closed_order_datetime_fields_converted_to_iso(
        self, order_store, test_db
    ):
        closed_order = ClosedOrder(
            userPubkey="user_pubkey",
            orderKey="order_key",
            inputMint="input_mint",
            outputMint="output_mint",
            makingAmount=Decimal("10.0"),
            takingAmount=Decimal("9.5"),
            remainingMakingAmount=Decimal("0.0"),
            remainingTakingAmount=Decimal("0.0"),
            expiredAt=None,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            status="closed",
            openTx="OPENTX123",
            closeTx="CLOSETX456",
            programVersion="v1.0",
            trades=[]
        )
        order_store.store_closed_order(closed_order)
        with sqlite3.connect(test_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                (
                    "SELECT createdAt, updatedAt "
                    "FROM closed_orders WHERE orderKey = ?"
                ),
                ("order_key",)
            )
            row = cursor.fetchone()
            assert isinstance(row["createdAt"], str)
            assert isinstance(row["updatedAt"], str)

            try:
                datetime.fromisoformat(row["createdAt"])
                datetime.fromisoformat(row["updatedAt"])
            except ValueError:
                pytest.fail("Datetime fields not in valid ISO 8601 format.")

    def test_store_closed_order_decimal_fields_stored_as_str(self, order_store, test_db):
        closed_order = ClosedOrder(
            userPubkey="user_pubkey",
            orderKey="order_key",
            inputMint="input_mint",
            outputMint="output_mint",
            makingAmount=Decimal("10.12345678"),
            takingAmount=Decimal("9.87654321"),
            remainingMakingAmount=Decimal("0.0"),
            remainingTakingAmount=Decimal("0.0"),
            expiredAt=None,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            status="closed",
            openTx="OPENTX123",
            closeTx="CLOSETX456",
            programVersion="v1.0",
            trades=[]
        )
        order_store.store_closed_order(closed_order)

        with sqlite3.connect(test_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT makingAmount, takingAmount FROM closed_orders WHERE orderKey = ?",
                ("order_key",)
            )
            row = cursor.fetchone()
            assert isinstance(row["makingAmount"], str)
            assert isinstance(row["takingAmount"], str)

            try:
                assert Decimal(row["makingAmount"]) == Decimal("10.12345678")
                assert Decimal(row["takingAmount"]) == Decimal("9.87654321")
            except (ValueError, ArithmeticError):
                pytest.fail("Decimal fields not stored as valid numeric strings.")

    def test_store_trade_decimal_fields_stored_as_str(self, order_store, test_db):
        trade = Trade(
            orderKey="order_key",
            keeper="keeper",
            inputMint="input_mint",
            outputMint="output_mint",
            inputAmount=Decimal("10.0"),
            outputAmount=Decimal("9.5"),
            feeMint="fee_mint",
            feeAmount=Decimal("0.5"),
            txId="TX123",
            confirmedAt=datetime.now(),
            action="sell",
            productMeta="Metadata for trade"
        )
        closed_order = ClosedOrder(
            userPubkey="user_pubkey",
            orderKey="order_key",
            inputMint="input_mint",
            outputMint="output_mint",
            makingAmount=Decimal("15.0"),
            takingAmount=Decimal("14.5"),
            remainingMakingAmount=Decimal("0.0"),
            remainingTakingAmount=Decimal("0.0"),
            expiredAt=None,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            status="closed",
            openTx="OPENTX123",
            closeTx="CLOSETX456",
            programVersion="v1.0",
            trades=[trade]
        )
        order_store.store_closed_order(closed_order)

        with sqlite3.connect(test_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                (
                    "SELECT inputAmount, outputAmount, feeAmount "
                    "FROM trades WHERE orderKey = ?"
                ),
                ("order_key",)
            )
            row = cursor.fetchone()
            assert isinstance(row["inputAmount"], str)
            assert isinstance(row["outputAmount"], str)
            assert isinstance(row["feeAmount"], str)

            try:
                assert Decimal(row["inputAmount"]) == Decimal("10.0")
                assert Decimal(row["outputAmount"]) == Decimal("9.5")
                assert Decimal(row["feeAmount"]) == Decimal("0.5")
            except (ValueError, ArithmeticError):
                pytest.fail(
                    "Trade decimal fields not stored as valid numeric strings."
                )

    def test_store_closed_order_atomicity_rolls_back_on_trade_failure(
        self, order_store, test_db
    ):
        valid_trade = Trade(
            orderKey="order_key",
            keeper="keeper",
            inputMint="mint",
            outputMint="mint",
            inputAmount=Decimal("10.0"),
            outputAmount=Decimal("9.5"),
            feeMint="fee",
            feeAmount=Decimal("0.5"),
            txId="TX_ATOMIC1",
            confirmedAt=datetime.now(),
            action="sell",
            productMeta="Meta"
        )
        invalid_trade = Trade(
            orderKey="order_key",
            keeper="keeper",
            inputMint="mint",
            outputMint="mint",
            inputAmount=Decimal("5.0"),
            outputAmount=Decimal("4.8"),
            feeMint="fee",
            feeAmount=Decimal("0.2"),
            txId="",
            confirmedAt=datetime.now(),
            action="sell",
            productMeta="Meta"
        )
        closed_order = ClosedOrder(
            userPubkey="user_pubkey",
            orderKey="order_key",
            inputMint="input_mint",
            outputMint="output_mint",
            makingAmount=Decimal("15.0"),
            takingAmount=Decimal("14.3"),
            remainingMakingAmount=Decimal("0.0"),
            remainingTakingAmount=Decimal("0.0"),
            expiredAt=None,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            status="closed",
            openTx="OPENTX123",
            closeTx="CLOSETX456",
            programVersion="v1.0",
            trades=[valid_trade, invalid_trade]
        )
        with pytest.raises(sqlite3.IntegrityError):
            order_store.store_closed_order(closed_order)

        assert order_store.get_order("order_key") is None

    def test_order_exists_returns_true_for_stored_order(self, order_store):
        closed_order = ClosedOrder(
            userPubkey="user_pubkey",
            orderKey="order_key",
            inputMint="input_mint",
            outputMint="output_mint",
            makingAmount=Decimal("8.0"),
            takingAmount=Decimal("7.5"),
            remainingMakingAmount=Decimal("0.0"),
            remainingTakingAmount=Decimal("0.0"),
            expiredAt=None,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            status="closed",
            openTx="OPENTX123",
            closeTx="CLOSETX456",
            programVersion="v1.0",
            trades=[]
        )
        order_store.store_closed_order(closed_order)
        assert order_store.order_exists("order_key") is True

    def test_order_exists_returns_false_for_missing_order(self, order_store):
        missing_order_key = "nonexistent_order"
        assert order_store.order_exists(missing_order_key) is False

    def test_multiple_connections_can_access_db(self, order_store, test_db):
        closed_order = ClosedOrder(
            userPubkey="user_pubkey",
            orderKey="order_key",
            inputMint="input_mint",
            outputMint="output_mint",
            makingAmount=Decimal("12.0"),
            takingAmount=Decimal("11.5"),
            remainingMakingAmount=Decimal("0.0"),
            remainingTakingAmount=Decimal("0.0"),
            expiredAt=None,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            status="closed",
            openTx="OPENTX123",
            closeTx="CLOSETX456",
            programVersion="v1.0",
            trades=[]
        )
        order_store.store_closed_order(closed_order)
        with sqlite3.connect(test_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM closed_orders WHERE orderKey = ?", ("order_key",)
            )
            row = cursor.fetchone()
            assert row is not None
            assert row["userPubkey"] == "user_pubkey"
