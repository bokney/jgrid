
import base64
import pytest
import requests
from decimal import Decimal
from solders.keypair import Keypair
from unittest.mock import patch, MagicMock
from solders.transaction import VersionedTransaction
from src.jupiter_api import JupiterLimitOrderAPI
from src.wallet import Wallet
from mock_api_responses import (
    MOCK_GET_OPEN_ORDERS,
    MOCK_GET_ORDER_HISTORY_PAGE_1,
    MOCK_GET_ORDER_HISTORY_PAGE_2
)


class DummyResponse:
    def __init__(self, status_code, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"Status: {self.status_code}")

    def json(self):
        if self._json_data is not None:
            return self._json_data
        raise ValueError("No JSON")


class TestGetJsonResponse:
    @pytest.fixture
    def api_instance(self):
        return JupiterLimitOrderAPI()

    def test_get_json_response_success(self, api_instance):
        dummy_json = {"key": "value"}
        response = DummyResponse(200, dummy_json)
        result = api_instance._get_json_response(response)

        assert result == dummy_json

    def test_get_json_response_http_error(self, api_instance):
        response = DummyResponse(404, text="Not Found")
        with pytest.raises(Exception) as exc_info:
            api_instance._get_json_response(response)

        assert "Not Found" in str(exc_info.value)

    def test_get_json_response_invalid_json(self, api_instance):
        response = DummyResponse(200, None, text="Internal Server Error")
        with pytest.raises(Exception) as exc_info:
            api_instance._get_json_response(response)

        assert "Invalid JSON" in str(exc_info.value)


class TestSignAndSendTransaction:
    @pytest.fixture
    def api_instance(self):
        api = JupiterLimitOrderAPI()
        dummy_result = MagicMock()
        dummy_result.value = "tx_signature"
        api._rpc_client = MagicMock()
        api._rpc_client.send_raw_transaction.return_value = dummy_result
        return api

    @pytest.fixture
    def dummy_wallet(self):
        keypair = Keypair()
        return Wallet(keypair=keypair)

    def test_sign_and_send_transaction_success(
        self, api_instance, dummy_wallet
    ):
        dummy_serialized = b"dummy_serialized"
        dummy_tx_base64 = base64.b64encode(dummy_serialized).decode("utf-8")

        dummy_tx = MagicMock()
        dummy_tx.message = "dummy_message"
        with patch.object(
            VersionedTransaction,
            "from_bytes",
            return_value=dummy_tx
        ):
            dummy_signed_tx = MagicMock()
            dummy_signed_tx.__bytes__ = lambda: b"dummy_signed"
            with patch.object(
                VersionedTransaction,
                "__new__",
                return_value=dummy_signed_tx
            ):
                result = api_instance._sign_and_send_transaction(
                    dummy_wallet, dummy_tx_base64
                )

        assert result == "tx_signature"
        api_instance._rpc_client.send_raw_transaction.assert_called_once()


class TestBase:
    @pytest.fixture
    def dummy_rpc_client(self):
        rpc_client = MagicMock()
        dummy_result = MagicMock()
        dummy_result.value = "dummy_tx_signature"
        rpc_client.send_raw_transaction.return_value = dummy_result
        return rpc_client

    @pytest.fixture(autouse=True)
    def setup_api(self, dummy_rpc_client):
        self.api = JupiterLimitOrderAPI()
        self.api._logger = MagicMock()
        self.api._rpc_client = dummy_rpc_client

    @pytest.fixture
    def dummy_keypair(self):
        return Keypair()

    @pytest.fixture
    def dummy_wallet(self, dummy_keypair):
        return Wallet(keypair=dummy_keypair)


