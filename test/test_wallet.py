
import pytest
from pydantic import ValidationError
from decimal import Decimal
from solders.pubkey import Pubkey
from unittest.mock import MagicMock
from solders.keypair import Keypair
from src.tokens import Token
from src.wallet import Wallet
from src.solana_rpc import SolanaRPC
from src.token_library import TokenLibrary


@pytest.fixture
def sample_tokens():
    return [
        Token(address="A", name="TokenA", symbol="TKA", decimals=18),
        Token(address="B", name="TokenB", symbol="TKB", decimals=8)
    ]


@pytest.fixture
def token_library(sample_tokens, tmp_path):
    lib = TokenLibrary()
    lib.tokens = {token.address: token for token in sample_tokens}
    lib._filepath = tmp_path / "tokens.json"
    return lib


class TestWallet:
    def test_wallet_accepts_token_as_key(self, sample_tokens):
        token_a = sample_tokens[0]
        token_b = sample_tokens[1]
        tokens = {
            token_a: Decimal("123.45"),
            token_b: Decimal("67.89")
        }
        wallet = Wallet(address="test_wallet")
        wallet._tokens = tokens
        assert wallet.get_token_quantity(token_a) == Decimal("123.45")
        assert wallet.get_token_quantity(token_b) == Decimal("67.89")

    def test_wallet_accepts_address_as_key(self, sample_tokens):
        token_a = sample_tokens[0]
        token_b = sample_tokens[1]
        tokens = {
            token_a: Decimal("123.45"),
            token_b: Decimal("67.89")
        }
        wallet = Wallet(address="test_wallet")
        wallet._tokens = tokens

        assert token_a in wallet._tokens
        assert token_b in wallet._tokens
        assert wallet.get_token_quantity("A") == Decimal("123.45")
        assert wallet.get_token_quantity("B") == Decimal("67.89")

    def test_wallet_accepts_symbol_as_key(self, sample_tokens):
        token_a = sample_tokens[0]
        token_b = sample_tokens[1]
        tokens = {
            token_a: Decimal("123.45"),
            token_b: Decimal("67.89")
        }
        wallet = Wallet(address="test_wallet")
        wallet._tokens = tokens

        assert token_a in wallet._tokens
        assert token_b in wallet._tokens
        assert wallet.get_token_quantity("TKA") == Decimal("123.45")
        assert wallet.get_token_quantity("TKB") == Decimal("67.89")

    def test_wallet_nonexistent_key(self):
        wallet = Wallet(address="test_wallet")

        with pytest.raises(KeyError):
            wallet.get_token_quantity("NON-EXISTENT-KEY")

    def test_wallet_invalid_key_type(self, sample_tokens):
        token_a = sample_tokens[0]
        token_b = sample_tokens[1]
        tokens = {
            token_a: Decimal("123.45"),
            token_b: Decimal("67.89")
        }
        wallet = Wallet(address="test_wallet")
        wallet._tokens = tokens

        with pytest.raises(TypeError):
            wallet.get_token_quantity(1)

    def test_wallet_stores_keypair(self):
        dummy_keypair = Keypair()
        wallet = Wallet(keypair=dummy_keypair)
        assert wallet.keypair is dummy_keypair

    def test_wallet_accepts_either_address_or_keypair_but_not_both(self):
        wallet_a = Wallet(address=str(Pubkey.new_unique()))
        wallet_b = Wallet(keypair=Keypair())
        with pytest.raises(ValidationError):
            wallet_c = Wallet(
                address=str(Pubkey.new_unique()),
                keypair=Keypair()
            )

    def test_update_tokens_success(self, monkeypatch, token_library):
        wallet = Wallet(address=str(Pubkey.new_unique()))

        mock_token_account = MagicMock()
        mock_token_account.mint = "FAKE_MINT_ADDRESS"
        mock_token_account.amount = 123450000000

        mock_account = MagicMock()
        mock_account.account.data = b"FAKE_DATA"
        mock_account.pubkey = "FAKE_PUBKEY"

        monkeypatch.setattr(
            "src.wallet.TokenAccount.from_bytes",
            lambda data: mock_token_account
        )

        mock_token = Token(
            address="FAKE_MINT_ADDRESS",
            name="FakeToken",
            symbol="FTK",
            decimals=9
        )
        monkeypatch.setattr(
            TokenLibrary, "get_token_info", lambda self, addr: mock_token
        )
        monkeypatch.setattr(
            TokenLibrary, "add_token", lambda self, token: None
        )

        mock_rpc_response = MagicMock()
        mock_rpc_response.value.decimals = 9
        mock_client = MagicMock()
        mock_client.get_token_supply.return_value = mock_rpc_response
        monkeypatch.setattr(SolanaRPC, "get_client", lambda: mock_client)

        mock_get_accounts_response = MagicMock()
        mock_get_accounts_response.value = [mock_account]
        monkeypatch.setattr(
            mock_client,
            "get_token_accounts_by_owner",
            lambda owner, opts: mock_get_accounts_response
        )

        wallet.update_tokens()

        expected_balance = Decimal("123.45")

        found = False
        for token, balance in wallet._tokens.items():
            if (
                token.address == mock_token.address
                and balance == expected_balance
            ):
                found = True
                break
        assert found

    def test_update_tokens_no_accounts(self, monkeypatch):
        wallet = Wallet(address=str(Pubkey.new_unique()))

        mock_client = MagicMock()
        mock_get_accounts_response = MagicMock()
        mock_get_accounts_response.value = []
        monkeypatch.setattr(SolanaRPC, "get_client", lambda: mock_client)
        monkeypatch.setattr(
            mock_client,
            "get_token_accounts_by_owner",
            lambda owner, opts: mock_get_accounts_response
        )

        wallet._tokens = {}
        wallet.update_tokens()

        assert wallet._tokens == {}

    def test_update_tokens_partial_failure(self, monkeypatch):
        wallet = Wallet(address=str(Pubkey.new_unique()))

        mock_account_good = MagicMock()
        mock_account_good.account.data = b"GOOD_DATA"
        mock_account_good.pubkey = "GOOD_PUBKEY"

        mock_account_bad = MagicMock()
        mock_account_bad.account.data = b"BAD_DATA"
        mock_account_bad.pubkey = "BAD_PUBKEY"

        mock_get_accounts_response = MagicMock()
        mock_get_accounts_response.value = [
            mock_account_good, mock_account_bad
        ]

        mock_client = MagicMock()
        monkeypatch.setattr(SolanaRPC, "get_client", lambda: mock_client)
        monkeypatch.setattr(
            mock_client,
            "get_token_accounts_by_owner",
            lambda owner, opts: mock_get_accounts_response
        )

        def mock_from_bytes(data):
            if data == b"GOOD_DATA":
                mock = MagicMock()
                mock.mint = "GOOD_MINT"
                mock.amount = 1000000000
                return mock
            else:
                raise Exception("Decoding error")
        monkeypatch.setattr(
            "src.wallet.TokenAccount.from_bytes", mock_from_bytes
        )
        mock_token = Token(
            address="GOOD_MINT", name="GoodToken", symbol="GOOD", decimals=9
        )
        monkeypatch.setattr(
            TokenLibrary, "get_token_info", lambda self, addr: mock_token
        )
        monkeypatch.setattr(
            TokenLibrary, "add_token", lambda self, token: None
        )

        wallet._tokens = {}
        wallet.update_tokens()

        expected_balance = Decimal("1")

        assert len(wallet._tokens) == 1
        for token_obj, balance in wallet._tokens.items():
            assert token_obj.address == "GOOD_MINT"
            assert balance == expected_balance
