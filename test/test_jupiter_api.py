
import pytest
from decimal import Decimal
from solders.keypair import Keypair
from unittest.mock import patch, MagicMock
from src.jupiter_api import JupiterLimitOrderAPI


class TestBase:
    @pytest.fixture(autouse=True)
    def setup_api(self):
        self.api = JupiterLimitOrderAPI()

    @pytest.fixture
    def mock_wallet(self):
        wallet = MagicMock()
        wallet.__str__.return_value = "mock_wallet_address"
        return wallet

    @pytest.fixture
    def mock_response(self):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"order": "test_order_id"}
        return response


class TestCreateLimitOrder(TestBase):
    @pytest.mark.skip
    def test_create_limit_order_success(self):
        pass

    @pytest.mark.skip
    def test_create_limit_order_failure(self):
        pass

    @pytest.mark.skip
    def test_create_limit_order_optional_parameters(self):
        pass

    @pytest.mark.skip
    def test_create_limit_order_excludes_optional_flags_when_false(self):
        pass

    @patch("requests.post")
    def test_create_limit_order_payload_integrity(
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
            takingAmount=Decimal("200")
        )

        mock_post.assert_called_once()
        actual_payload = mock_post.call_args.kwargs["json"]
        assert actual_payload == expected_payload

    @patch("requests.post")
    def test_create_limit_order_correct_endpoint_url_and_http_method(
        self, mock_post, mock_wallet, mock_response
    ):
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

    @pytest.mark.skip
    def test_create_limit_order_network_error_handling(self):
        pass

    @pytest.mark.skip
    def test_create_limit_order_success_response_parsing(self):
        pass

    @pytest.mark.skip
    def test_create_limit_order_non_json_error_response(self):
        pass

    @pytest.mark.skip
    def test_create_limit_order_logger_output(self):
        pass


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
