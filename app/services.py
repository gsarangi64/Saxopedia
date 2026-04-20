#!usr/bin/env python3
import requests
import time
from urllib.parse import quote

# Cnfig

REPERTOIRE_URL = "https://raw.githubusercontent.com/gsarangi64/sax-repertoire-data/main/sax_repertoire.json"
OPENOPUS_BASE_URL = "https://api.openopus.org/composer/list/search/"

CACHE_DURATION = 300  # seconds (5 minutes)

# Cache storage

_cache = {
    "repertoire": {
        "data": None,
        "last_fetch": 0
    },
    "composers": {}
}

# sax-repertoire (GitHub JSON)

def load_repertoire():
    current_time = time.time()

    # Return cached if still valid
    if (_cache["repertoire"]["data"] and
        current_time - _cache["repertoire"]["last_fetch"] < CACHE_DURATION):
        return _cache["repertoire"]["data"]

    print("Fetching repertoire from GitHub...")

    try:
        response = requests.get(REPERTOIRE_URL)
        data = response.json()

        _cache["repertoire"]["data"] = data
        _cache["repertoire"]["last_fetch"] = current_time

        return data

    except Exception as e:
        print(f"Error loading repertoire: {e}")
        return []

# OpenOpus (single composer)

def fetch_composer(name):
    cleaned_name = quote(name)
    url = f"{OPENOPUS_BASE_URL}{cleaned_name}.json"

    print(f"Fetching composer from: {url}")

    try:
        response = requests.get(url, timeout=5)

        # Check for bad status (like 504)
        if response.status_code != 200:
            print(f"API error: {response.status_code}")
            return None

        data = response.json()

        if data.get("status", {}).get("success") == "true" and data.get("composers"):
            return data["composers"][0]

        return None

    except requests.exceptions.Timeout:
        print("Request timed out")
        return None

    except Exception as e:
        print(f"Error fetching composer: {e}")
        return None

# OpenOpus (search multiple)

def search_composers(name):
    cleaned_name = quote(name)
    url = f"{OPENOPUS_BASE_URL}{cleaned_name}.json"

    print(f"Searching composers from: {url}")

    try:
        response = requests.get(url)
        data = response.json()

        if data.get("status", {}).get("success") == "true":
            return data.get("composers", [])
        else:
            return []

    except Exception as e:
        print(f"Error searching composers {name}: {e}")
        return []