class TestCreateLimitOrder(TestBase):
    @pytest.fixture
    def dummy_api_response(self):
        return {
            "order": "CFG9Bmppz7eZbna96UizACJPYT3UgVgps3KkMNNo6P4k",
            "tx": (
                "AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                "AAAAAAAAAAAAAAAAAAAAAACAAQAJDpTx"
                "Dp/xl7Xf1xr/AvZ2toT7RQ+sPKtJ3EXY"
                "YDjpc6n5NLjEhcfvvYS1FMk1x/xTZz6l"
                "XvBY8ahgHexvAioy59aRS0Fv6FPiAVy7"
                "Xr9yJejYQIT5CYlfamvD0yJJR8gjU9qg"
                "w0AEF4kjC6AYjS3tqXl1nOkykCuEjM9Z"
                "J7+FDTQVAYhY5Li0AMBYqNfFTHinm76y"
                "MtngS7NvNBcDf9hYcyoDBkZv5SEXMv/s"
                "rbpyw5vnvIzlu8X3EmssQ5s6QAAAAIyX"
                "JY9OJInxuz0QKRSODYMLWhOZ2v8QhASO"
                "e9jb6fhZxEBRqRG1TH7P/H7gsKQK9Isy"
                "iudVqZUzyEAssm30OAcAAAAAAAAAAAAA"
                "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAbd"
                "9uHXZaGT2cvhRs7reawctIXtX1s3kTqM"
                "9YV+/wCpCsNKlsFmcVpgwSM+yiWKDfML"
                "HshY4HRcc2oSYmZjSyIQiYnNzGGPBnZ0"
                "rGd+KZqtsSj+INnM2CjlCMnxv5sw68b6"
                "evO+2606PWXzaqvJdDGxu+TC0vbg5Hym"
                "AgNFL11hkn9sh+xDEAWX2S7IDh4PwuUs"
                "i7/8dQ+DB2YEV+4zsuGo3Hgci1ZtTlqF"
                "fRVfzXVLPsjvoeOru9qF40dVAjQ/tQQF"
                "AAkDtLQAAAAAAAAFAAUCzisBAAYGAAEA"
                "BwgJAQEKDwAAAgMECwoMBwkJCAYNCiWF"
                "bkqvcJ/1n4EHr6bNmZzBgJaYAAAAAAAA"
                "4fUFAAAAAAAAAQAAAA=="
            )
        }

    @patch("src.jupiter_api.requests.post")
    def test_create_limit_order_success(
        self,
        mock_post,
        dummy_rpc_client,
        dummy_wallet,
        dummy_api_response
    ):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = dummy_api_response
        mock_post.return_value = mock_response

        expected_tx = "dummy_tx_signature"
        dummy_rpc_client.send_raw_transaction.return_value = MagicMock(
            value=expected_tx
        )

        with patch(
            "src.jupiter_api.VersionedTransaction",
            return_value=MagicMock(
                __bytes__=lambda self: b"dummy_serialized",
                message="dummy_message")
        ):
            result = self.api.create_limit_order(
                wallet=dummy_wallet,
                inputMint="input_mint",
                outputMint="output_mint",
                maker="maker_address",
                payer="payer_address",
                makingAmount=Decimal("100"),
                takingAmount=Decimal("200")
            )

        assert result == expected_tx
        dummy_rpc_client.send_raw_transaction.assert_called_once()
        mock_post.assert_called_once()

    @patch("src.jupiter_api.requests.post")
    def test_create_limit_order_failure(
        self, mock_post, dummy_wallet
    ):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "Invalid order parameters"
        }
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            self.api.create_limit_order(
                wallet=dummy_wallet,
                inputMint="input_mint",
                outputMint="output_mint",
                maker="maker_address",
                payer="payer_address",
                makingAmount=Decimal("100"),
                takingAmount=Decimal("200")
            )

        assert "Unexpected response from Jupiter" in str(exc_info.value)
        mock_post.assert_called_once()

    @patch("src.jupiter_api.requests.post")
    @patch("src.jupiter_api.Keypair.from_base58_string")
    @patch("src.jupiter_api.VersionedTransaction.from_bytes")
    @patch("src.jupiter_api.VersionedTransaction")
    def test_create_limit_order_optional_parameters(
        self,
        mock_versioned_tx,
        mock_from_bytes,
        mock_keypair,
        mock_post,
        dummy_rpc_client,
        dummy_api_response,
        dummy_wallet
    ):
        expected_payload = {
            "wallet": dummy_wallet.address,
            "inputMint": "input_mint",
            "outputMint": "output_mint",
            "maker": "maker_address",
            "payer": "payer_address",
            "params": {
                "makingAmount": "100",
                "takingAmount": "200",
                "expiredAt": "1700000000",
                "feeBps": "5"
            },
            "computeUnitPrice": "auto",
            "referral": "referral_account",
            "inputTokenProgram": "token_program_1",
            "outputTokenProgram": "token_program_2",
            "wrapAndUnwrapSol": "true"
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = dummy_api_response
        mock_post.return_value = mock_response

        dummy_result = MagicMock()
        dummy_result.value = "dummy_tx_signature"
        dummy_rpc_client.send_raw_transaction.return_value = dummy_result
        self.api._rpc_client = dummy_rpc_client

        mock_keypair.return_value = MagicMock(
            pubkey=lambda: "mock_wallet_address",
            __str__=lambda self: "mock_wallet_address"
        )

        mock_from_bytes.return_value = MagicMock(message="dummy_message")
        mock_versioned_tx.return_value = MagicMock()

        self.api.create_limit_order(
            wallet=dummy_wallet,
            inputMint="input_mint",
            outputMint="output_mint",
            maker="maker_address",
            payer="payer_address",
            makingAmount=Decimal("100"),
            takingAmount=Decimal("200"),
            expiredAt=1700000000,
            feeBps=5,
            computeUnitPrice="auto",
            referral="referral_account",
            inputTokenProgram="token_program_1",
            outputTokenProgram="token_program_2",
            wrapAndUnwrapSol=True
        )

        mock_post.assert_called_once()
        actual_payload = mock_post.call_args.kwargs["json"]
        assert actual_payload == expected_payload
        assert set(actual_payload.keys()) == set(expected_payload.keys())

    @patch("src.jupiter_api.requests.post")
    @patch("src.jupiter_api.VersionedTransaction")
    def test_create_limit_order_excludes_optional_flags_when_false(
        self,
        mock_versioned_tx,
        mock_post,
        dummy_rpc_client,
        dummy_api_response,
        dummy_wallet
    ):
        expected_payload = {
            "wallet": dummy_wallet.address,
            "inputMint": "input_mint",
            "outputMint": "output_mint",
            "maker": "maker_address",
            "payer": "payer_address",
            "params": {
                "makingAmount": "100",
                "takingAmount": "200"
            }
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = dummy_api_response
        mock_post.return_value = mock_response

        dummy_result = MagicMock()
        dummy_result.value = "dummy_tx_signature"
        dummy_rpc_client.send_raw_transaction.return_value = dummy_result
        self.api._rpc_client = dummy_rpc_client

        self.api.create_limit_order(
            wallet=dummy_wallet,
            inputMint="input_mint",
            outputMint="output_mint",
            maker="maker_address",
            payer="payer_address",
            makingAmount=Decimal("100"),
            takingAmount=Decimal("200"),
            feeBps=False,
            computeUnitPrice=None,
            referral=False,
            inputTokenProgram=None,
            outputTokenProgram=False,
            wrapAndUnwrapSol=None
        )

        mock_post.assert_called_once()
        actual_payload = mock_post.call_args.kwargs["json"]
        assert actual_payload == expected_payload
        assert set(actual_payload.keys()) == set(expected_payload.keys())

    @patch("src.jupiter_api.requests.post")
    @patch("src.jupiter_api.Keypair.from_base58_string")
    @patch("src.jupiter_api.VersionedTransaction.from_bytes")
    @patch("src.jupiter_api.VersionedTransaction")
    def test_create_limit_order_correct_endpoint_url(
        self,
        mock_versioned_tx,
        mock_from_bytes,
        mock_keypair,
        mock_post,
        dummy_rpc_client,
        dummy_api_response,
        dummy_wallet
    ):
        expected_url = "https://api.jup.ag/limit/v2/createOrder"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = dummy_api_response
        mock_post.return_value = mock_response

        dummy_result = MagicMock()
        dummy_result.return_value = "dummy_tx_signature"
        dummy_rpc_client.send_raw_transaction.return_value = dummy_result
        self.api._rpc_client = dummy_rpc_client

        mock_keypair.return_value = MagicMock(
            pubkey=lambda: "mock_wallet_address",
            __str__=lambda self: "mock_wallet_address"
        )

        mock_from_bytes.return_value = MagicMock(message="dummy_message")
        mock_versioned_tx.return_value = MagicMock()

        self.api.create_limit_order(
            wallet=dummy_wallet,
            inputMint="input_mint",
            outputMint="output_mint",
            maker="maker_address",
            payer="payer_address",
            makingAmount=Decimal("100"),
            takingAmount=Decimal("200")
        )

        actual_url = mock_post.call_args.kwargs["url"]
        assert actual_url == expected_url
        mock_post.assert_called_once()

    @patch("src.jupiter_api.requests.post")
    def test_create_limit_order_network_error_handling(
        self, mock_post, dummy_wallet
    ):
        mock_post.side_effect = requests.exceptions.RequestException(
            "Network error"
        )

        with pytest.raises(Exception):
            self.api.create_limit_order(
                wallet=dummy_wallet,
                inputMint="input_mint",
                outputMint="output_mint",
                maker="maker_address",
                payer="payer_address",
                makingAmount=Decimal("100"),
                takingAmount=Decimal("200")
            )

        mock_post.assert_called_once()

    @patch("src.jupiter_api.requests.post")
    @patch("src.jupiter_api.Keypair.from_base58_string")
    @patch("src.jupiter_api.VersionedTransaction.from_bytes")
    @patch("src.jupiter_api.VersionedTransaction")
    def test_create_limit_order_success_response_parsing(
        self,
        mock_versioned_tx,
        mock_from_bytes,
        mock_keypair,
        mock_post,
        dummy_rpc_client,
        dummy_api_response
    ):
        expected_response = dummy_api_response

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "order": "some_order",
            "tx": base64.b64encode(b"dummy_serialized").decode("utf-8")
        }
        mock_post.return_value = mock_response

        dummy_result = MagicMock()
        dummy_result.value = expected_response
        dummy_rpc_client.send_raw_transaction.return_value = dummy_result
        self.api._rpc_client = dummy_rpc_client

        keypair = Keypair()
        dummy_wallet = Wallet(keypair=keypair)

        mock_keypair.return_value = MagicMock(
            pubkey=lambda: str(keypair.pubkey()),
            __str__=lambda self: str(keypair.pubkey())
        )

        mock_from_bytes.return_value = MagicMock(message="dummy_message")
        mock_versioned_tx.return_value = MagicMock(
            __bytes__=lambda self: b"dummy_serialized"
        )

        result = self.api.create_limit_order(
            wallet=dummy_wallet,
            inputMint="input_mint",
            outputMint="output_mint",
            maker="maker_address",
            payer="payer_address",
            makingAmount="100",
            takingAmount="200"
        )

        assert result == expected_response
        mock_post.assert_called_once()

    @patch("src.jupiter_api.requests.post")
    def test_create_limit_order_non_json_error_response(
        self, mock_post, dummy_wallet
    ):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("No JSON")
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            self.api.create_limit_order(
                wallet=dummy_wallet,
                inputMint="input_mint",
                outputMint="output_mint",
                maker="maker_address",
                payer="payer_address",
                makingAmount=Decimal("100"),
                takingAmount=Decimal("200")
            )

        assert "Internal Server Error" in str(exc_info.value)
        mock_post.assert_called_once()


class TestCancelOrder(TestBase):
    @patch("src.jupiter_api.requests.post")
    def test_cancel_order_success(self, mock_post, dummy_wallet):
        dummy_tx_base64 = base64.b64encode(b"dummy_serialized").decode("utf-8")
        api_response = {"txs": [dummy_tx_base64]}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = api_response
        mock_post.return_value = mock_response

        with patch.object(
            self.api,
            "_sign_and_send_transaction",
            return_value="dummy_cancel_signature"
        ):
            result = self.api.cancel_order(
                wallet=dummy_wallet,
                maker="maker_address"
            )

        assert result == ["dummy_cancel_signature"]
        mock_post.assert_called_once()

    @patch("src.jupiter_api.requests.post")
    def test_cancel_order_failure(self, mock_post, dummy_wallet):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Cancellation failed"}
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            self.api.cancel_order(
                wallet=dummy_wallet,
                maker="maker_address"
            )

        assert "Cancellation failed" in str(exc_info.value)
        mock_post.assert_called_once()

    @patch("src.jupiter_api.requests.post")
    def test_cancel_order_without_optional_params(
        self, mock_post, dummy_wallet
    ):
        expected_payload = {
            "maker": "maker_address",
            "orders": [(
                "AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA......FWPqnIQMDAAk"
                "DvRcoAAAAAAADAAUCY10AAAQJAAABAgQFBgcECF+B7fAIMd+EAA=="
            )]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        dummy_tx_base64 = base64.b64encode(b"dummy_serialized").decode("utf-8")
        mock_response.json.return_value = {"txs": [dummy_tx_base64]}
        mock_post.return_value = mock_response

        with patch.object(
            self.api,
            "_sign_and_send_transaction",
            return_value="dummy_cancel_signature"
        ):
            self.api.cancel_order(
                wallet=dummy_wallet,
                maker="maker_address",
                orders=[(
                    "AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA......FWPqnIQMDAAk"
                    "DvRcoAAAAAAADAAUCY10AAAQJAAABAgQFBgcECF+B7fAIMd+EAA=="
                )]
            )

        mock_post.assert_called_once()
        actual_payload = mock_post.call_args.kwargs["json"]
        assert actual_payload == expected_payload

    @patch("src.jupiter_api.requests.post")
    def test_cancel_order_correct_endpoint_url(
        self, mock_post, dummy_wallet
    ):
        expected_url = "https://api.jup.ag/limit/v2/cancelOrder"
        mock_response = MagicMock()
        mock_response.status_code = 200
        dummy_tx_base64 = base64.b64encode(b"dummy_serialized").decode("utf-8")
        mock_response.json.return_value = {"txs": [dummy_tx_base64]}
        mock_post.return_value = mock_response

        with patch.object(
            self.api,
            "_sign_and_send_transaction",
            return_value="dummy_cancel_signature"
        ):
            self.api.cancel_order(
                wallet=dummy_wallet,
                maker="maker_address"
            )

        mock_post.assert_called_once()
        actual_url = mock_post.call_args.kwargs["url"]
        assert actual_url == expected_url

    @patch("src.jupiter_api.requests.post")
    def test_cancel_order_correct_http_method(
        self, mock_post, dummy_wallet
    ):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "txs": [(
                "AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA......FWPqnIQMDAAk"
                "DvRcoAAAAAAADAAUCY10AAAQJAAABAgQFBgcECF+B7fAIMd+EAA=="
            )]
        }
        mock_post.return_value = mock_response

        with patch.object(
            self.api,
            "_sign_and_send_transaction",
            return_value="dummy_cancel_signature"
        ):
            self.api.cancel_order(
                wallet=dummy_wallet,
                maker="maker_address"
            )

        mock_post.assert_called_once()

    @patch("src.jupiter_api.requests.post")
    def test_cancel_order_network_error_handling(
        self, mock_post, dummy_wallet
    ):
        mock_post.side_effect = requests.exceptions.RequestException(
            "Network error"
        )

        with pytest.raises(Exception) as exc_info:
            self.api.cancel_order(
                wallet=dummy_wallet,
                maker="maker_address"
            )
            assert "Network error" in str(exc_info.value)
            mock_post.assert_called_once()

    @patch("src.jupiter_api.requests.post")
    @patch("src.jupiter_api.VersionedTransaction")
    def test_cancel_order_success_response_parsing(
        self,
        mock_versioned_tx,
        mock_post,
        dummy_wallet,
        dummy_rpc_client
    ):
        dummy_tx_base64 = base64.b64encode(b"dummy_serialized").decode("utf-8")
        api_response = {"txs": [dummy_tx_base64]}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = api_response
        mock_post.return_value = mock_response

        dummy_result = MagicMock()
        dummy_result.value = "dummy_cancel_signature"
        dummy_rpc_client.send_raw_transaction.return_value = dummy_result
        self.api._rpc_client = dummy_rpc_client

        result = self.api.cancel_order(
            wallet=dummy_wallet,
            maker="maker_address"
        )

        assert isinstance(result, list)
        assert result == ["dummy_cancel_signature"]
        mock_post.assert_called_once()

    @patch("src.jupiter_api.requests.post")
    def test_cancel_order_non_json_error_response(
        self, mock_post, dummy_wallet
    ):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("No JSON")
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            self.api.cancel_order(
                wallet=dummy_wallet,
                maker="maker_address"
            )
        assert "Internal Server Error" in str(exc_info.value)
        mock_post.assert_called_once()


class TestGetOrderHistory(TestBase):
    @patch("src.jupiter_api.requests.get")
    def test_get_order_history_success(self, mock_get, dummy_wallet):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_GET_ORDER_HISTORY_PAGE_1
        mock_get.return_value = mock_response

        result = self.api.get_order_history(wallet=dummy_wallet)

        orders_list = MOCK_GET_ORDER_HISTORY_PAGE_1.get("orders", [])
        assert isinstance(result, list)
        assert len(result) == len(orders_list)
        if orders_list:
            assert result[0].orderKey == orders_list[0]["orderKey"]
        mock_get.assert_called_once()

    @patch("src.jupiter_api.requests.get")
    def test_get_order_history_failure(self, mock_get, dummy_wallet):
        error_data = {"error": "Invalid request"}
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "400 Client Error"
        )
        mock_response.json.return_value = error_data
        mock_get.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            self.api.get_order_history(wallet=dummy_wallet)
        assert "Bad Request" in str(exc_info.value)
        mock_get.assert_called_once()

    @patch("src.jupiter_api.requests.get")
    def test_get_order_history_page_success(self, mock_get, dummy_wallet):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_GET_ORDER_HISTORY_PAGE_2
        mock_get.return_value = mock_response

        result = self.api.get_order_history(wallet=dummy_wallet, page=2)
        orders_list = MOCK_GET_ORDER_HISTORY_PAGE_2.get("orders", [])

        assert isinstance(result, list)
        assert len(result) == len(orders_list)
        if orders_list:
            assert result[0].orderKey == orders_list[0]["orderKey"]
        params = mock_get.call_args.kwargs.get("params")
        assert params is not None
        assert params.get("page") == 2
        mock_get.assert_called_once()

    @patch("src.jupiter_api.requests.get")
    def test_get_order_history_page_failure(self, mock_get, dummy_wallet):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"orders": []}
        mock_get.return_value = mock_response

        result = self.api.get_order_history(wallet=dummy_wallet, page=999)

        assert result == []
        mock_get.assert_called_once()

    @patch("src.jupiter_api.requests.get")
    def test_get_order_history_payload_integrity(self, mock_get, dummy_wallet):
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_response.json.return_value = {"orders": []}
        mock_get.return_value = mock_response

        self.api.get_order_history(wallet=dummy_wallet, page=3)

        params = mock_get.call_args.kwargs.get("params")
        assert params is not None
        assert params["wallet"] == dummy_wallet.address
        assert params["page"] == 3
        mock_get.assert_called_once()

    @patch("src.jupiter_api.requests.get")
    def test_get_order_history_correct_endpoint_url_and_http_method(
        self, mock_get, dummy_wallet
    ):
        expected_url = "https://api.jup.ag/limit/v2/orderHistory"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"orders": []}
        mock_get.return_value = mock_response

        self.api.get_order_history(wallet=dummy_wallet)

        actual_args = mock_get.call_args[0]
        if actual_args:
            actual_url = actual_args[0]
        else:
            actual_url = mock_get.call_args.kwargs["url"]
        assert actual_url == expected_url
        mock_get.assert_called_once()

    @patch("src.jupiter_api.requests.get")
    def test_get_order_history_network_error_handling(
        self, mock_get, dummy_wallet
    ):
        mock_get.side_effect = requests.exceptions.RequestException(
            "Network error"
        )

        with pytest.raises(Exception) as exc_info:
            self.api.get_order_history(wallet=dummy_wallet)
        assert "Network error" in str(exc_info.value)
        mock_get.assert_called_once()

    @patch("src.jupiter_api.requests.get")
    def test_get_order_history_success_response_parsing(
        self, mock_get, dummy_wallet
    ):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_GET_ORDER_HISTORY_PAGE_2
        mock_get.return_value = mock_response

        result = self.api.get_order_history(wallet=dummy_wallet)

        orders_list = MOCK_GET_ORDER_HISTORY_PAGE_2.get("orders", [])
        assert isinstance(result, list)
        assert len(result) == len(orders_list)
        if orders_list:
            assert result[0].orderKey == orders_list[0]["orderKey"]
        mock_get.assert_called_once()

    @patch("src.jupiter_api.requests.get")
    def test_get_order_history_non_json_error_response(
        self, mock_get, dummy_wallet
    ):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("No JSON")
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            self.api.get_order_history(wallet=dummy_wallet)
        assert "Invalid JSON response" in str(exc_info.value)
        assert "Internal Server Error" in str(exc_info.value)
        mock_get.assert_called_once()


