import logging
from typing import List
import requests
import pandas as pd
from bs4 import BeautifulSoup

def extract(max_pages=50) -> pd.DataFrame:
    logging.info("Starting data extraction...")

    base_url = "https://fashion-studio.dicoding.dev"
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    all_data: List[dict] = []

    for page in range(1, max_pages + 1):
        url = base_url if page == 1 else f"{base_url}/page{page}"
        logging.info(f"Extracting data from {url}")

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 404:
                logging.warning(f"Failed to retrieve page {page}: 404")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.find_all(class_="collection-card")

            for card in cards:
                data = parse_product_card(card)
                all_data.append(data)


        except requests.exceptions.RequestException as e:
             logging.error(f"Request error on page {page}: {e}")
            

    if not all_data:
        logging.error("No data was extracted. Exiting...")
        return pd.DataFrame()

    return pd.DataFrame(all_data)

def parse_product_card(card) -> dict:
    title = card.find(class_="product-title")
    price = card.find(class_="price")
    img_tag = card.find("img")
    details = card.find_all("p")

    data = {
        "Title": title.text.strip() if title else "Unknown",
        "Price": price.text.strip() if price else "N/A",
        "Image URL": img_tag["src"] if img_tag else None,
        "Rating": None,
        "Colors": None,
        "Size": None,
        "Gender": None,
        "Timestamp": pd.Timestamp.now()
    }

    for p in details:
        text = p.text.strip()
        if "Rating:" in text:
            data["Rating"] = text.replace("Rating:", "").strip()
        elif "Colors" in text:
            data["Colors"] = text.replace("Colors", "").strip()
        elif "Size:" in text:
            data["Size"] = text.replace("Size:", "").strip()
        elif "Gender:" in text:
            data["Gender"] = text.replace("Gender:", "").strip()

    return data


