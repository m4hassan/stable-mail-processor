import requests

from logger import get_logger

from . import MailService

logger = get_logger()


class StableMailService(MailService):
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url

    def fetch_mail_items(self, status="completed"):
        headers = {"accept": "application/json", "x-api-key": self.api_key}
        params = {"scan.status": status, "first": 50}
        all_items = []

        while True:
            response = requests.get(self.api_url, headers=headers, params=params)
            if response.status_code != 200:
                logger.error(f"Error fetching mail items: {response.status_code}")
                break

            data = response.json()
            fetched_items = data.get("edges", [])
            all_items.extend(fetched_items)

            page_info = data.get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break

            params["after"] = page_info.get("endCursor")

        return all_items

    def extract_recipient_name(self, mail_item):
        return (
            mail_item.get("node", {})
            .get("recipients", {})
            .get("line1", {})
            .get("text", "Unknown Recipient")
        )
