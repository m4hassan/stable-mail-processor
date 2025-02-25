from supabase import create_client, Client
from logger import get_logger
from . import DatabaseService

logger = get_logger()


class SupabaseDatabase(DatabaseService):
    def __init__(self, supabase_url: str, supabase_key: str):
        self.client: Client = create_client(supabase_url, supabase_key)

    def get_processed_mail_ids(self):
        try:
            response = self.client.table("processed_mails").select("mail_id").execute()
            return set(row["mail_id"] for row in response.data or [])
        except Exception as e:
            logger.error(f"Error retrieving processed mail ids: {e}")
            return set()

    def save_processed_mail_id(self, mail_id, recipient_name):
        try:
            data = {"mail_id": mail_id, "recipient_name": recipient_name}
            self.client.table("processed_mails").insert(data).execute()
            logger.info(f"Mail ID '{mail_id}' saved successfully.")
        except Exception as e:
            logger.error(f"Error inserting processed mail id '{mail_id}': {e}")
