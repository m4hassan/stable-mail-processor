import logging

import requests

from config import STABLE_API_KEY, STABLE_API_URL

logger = logging.getLogger(__name__)


def fetch_mail_items(status="completed"):
    URL = f"{STABLE_API_URL}/v1/mail-items"
    headers = {"accept": "application/json", "x-api-key": STABLE_API_KEY}
    params = {"scan.status": status, "first": 50}  # Fetch 50 items per request
    all_items = []

    print("Starting mail items fetch...")

    while True:
        print(f"Fetching mail items with params: {params}")
        response = requests.get(URL, headers=headers, params=params)

        if response.status_code != 200:
            print(
                f"Error fetching mail items: {response.status_code} - {response.text}"
            )
            return all_items

        data = response.json()
        fetched_items = data.get("edges", [])
        all_items.extend(fetched_items)
        print(f"Fetched {len(fetched_items)} items, total so far: {len(all_items)}")

        page_info = data.get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            print("No more pages left to fetch.")
            break  # Stop if there are no more pages

        params["after"] = page_info.get("endCursor")  # Move to the next page
        print(f"Moving to next page with cursor: {params['after']}")

    print(f"Completed fetching mail items. Total items retrieved: {len(all_items)}")
    return all_items


def extract_recipient_name(mail_item):
    """
    Extract the recipient's name from a mail item.

    Args:
        mail_item (dict): A dictionary representing a mail item.

    Returns:
        str: The recipient's name.
    """
    recipient = (
        mail_item.get("node", {})
        .get("recipients", {})
        .get("line1", {})
        .get("text", "Unknown Recipient")
    )
    return recipient
