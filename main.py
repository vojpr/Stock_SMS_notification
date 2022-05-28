import requests
import html
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()


def get_change(current, previous):
    try:
        return ((current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return 0


def send_sms(up_down, price_difference, article_list):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    for article in article_list:
        client = Client(account_sid, auth_token)
        message = client.messages \
            .create(
                body=f"TSLA: {up_down}{abs(price_difference)}%{up_down}\n{article}",
                from_=os.getenv('TWILIO_NUMBER'),
                to=os.getenv('PHONE_NUMBER')
            )


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

# Stock API
stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": os.getenv('STOCK_API_KEY'),
}

stock_response = requests.get("https://www.alphavantage.co/query", stock_parameters)
stock_response.raise_for_status()
stock_data = stock_response.json()["Time Series (Daily)"]
yesterday = list(stock_data.keys())[0]
yesterday_close = float(stock_data[yesterday]["4. close"])
before_yesterday = list(stock_data.keys())[1]
before_yesterday_close = float(stock_data[before_yesterday]["4. close"])
price_difference = get_change(yesterday_close, before_yesterday_close)
price_difference = round(price_difference, 2)

# News API
news_parameters = {
    "q": "tesla",
    "from": yesterday,
    "apiKey": os.getenv('NEWS_API_KEY'),
    "language": "en",
    "sortBy": "popularity",
    "searchIn": "title"
}
news_response = requests.get("https://newsapi.org/v2/everything?", news_parameters)
news_response.raise_for_status()
news_data = news_response.json()["articles"]
news_data = news_data[:3]

article_list = [f"Headline: {html.unescape(article['title'])}\nBrief: {html.unescape(article['description'])}" for
                article in news_data]

if price_difference <= -5:
    send_sms("🔻", price_difference, article_list)
if price_difference >= 5:
    send_sms("🔺", price_difference, article_list)
