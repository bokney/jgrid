
import pytest
from unittest.mock import patch, MagicMock
from src.dexscreener_api import DEXScreenerAPI


@pytest.fixture
def sample_response():
    return [{
        "chainId": "solana",
        "dexId": "raydium",
        "url": (
            "https://dexscreener_api.com/solana/"
            "8slbnzoa1cfnvmjlpfp98zlanfsycfapfjkmbixnlwxj"
        ),
        "pairAddress": "8sLbNZoA1cfnvMJLPfp98ZLAnFSYCFApfJKMbiXNLwxj",
        "labels": ["CLMM"],
        "baseToken": {
            "address": "So11111111111111111111111111111111111111112",
            "name": "Wrapped SOL",
            "symbol": "SOL",
        },
        "quoteToken": {
            "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "name": "USD Coin",
            "symbol": "USDC",
        },
        "priceNative": "146.4843",
        "priceUsd": "146.48",
        "txns": {
            "m5": {"buys": 324, "sells": 635},
            "h1": {"buys": 7319, "sells": 8892},
            "h6": {"buys": 28468, "sells": 34996},
            "h24": {"buys": 114957, "sells": 122091},
        },
        "volume": {
            "h24": 45572877.43,
            "h6": 14726348.08,
            "h1": 4123911.04,
            "m5": 149928.1,
        },
        "priceChange": {"m5": 0.51, "h1": 2.1, "h6": 11.42, "h24": 5.69},
        "liquidity": {
            "usd": 3821675.21,
            "base": 22977,
            "quote": 455767,
        },
        "pairCreatedAt": 1723699294000,
    },
    {
        "chainId": "solana",
        "dexId": "raydium",
        "url": (
            "https://dexscreener_api.com/solana/"
            "bztgqeys6exuxicyphecyq7pybqodxqmvkjubp4r8muu"
        ),
        "pairAddress": "BZtgQEyS6eXUXicYPHecYQ7PybqodXQMvkjUbP4R8mUU",
        "labels": ["CLMM"],
        "baseToken": {
            "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "name": "USD Coin",
            "symbol": "USDC",
        },
        "quoteToken": {
            "address": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
            "name": "USDT",
            "symbol": "USDT",
        },
        "priceNative": "1.0004228",
        "priceUsd": "1.00042",
        "txns": {
            "m5": {"buys": 6, "sells": 11},
            "h1": {"buys": 157, "sells": 370},
            "h6": {"buys": 1052, "sells": 1678},
            "h24": {"buys": 3692, "sells": 4974},
        },
        "volume": {
            "h24": 41679649.97,
            "h6": 16302252.4,
            "h1": 3051322.55,
            "m5": 142767.49,
        },
        "priceChange": {"h1": -0.03, "h6": -0.04, "h24": -0.04},
        "liquidity": {
            "usd": 6178266.53,
            "base": 2583973,
            "quote": 3593200,
        },
        "fdv": 9439665853,
        "marketCap": 55524326555,
        "pairCreatedAt": 1723699296000,
        "info": {
            "imageUrl": (
                "https://dd.dexscreener_api.com/ds-data/tokens/solana/"
                "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v.png"
                "?key=d2dc50"
            ),
            "header": (
                "https://dd.dexscreener_api.com/ds-data/tokens/solana/"
                "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v/header.png"
                "?key=d2dc50"
            ),
            "openGraph": (
                "https://cdn.dexscreener_api.com/token-images/og/solana/"
                "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
                "?timestamp=1740756300000"
            ),
            "websites": [],
            "socials": [],
        },
    }]


@pytest.fixture
def api():
    return DEXScreenerAPI()


class TestDEXScreenerAPI:
    @patch("src.backoff.sleep", return_value=None)
    @patch("src.dexscreener_api.requests.get")
    def test_get_token_info_success(
        self, mock_get, sleep_mock, sample_response, api
    ):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_response
        mock_get.return_value = mock_response
        result = api.get_token_info(
            "So11111111111111111111111111111111111111112"
        )
        assert result == {"name": "Wrapped SOL", "symbol": "SOL"}

    @patch("src.backoff.sleep", return_value=None)
    @patch("src.dexscreener_api.requests.get")
    def test_get_token_info_http_error(
        self, mock_get, sleep_mock
    ):
        api = DEXScreenerAPI()
        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_get.return_value = mock_response
        token_address = "invalid_address"

        with pytest.raises(
            Exception,
            match="404 Not Found"
        ):
            api.get_token_info(token_address)

    @patch("src.backoff.sleep", return_value=None)
    @patch("src.dexscreener_api.requests.get")
    def test_get_token_info_url_construction(
        self, mock_get, sleep_mock, sample_response
    ):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = sample_response
        mock_get.return_value = mock_response

        api = DEXScreenerAPI()
        api.get_token_info("ExampleTokenAddress")

        expected_url = (
            "https://api.dexscreener.com/tokens"
            "/v1/solana/ExampleTokenAddress"
        )
        mock_get.assert_called_with(url=expected_url)
