import json
import urllib.parse
import urllib.request
from typing import List, Optional

from . import data

PUBLIC_FIELDS = ("id", "name", "category", "price", "tags")


# --- tools (each one belongs to an agent / knowledge base shown in the UI) ---

def search_catalog(query: str = "", category: Optional[str] = None, max_price: Optional[float] = None):
    words = [w.rstrip("s") for w in query.lower().split() if len(w) > 2]
    hits = []
    for p in data.PRODUCTS:
        if (category and p["category"] != category) or (max_price is not None and p["price"] > max_price):
            continue
        text = " ".join([p["name"], p["category"], *p["tags"]]).lower()
        score = sum(w in text for w in words)
        if score or not words:
            hits.append((score, {k: p[k] for k in PUBLIC_FIELDS}))
    hits.sort(key=lambda h: -h[0])
    return [p for _, p in hits[:10]]


def get_fashion_trends():
    return data.FASHION_TRENDS


def get_order_history():
    return data.ORDER_HISTORY.get(data.CUSTOMER_ID, {})


def get_customer_reviews(product_ids: List[str]):
    return {pid: data.REVIEWS.get(pid, []) for pid in product_ids}


def check_inventory(product_ids: List[str]):
    stock = {p["id"]: p["stock"] for p in data.PRODUCTS}
    return {pid: stock.get(pid, "unknown product") for pid in product_ids}


def get_weather(city: str):
    def fetch(url, **params):
        with urllib.request.urlopen(f"{url}?{urllib.parse.urlencode(params)}", timeout=10) as r:
            return json.load(r)

    geo = fetch("https://geocoding-api.open-meteo.com/v1/search", name=city, count=1).get("results")
    if not geo:
        return {"error": f"unknown city {city}"}
    g = geo[0]
    d = fetch(
        "https://api.open-meteo.com/v1/forecast", latitude=g["latitude"], longitude=g["longitude"], timezone="auto",
        daily="temperature_2m_max,temperature_2m_min,precipitation_probability_max",
    )["daily"]
    days = zip(d["time"], d["temperature_2m_min"], d["temperature_2m_max"], d["precipitation_probability_max"])
    return {
        "location": f"{g['name']}, {g.get('country', '')}",
        "forecast": [{"date": t, "min_c": lo, "max_c": hi, "rain_chance_pct": rain} for t, lo, hi, rain in days],
    }


def fn(name, description, properties=None, required=()):
    params = {"type": "object", "properties": properties or {}, "required": list(required)}
    return {"type": "function", "function": {"name": name, "description": description, "parameters": params}}


IDS = {"type": "array", "items": {"type": "string"}}
TOOLS = [
    fn("search_catalog", "Search the store's product catalog (private). Returns at most 10 products.", {
        "query": {"type": "string", "description": "keywords, e.g. 'business wool navy'"},
        "category": {"type": "string", "enum": ["top", "bottom", "dress", "outerwear", "shoes", "accessory"]},
        "max_price": {"type": "number"},
    }),
    fn("get_fashion_trends", "Current fashion trends (public data)."),
    fn("get_order_history", "The customer's past orders, returns and preferences (private)."),
    fn("get_customer_reviews", "Customer reviews for products (private).", {"product_ids": IDS}, ["product_ids"]),
    fn("check_inventory", "Units in stock per product. 0 means unavailable.", {"product_ids": IDS}, ["product_ids"]),
    fn("get_weather", "7-day weather forecast for a city.", {"city": {"type": "string"}}, ["city"]),
]
FUNCS = {f.__name__: f for f in [search_catalog, get_fashion_trends, get_order_history, get_customer_reviews, check_inventory, get_weather]}
# tool -> (agent, knowledge base) highlighted in the UI
UI = {
    "search_catalog": ("catalog", "catalog"),
    "get_fashion_trends": ("catalog", "trends"),
    "get_order_history": ("inventory", "orders"),
    "get_customer_reviews": ("catalog", "reviews"),
    "check_inventory": ("inventory", None),
    "get_weather": ("weather", None),
}
