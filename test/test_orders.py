
import pytest
from decimal import Decimal
from datetime import datetime
from src.orders import OpenOrder


class TestOpenOrder:
    def test_open_order_creation_success(self):
        order = OpenOrder(
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
