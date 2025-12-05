import os

from django.test import TestCase
import requests
from dotenv import load_dotenv

from apps.core.helpers import convert_currency


def test_API():
    load_dotenv()
    API_KEY = os.environ.get("API_KEY")
    # Create your tests here.
    url = "http://api.exchangerate.host/live"
    params = {
        "access_key": API_KEY,
        "source": "GBP",
        "currencies": "USD,AUD,CAD,PLN,MXN",
        "format": 1
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        print("Live exchange rates:", data)
    else:
        print("Error:", response.status_code, response.text)


class CurrencyConversionTest(TestCase):
    def test_conversion(self):
        amounts = [100, 50, 200]
        from_currencies = ["USD", "AUD", "CAD"]
        to_currency = "GBP"
        result = convert_currency(amounts, from_currencies, to_currency)
        self.assertEqual(len(result), len(amounts))