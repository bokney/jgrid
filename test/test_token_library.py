
import json
import pytest
import threading
from unittest.mock import patch, MagicMock
from src.tokens import Token
from src.solana_rpc import SolanaRPC
from src.token_library import TokenLibrary
from src.dexscreener_api import DEXScreenerAPI


@pytest.fixture
def sample_tokens():
    return [
        Token(address="A", name="TokenA", symbol="TKA", decimals=18),
        Token(address="B", name="TokenB", symbol="TKB", decimals=8)
    ]


@pytest.fixture
def token_library(sample_tokens, tmp_path, monkeypatch):
    monkeypatch.setattr(TokenLibrary, "load_tokens", lambda self: None)
    lib = TokenLibrary()
    lib.tokens = {token.address: token for token in sample_tokens}
    lib._filepath = tmp_path / "tokens.json"
    return lib


class TestTokenLibrary:
    def test_token_library_is_singleton(self):
        client_1 = TokenLibrary()
        client_2 = TokenLibrary()
        assert client_1 is client_2

    def test_token_library_thread_safety(self):
        instances = []

        def get_instance():
            instances.append(TokenLibrary())

        threads = [threading.Thread(target=get_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(instance is instances[0] for instance in instances)

    def test_save_tokens_success(self, tmp_path, token_library):
        token_library._filepath = tmp_path / "tokens.json"
        token_library.save_tokens()

        expected = json.dumps(
            [token.model_dump() for token in token_library.tokens.values()],
            indent=4
        )

        with open(token_library._filepath, "r") as file:
            file_content = file.read()

        assert json.loads(file_content) == json.loads(expected)

    def test_load_tokens_success(self, tmp_path, token_library):
        token_library._filepath = tmp_path / "tokens.json"
        token_library.save_tokens()

        loaded_library = TokenLibrary()
        loaded_library._filepath = tmp_path / "tokens.json"
        loaded_library.load_tokens()

        assert loaded_library.tokens == token_library.tokens
        assert loaded_library is token_library

    def test_load_tokens_invalid_json(self, tmp_path):
        filepath = tmp_path / "invalid.json"
        filepath.write_text("this is not valid json")
        lib = TokenLibrary()
        lib._filepath = filepath

        with pytest.raises(Exception) as exc_info:
            lib.load_tokens()
        assert "Error loading tokens" in str(exc_info.value)

    def test_load_tokens_file_not_found(self, tmp_path, monkeypatch):
        TokenLibrary._instance = None
        non_existent_file = tmp_path / "nonexistent.json"
        assert not non_existent_file.exists()

        monkeypatch.setattr(TokenLibrary, "_filepath", non_existent_file)
        lib = TokenLibrary()

        assert lib.tokens == {}

    def test_get_token_info_success(self, token_library):
        token_address = "So11111111111111111111111111111111111111112"
        mock_token_info = {"name": "MockToken", "symbol": "MKT"}
        mock_decimals = 6

        with patch.object(
            DEXScreenerAPI, "get_token_info", return_value=mock_token_info
        ), patch.object(
            SolanaRPC, "get_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.value.decimals = mock_decimals
            mock_client.get_token_supply.return_value = mock_response
            mock_get_client.return_value = mock_client

            token = token_library.get_token_info(token_address)

            assert isinstance(token, Token)
            assert token.address == token_address
            assert token.name == "MockToken"
            assert token.symbol == "MKT"
            assert token.decimals == mock_decimals

    def test_get_token_info_failure(self, token_library):
        token_address = "INVALIDTOKEN"

        with patch.object(
            DEXScreenerAPI, "get_token_info"
        ), patch.object(
            SolanaRPC, "get_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_client.get_token_supply.return_value = mock_response
            mock_get_client.return_value = mock_client

            with pytest.raises(Exception):
                token_library.get_token_info(token_address)
