import requests
from newsapi import NewsApiClient
from datetime import datetime,timedelta
from twilio.rest import Client
import json


with open ("credentials.json", mode= "r") as file :
    data = json.load(file)


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
newsapi = NewsApiClient(api_key= data["news_api"])
account_sid = data["account_sid"]
auth_token = data["auth_token"]

parameters = {
    "function" : "TIME_SERIES_DAILY",
    "symbol" : STOCK,
    "apikey" : data["alpha_key"]   
}

# Get stock data for yesterday and the day before
response = requests.get("https://www.alphavantage.co/query", params= parameters)
response.raise_for_status()
stock_data = response.json()
daily_stock = [val for (key, val) in stock_data["Time Series (Daily)"].items()]
yesterday_closing_price = float(daily_stock[0]["4. close"])
day_before_yesterday_closing_price = float(daily_stock[1]["4. close"])
difference = (yesterday_closing_price - day_before_yesterday_closing_price)
diff_percentage = round(abs(difference / yesterday_closing_price) * 100)


if diff_percentage >= 5 :

    today = datetime.now().date()
    start_date = today - timedelta(2)

    # /v2/top-headlines
    news_data = newsapi.get_everything(q= COMPANY_NAME ,
                                        from_param= start_date,
                                        to= today,
                                        language="en",
                                        sort_by="relevancy",
                                        page=1)


    articles_list =  news_data["articles"][:2]
   

    if difference > 0 : 
        stock_change = f"{STOCK}: 🔺 {diff_percentage}%"
    else :
        stock_change = f"{STOCK}: 🔻 {diff_percentage}%"
    # send 2 smses with stock difference and 2 news headlines + description
    for i in range (len(articles_list)) :
        headline = articles_list[i]["title"]
        brief = articles_list[i]["description"]
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=f"\n{stock_change}\nHeadline: {headline}.\nBrief: {brief}.",
            from_= data["sender"],
            to= data["receiver"],
        )
        print(message.status)
    
    



