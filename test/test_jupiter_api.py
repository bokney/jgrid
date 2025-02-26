
import pytest
from src.jupiter_api import JupiterLimitOrderAPI


class TestBase:
    @pytest.fixture(autouse=True)
    def setup_api(self):
        self.api = JupiterLimitOrderAPI()


class TestCreateOrder:
    def test_create_order_success(self):
        pass

    def test_create_order_failure(self):
        pass

    def test_create_order_optional_parameters(self):
        pass

    def test_create_order_excludes_optional_flags_when_false(self):
        pass

    def test_create_order_payload_integrity(self):
        pass

    def test_create_order_correct_endpoint_url(self):
        pass

    def test_create_order_correct_http_method(self):
        pass

    def test_create_order_network_error_handling(self):
        pass

    def test_create_order_success_response_parsing(self):
        pass

    def test_create_order_non_json_error_response(self):
        pass

    def test_create_order_logger_output(self):
        pass


class TestCancelOrders:
    def test_cancel_orders_success(self):
        pass

    def test_cancel_orders_failure(self):
        pass

    def test_cancel_orders_without_optional_params(self):
        pass

    def test_cancel_orders_payload_integrity(self):
        pass

    def test_cancel_orders_correct_endpoint_url(self):
        pass

    def test_cancel_orders_correct_http_method(self):
        pass

    def test_cancel_orders_network_error_handling(self):
        pass

    def test_cancel_orders_success_response_parsing(self):
        pass

    def test_cancel_orders_non_json_error_response(self):
        pass

    def test_cancel_orders_logger_output(self):
        pass


class TestGetOrderHistory:
    def test_get_order_history_success(self):
        pass

    def test_get_order_history_failure(self):
        pass

    def test_get_order_history_page_success(self):
        pass

    def test_get_order_history_page_failure(self):
        # what happens when trying to access a page out of bounds?
        pass

    def test_get_order_history_payload_integrity(self):
        pass

    def test_get_order_history_correct_endpoint_url(self):
        pass

    def test_get_order_history_correct_http_method(self):
        pass

    def test_get_order_history_network_error_handling(self):
        pass

    def test_get_order_history_success_response_parsing(self):
        pass

    def test_get_order_history_non_json_error_response(self):
        pass

    def test_get_order_history_logger_output(self):
        pass


class TestGetOpenOrders:
    def test_get_open_orders_success(self):
        pass

    def test_get_open_orders_failure(self):
        pass

    def test_get_open_orders_empty_response(self):
        # what happens when there are no open orders?
        # is it None or an empty list?
        pass

    def test_get_open_orders_unexpected_response_structure(self):
        pass

    def test_get_open_orders_payload_integrity(self):
        pass

    def test_get_open_orders_correct_endpoint_url(self):
        pass

    def test_get_open_orders_correct_http_method(self):
        pass

    def test_get_open_orders_network_error_handling(self):
        pass

    def test_get_open_orders_success_response_parsing(self):
        pass

    def test_get_open_orders_non_json_error_response(self):
        pass

    def test_get_open_orders_logger_output(self):
        pass
