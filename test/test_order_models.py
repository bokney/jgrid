
import pytest
from decimal import Decimal
from datetime import datetime
from pydantic_core import ValidationError
from src.jupiter_api import OpenOrder, Trade, ClosedOrder


class TestOpenOrder:
    def test_open_order_creation_success(self):
        order = OpenOrder(
            publicKey="public_key",
            borrowMakingAmount=Decimal("100.0"),
            createdAt=datetime.now(),
            expiredAt=datetime.now(),
            makingAmount=Decimal("50.0"),
            oriMakingAmount=Decimal("50.0"),
            oriTakingAmount=Decimal("30.0"),
            takingAmount=Decimal("30.0"),
            uniqueId=1,
            updatedAt=datetime.now(),
            feeAccount="fee_account",
            inputMint="input_mint",
            inputMintReserve="input_mint_reserve",
            inputTokenProgram="input_token_program",
            maker="maker",
            outputMint="output_mint",
            outputTokenProgram="output_token_program",
            feeBps=10,
            bump=1
        )
        assert order.borrowMakingAmount == Decimal("100.0")
        assert order.inputMint == "input_mint"
        assert order.uniqueId == 1

    def test_open_order_missing_required_fields(self):
        with pytest.raises(Exception):
            OpenOrder(
                borrowMakingAmount=Decimal("100.0"),
                createdAt=datetime.now(),
                expiredAt=datetime.now(),
                oriMakingAmount=Decimal("50.0"),
                oriTakingAmount=Decimal("30.0"),
                takingAmount=Decimal("30.0"),
                uniqueId=1,
                updatedAt=datetime.now(),
                feeAccount="fee_account",
                inputMint="input_mint",
                inputMintReserve="input_mint_reserve",
                inputTokenProgram="input_token_program",
                maker="maker",
                outputMint="output_mint",
                outputTokenProgram="output_token_program",
                feeBps=10,
                bump=1
            )


class TestTrade:
    def test_trade_creation_success(self):
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
            action="buy",
            productMeta="Some metadata"
        )
        assert trade.txId == "TX123"
        assert trade.action == "buy"

    def test_trade_missing_required_fields(self):
        with pytest.raises(ValidationError):
            Trade(
                orderKey="order_key",
                keeper="keeper",
                inputMint="input_mint",
                outputMint="output_mint",
                inputAmount=Decimal("10.0"),
                outputAmount=Decimal("9.5"),
                feeMint="fee_mint",
                feeAmount=Decimal("0.5"),
                confirmedAt=datetime.now(),
                action="buy"
            )


class TestClosedOrder:
    def test_closed_order_creation_success(self):
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
            action="buy",
            productMeta="Some metadata"
        )
        closed_order = ClosedOrder(
            userPubkey="user_pubkey",
            orderKey="order_key",
            inputMint="input_mint",
            outputMint="output_mint",
            makingAmount=Decimal("100.0"),
            takingAmount=Decimal("50.0"),
            remainingMakingAmount=Decimal("0.0"),
            remainingTakingAmount=Decimal("0.0"),
            expiredAt=datetime.now(),
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            status="filled",
            openTx="OPENTX123",
            closeTx="CLOSETX456",
            programVersion="v1.0",
            trades=[trade]
        )
        assert closed_order.status == "filled"
        assert len(closed_order.trades) == 1
        assert closed_order.trades[0] is trade

    def test_closed_order_missing_required_fields(self):
        with pytest.raises(ValidationError):
            ClosedOrder(
                userPubkey="user_pubkey",
                orderKey="order_key",
                inputMint="input_mint",
                outputMint="output_mint",
                makingAmount=Decimal("100.0"),
                takingAmount=Decimal("50.0"),
                remainingMakingAmount=Decimal("0.0"),
                remainingTakingAmount=Decimal("0.0"),
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
                status="filled",
                openTx="OPENTX123",
                programVersion="v1.0",
                trades=[]
            )