class TestGetOpenOrders(TestBase):
    @patch("src.jupiter_api.requests.get")
    def test_get_open_orders_success(self, mock_get, dummy_wallet):
        orders_data = MOCK_GET_OPEN_ORDERS
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = orders_data
        mock_get.return_value = mock_response

        result = self.api.get_open_orders(wallet=dummy_wallet)

        assert isinstance(result, list)
        assert len(result) == len(orders_data)

        if orders_data and "publicKey" in orders_data[0]:
            assert result[0].publicKey == orders_data[0]["publicKey"]
        mock_get.assert_called_once()

    @patch("src.jupiter_api.requests.get")
    def test_get_open_orders_failure(self, mock_get, dummy_wallet):
        error_data = {"error": "Invalid wallet address"}
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "400 Client Error"
        )
        mock_response.json.return_value = error_data
        mock_get.return_value = mock_response

        with pytest.raises(Exception):
            self.api.get_open_orders(wallet=dummy_wallet)
        mock_get.assert_called_once()

    @patch("src.jupiter_api.requests.get")
    def test_get_open_orders_empty_response(self, mock_get, dummy_wallet):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = self.api.get_open_orders(wallet=dummy_wallet)

        assert result == []
        mock_get.assert_called_once()

    @patch("src.jupiter_api.requests.get")
    def test_get_open_orders_unexpected_response_structure(
        self, mock_get, dummy_wallet
    ):
        unexpected_response = {"unexpected": "data"}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = unexpected_response
        mock_get.return_value = mock_response

        result = self.api.get_open_orders(wallet=dummy_wallet)
        assert result == []
        mock_get.assert_called_once()

    @patch("src.jupiter_api.requests.get")
    def test_get_open_orders_payload_integrity(self, mock_get, dummy_wallet):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        self.api.get_open_orders(wallet=dummy_wallet)

        params = mock_get.call_args.kwargs.get("params", {})
        assert params["wallet"] == dummy_wallet.address
        mock_get.assert_called_once()

    @patch("src.jupiter_api.requests.get")
    def test_get_open_orders_correct_endpoint_url_and_http_method(
        self, mock_get, dummy_wallet
    ):
        expected_url = "https://api.jup.ag/limit/v2/openOrders"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        self.api.get_open_orders(wallet=dummy_wallet)

        actual_args = mock_get.call_args[0]
        if actual_args:
            actual_url = actual_args[0]
        else:
            actual_url = mock_get.call_args.kwargs["url"]
        assert actual_url == expected_url
        mock_get.assert_called_once()

    @patch("src.jupiter_api.requests.get")
    def test_get_open_orders_network_error_handling(
        self, mock_get, dummy_wallet
    ):
        mock_get.side_effect = requests.exceptions.RequestException(
            "Network error"
        )

        with pytest.raises(Exception) as exc_info:
            self.api.get_open_orders(wallet=dummy_wallet)
        assert "Network error" in str(exc_info.value)
        mock_get.assert_called_once()

    @patch("src.jupiter_api.requests.get")
    def test_get_open_orders_success_response_parsing(
        self, mock_get, dummy_wallet
    ):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("No JSON")
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            self.api.get_open_orders(wallet=dummy_wallet)
        assert (
            "Internal Server Error" in str(exc_info.value)
            or "No JSON" in str(exc_info.value)
        )
        mock_get.assert_called_once()

    @patch("src.jupiter_api.requests.get")
    def test_get_open_orders_non_json_error_response(
        self, mock_get, dummy_wallet
    ):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("No JSON")
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            self.api.get_open_orders(wallet=dummy_wallet)
        assert "Invalid JSON response" in str(exc_info.value)
        assert "Internal Server Error" in str(exc_info.value)
        mock_get.assert_called_once()
