import logging
import requests

from config import STABLE_API_KEY, STABLE_API_URL

logger = logging.getLogger(__name__)


def fetch_mail_items(status="completed"):
    """
    Fetch mail items from the Stable API with the given scan status.

    Args:
        status (str): The scan status of the mail items to fetch. Default is 'completed'.

    Returns:
        list: A list of mail item dictionaries.
    """
    url = f"{STABLE_API_URL}/"

    headers = {
        "accept": "application/json",
        "x-api-key": STABLE_API_KEY
    }
    params = {
        "scan.status": status,
        "first": 2,
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Error fetching mail items: {response.status_code} - {response.text}")
        return []

    data = response.json()
    return data.get("edges", [])


def extract_recipient_name(mail_item):
    """
    Extract the recipient's name from a mail item.

    Args:
        mail_item (dict): A dictionary representing a mail item.

    Returns:
        str: The recipient's name.
    """
    recipient = mail_item.get("node", {}).get("recipients", {}).get("line1", {}).get("text", "Unknown Recipient")
    return recipient

