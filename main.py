import json
import time
import os
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import requests
from selenium import webdriver

load_dotenv()  # Automatically loads the .env file

# Load configuration
CONFIG_FILE = "./config.json"
STATE_FILE = "./alert_state.json"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def send_email(subject, body, recipient_email=os.getenv("RECIPIENT_EMAIL")):
    sender_email = os.getenv("SENDER_EMAIL")  # Replace with your email
    sender_password = os.getenv("SENDER_PASSWORD")        # Replace with your password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

def fetch_price(url, price_tag_id=None, price_tag_class=None):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("start-maximized")

        driver = webdriver.Chrome(options=options)
        driver.get(url)

        html_content = driver.page_source
        driver.quit()

        soup = BeautifulSoup(html_content, 'html.parser')

        if price_tag_id:
            price_tag = soup.find(id=price_tag_id)
        elif price_tag_class:
            price_tag = soup.find(class_=price_tag_class)
        else:
            return None

        if price_tag:
            price_text = price_tag.get_text(strip=True).replace(',', '').replace('€', '')
            return float(price_text)
    except Exception as e:
        print(f"Error fetching price from {url}: {e}")
    return None

def main():
    #Load configuration and state
    config = load_config()
    state = load_state()

    rerun_interval = config.get("rerunIntervalHours", 8) * 3600
    items = config.get("items", [])

    while True:
        #Iterate items list
        for item in items:

            #Extract items data
            name = item["name"]
            url = item["websiteLink"]
            price_below_alert = float(item["priceBelowAlert"])
            price_tag_id = item.get("priceTagId")
            price_tag_class = item.get("priceTagClass")

            #Get price from web
            price = fetch_price(url, price_tag_id, price_tag_class)

            if price is None:
                print(f"Failed to fetch price for {name} ({url})")
                continue

            print(f"Current price for '{name}' is {price} EUR")

            if name not in state:
                state[name] = {"last_price": price, "alert_sent": False}

            last_price = state[name]["last_price"]
            alert_sent = state[name]["alert_sent"]

            if price < price_below_alert and not alert_sent:
                drop_amount = last_price - price
                subject = f"Price Alert: {name}"
                body = (f"The price for '{name}' has dropped to {price} EUR.\n\n"
                        f"Price drop: {drop_amount} EUR\n"
                        f"Link: {url}")
                send_email(subject, body)
                print(f"Alert sent for {name}!")
                state[name] = {"last_price": price, "alert_sent": True}

            elif price >= price_below_alert and alert_sent:
                print(f"Price for {name} has risen above the threshold. Resetting alert state.")
                state[name] = {"last_price": price, "alert_sent": False}

            else:
                state[name]["last_price"] = price

        save_state(state)
        print(f"Waiting for {rerun_interval / 3600} hours before the next check.")

        time.sleep(rerun_interval)

if __name__ == "__main__":
    main()
