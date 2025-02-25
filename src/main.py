import requests

from config import STABLE_API_KEY
from config import STABLE_API_URL
from config import SUPABASE_URL
from config import SUPABASE_KEY
from logger import get_logger
from services.google_drive import GoogleDriveService
from services.stable_mail import StableMailService
from services.storage import SupabaseDatabase

logger = get_logger()


def process_mail_items(drive_service, db_service, mail_service):
    mail_items = mail_service.fetch_mail_items()
    processed_mail_ids = db_service.get_processed_mail_ids()

    for item in mail_items:
        mail_id = item["node"]["id"]

        if mail_id in processed_mail_ids:
            logger.info(f"Mail ID: {mail_id} already processed. Skipping...")
            continue

        recipient_name = mail_service.extract_recipient_name(item)
        logger.info(f"Processing mail ID: {mail_id}, Recipient Name: {recipient_name}")

        pdf_url = item["node"]["scanDetails"]["imageUrl"]

        if pdf_url:
            folder_id, matched = drive_service.fuzzy_search(recipient_name)

            if not matched:
                logger.warning(
                    f"No matching folder found for '{recipient_name}'. "
                    "Document will be saved in the default folder."
                )

            response = requests.get(pdf_url)
            if response.status_code == 200:
                file_name = (
                    f"{recipient_name}_{mail_id}.pdf" if not matched
                    else f"{mail_id}.pdf"
                )

                uploaded_file_id = drive_service.upload_file(
                    file_name, response.content, folder_id
                )
                if uploaded_file_id:
                    db_service.save_processed_mail_id(mail_id, recipient_name)
            else:
                logger.error(f"Failed to download PDF for Mail ID: {mail_id}")
        else:
            logger.error(f"Failed to process Mail ID: {mail_id} due to null pdf url.")


if __name__ == "__main__":

    drive_service = GoogleDriveService()
    db_service = SupabaseDatabase(SUPABASE_URL, SUPABASE_KEY)
    mail_service = StableMailService(STABLE_API_KEY, STABLE_API_URL)

    process_mail_items(drive_service, db_service, mail_service)
