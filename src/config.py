import os
from dotenv import load_dotenv

load_dotenv()

STABLE_API_KEY = os.getenv('STABLE_API_KEY')
STABLE_API_URL = 'https://api.usestable.com/v1/mail-items'

SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
