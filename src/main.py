import sys
import logging

from stable_api import fetch_mail_items, extract_recipient_name
from gdrive_api import fuzzy_search_or_create_folder, upload_to_google_drive
from db_utils import load_processed_mail_ids, save_processed_mail_id

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger()


def process_mail_items():
    mail_items = fetch_mail_items()
    processed_mail_ids = load_processed_mail_ids()

    for item in mail_items:
        mail_id = item["node"]["id"]

        if mail_id in processed_mail_ids:
            logger.info(f"Mail ID: {mail_id} already processed. Skipping...")
            continue

        recipient_name = extract_recipient_name(item)
        logger.info(f"Processing mail ID: {mail_id}, Recipient Name: {recipient_name}")

        # fetch mail content pdf url
        pdf_url = item["node"]["scanDetails"]["imageUrl"]


        if pdf_url:
            recipient_folder_id = fuzzy_search_or_create_folder(recipient_name)

            uploaded_file_id = upload_to_google_drive(mail_id, pdf_url, recipient_name, recipient_folder_id)
            if uploaded_file_id:
                # save mail ID after successful processing
                save_processed_mail_id(mail_id)

        else:
            logger.error(f"Failed to process Mail ID: {mail_id} due to null pdf url.")


if __name__ == '__main__':
    process_mail_items()
