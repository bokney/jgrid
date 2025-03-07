
import pytest
from solders.pubkey import Pubkey
from pydantic_core import ValidationError
from src.tokens import Token


class TestToken:
    def test_token_creation_success(self):
        address = str(Pubkey.new_unique())
        token = Token(
            address=address,
            name="TestToken",
            symbol="TTK",
            decimals=18
        )
        assert token.address == address
        assert token.name == "TestToken"
        assert token.symbol == "TTK"
        assert token.decimals == 18

    def test_token_missing_field(self):
        with pytest.raises(Exception):
            Token(
                address=str(Pubkey.new_unique()),
                name="TestToken",
                symbol="TTK"
            )

    def test_token_is_frozen(self):
        token = Token(
            address=str(Pubkey.new_unique()),
            name="TestToken",
            symbol="TTK",
            decimals=18
        )
        with pytest.raises(ValidationError):
            token.name = str(Pubkey.new_unique())
