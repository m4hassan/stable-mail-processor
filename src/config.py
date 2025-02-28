import os
from dotenv import load_dotenv

load_dotenv()

UNMATCHED_COURT_DOCUMENTS = os.getenv("UNMATCHED_COURT_DOCUMENTS", "")
DRAFT_LAWSUIT_PACKETS_ALL_ID = os.getenv("DRAFT_LAWSUIT_PACKETS_ALL_ID", "")

STABLE_API_KEY = os.getenv("STABLE_API_KEY", "")
STABLE_API_URL = "https://api.usestable.com/v1/mail-items"

SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
