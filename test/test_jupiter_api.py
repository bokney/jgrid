
import pytest
import requests
from decimal import Decimal
from unittest.mock import patch, MagicMock
from src.jupiter_api import JupiterLimitOrderAPI


class TestBase:
    @pytest.fixture(autouse=True)
    def setup_api(self):
        self.api = JupiterLimitOrderAPI()
        self.api._logger = MagicMock()

    @pytest.fixture
    def mock_wallet(self):
        wallet = MagicMock()
        wallet.__str__.return_value = "mock_wallet_address"
        return wallet
    
    @pytest.fixture
    def mock_response(self):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "order": "test_order_id",
            "tx": "a_transaction"
        }
        return response


class TestCreateLimitOrder(TestBase):
    @patch("requests.post")
    def test_create_limit_order_success(
        self, mock_post, mock_wallet, mock_response
    ):
        mock_post.return_value = mock_response

        result = self.api.create_limit_order(
            wallet=mock_wallet,
            inputMint="input_mint",
            outputMint="output_mint",
            maker="maker_address",
            payer="payer_address",
            makingAmount=Decimal("100"),
            takingAmount=Decimal("200")
        )

        assert result == {
            "order": "test_order_id",
            "tx": "a_transaction"
        }

    @patch("requests.post")
    def test_create_limit_order_failure(
        self, mock_post, mock_wallet
    ):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid order parameters"}
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            self.api.create_limit_order(
                wallet=mock_wallet,
                inputMint="input_mint",
                outputMint="output_mint",
                maker="maker_address",
                payer="payer_address",
                makingAmount=Decimal("100"),
                takingAmount=Decimal("200")
            )

        assert "Invalid order parameters" in str(exc_info.value)
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_create_limit_order_optional_parameters(
        self, mock_post, mock_wallet, mock_response
    ):
        expected_payload = {
            "wallet": "mock_wallet_address",
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

        mock_post.return_value = mock_response

        self.api.create_limit_order(
            wallet=mock_wallet,
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

    @patch("requests.post")
    def test_create_limit_order_excludes_optional_flags_when_false(
        self, mock_post, mock_wallet, mock_response
    ):
        expected_payload = {
            "wallet": "mock_wallet_address",
            "inputMint": "input_mint",
            "outputMint": "output_mint",
            "maker": "maker_address",
            "payer": "payer_address",
            "params": {
                "makingAmount": "100",
                "takingAmount": "200"
            }
        }

        mock_post.return_value = mock_response

        self.api.create_limit_order(
            wallet=mock_wallet,
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

    @patch("requests.post")
    def test_create_limit_order_correct_endpoint_url(self, mock_post, mock_wallet, mock_response):
        expected_url = "https://api.jup.ag/limit/v2/createOrder"
        mock_post.return_value = mock_response

        self.api.create_limit_order(
            wallet=mock_wallet,
            inputMint="input_mint",
            outputMint="output_mint",
            maker="maker_address",
            payer="payer_address",
            makingAmount=Decimal("100"),
            takingAmount=Decimal("200")
        )

        mock_post.assert_called_once()
        actual_url = mock_post.call_args.kwargs["url"]
        assert actual_url == expected_url

    @patch("requests.post")
    def test_create_limit_order_correct_http_method(self, mock_post, mock_wallet, mock_response):
        mock_post.return_value = mock_response

        self.api.create_limit_order(
            wallet=mock_wallet,
            inputMint="input_mint",
            outputMint="output_mint",
            maker="maker_address",
            payer="payer_address",
            makingAmount=Decimal("100"),
            takingAmount=Decimal("200")
        )

        mock_post.assert_called_once()

    @patch("requests.post")
    def test_create_limit_order_network_error_handling(
        self, mock_post, mock_wallet
    ):
        mock_post.side_effect = requests.exceptions.RequestException(
            "Network error"
        )

        with pytest.raises(Exception) as exc_info:
            self.api.create_limit_order(
                wallet=mock_wallet,
                inputMint="input_mint",
                outputMint="output_mint",
                maker="maker_address",
                payer="payer_address",
                makingAmount=Decimal("100"),
                takingAmount=Decimal("200")
            )

        assert "Network error" in str(exc_info.value)
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_create_limit_order_success_response_parsing(
        self, mock_post, mock_wallet
    ):
        expected_response = {
            "order": "test_order_id",
            "tx": "some_transaction_data"
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_response
        mock_post.return_value = mock_response

        result = self.api.create_limit_order(
            wallet=mock_wallet,
            inputMint="input_mint",
            outputMint="output_mint",
            maker="maker_address",
            payer="payer_address",
            makingAmount=Decimal("100"),
            takingAmount=Decimal("200")
        )

        assert result == expected_response

        mock_post.assert_called_once()

    @patch("requests.post")
    def test_create_limit_order_non_json_error_response(
        self, mock_post, mock_wallet
    ):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("No JSON")
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            self.api.create_limit_order(
                wallet=mock_wallet,
                inputMint="input_mint",
                outputMint="output_mint",
                maker="maker_address",
                payer="payer_address",
                makingAmount=Decimal("100"),
                takingAmount=Decimal("200")
            )
        
        assert "Internal Server Error" in str(exc_info.value)
        mock_post.assert_called_once()

    @patch("requests.post")
    @patch("src.jupiter_api.get_logger")
    def test_create_limit_order_logger_output(
        self, mock_get_logger, mock_post, mock_wallet
    ):
        mock_logger = self.api._logger

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "order": "test_order_id", "tx": "a_transaction"
        }
        mock_post.return_value = mock_response

        expected_log_message = str({
            "wallet": "mock_wallet_address",
            "inputMint": "input_mint",
            "outputMint": "output_mint",
            "maker": "maker_address",
            "payer": "payer_address",
            "params": {"makingAmount": "100", "takingAmount": "200"}
        })

        self.api.create_limit_order(
            wallet=mock_wallet,
            inputMint="input_mint",
            outputMint="output_mint",
            maker="maker_address",
            payer="payer_address",
            makingAmount=Decimal("100"),
            takingAmount=Decimal("200")
        )

        mock_logger.debug.assert_any_call("Posting jupiter limit order:")
        mock_logger.debug.assert_any_call(expected_log_message)

        mock_post.assert_called_once()


class TestCancelOrders:
    @pytest.mark.skip
    def test_cancel_orders_success(self):
        pass

    @pytest.mark.skip
    def test_cancel_orders_failure(self):
        pass

    @pytest.mark.skip
    def test_cancel_orders_without_optional_params(self):
        pass

    @pytest.mark.skip
    def test_cancel_orders_payload_integrity(self):
        pass

    @pytest.mark.skip
    def test_cancel_orders_correct_endpoint_url_and_http_method(self):
        pass

    @pytest.mark.skip
    def test_cancel_orders_network_error_handling(self):
        pass

    @pytest.mark.skip
    def test_cancel_orders_success_response_parsing(self):
        pass

    @pytest.mark.skip
    def test_cancel_orders_non_json_error_response(self):
        pass

    @pytest.mark.skip
    def test_cancel_orders_logger_output(self):
        pass


class TestGetOrderHistory:
    @pytest.mark.skip
    def test_get_order_history_success(self):
        pass

    @pytest.mark.skip
    def test_get_order_history_failure(self):
        pass

    @pytest.mark.skip
    def test_get_order_history_page_success(self):
        pass

    @pytest.mark.skip
    def test_get_order_history_page_failure(self):
        # what happens when trying to access a page out of bounds?
        pass

    @pytest.mark.skip
    def test_get_order_history_payload_integrity(self):
        pass

    @pytest.mark.skip
    def test_get_order_history_correct_endpoint_url_and_http_method(self):
        pass

    @pytest.mark.skip
    def test_get_order_history_network_error_handling(self):
        pass

    @pytest.mark.skip
    def test_get_order_history_success_response_parsing(self):
        pass

    @pytest.mark.skip
    def test_get_order_history_non_json_error_response(self):
        pass

    @pytest.mark.skip
    def test_get_order_history_logger_output(self):
        pass


class TestGetOpenOrders:
    @pytest.mark.skip
    def test_get_open_orders_success(self):
        pass

    @pytest.mark.skip
    def test_get_open_orders_failure(self):
        pass

    @pytest.mark.skip
    def test_get_open_orders_empty_response(self):
        # what happens when there are no open orders?
        # is it None or an empty list?
        pass

    @pytest.mark.skip
    def test_get_open_orders_unexpected_response_structure(self):
        pass

    @pytest.mark.skip
    def test_get_open_orders_payload_integrity(self):
        pass

    @pytest.mark.skip
    def test_get_open_orders_correct_endpoint_url_and_http_method(self):
        pass

    @pytest.mark.skip
    def test_get_open_orders_network_error_handling(self):
        pass

    @pytest.mark.skip
    def test_get_open_orders_success_response_parsing(self):
        pass

    @pytest.mark.skip
    def test_get_open_orders_non_json_error_response(self):
        pass

    @pytest.mark.skip
    def test_get_open_orders_logger_output(self):
        pass
