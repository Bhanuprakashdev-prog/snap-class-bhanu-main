import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load .env for local dev (no-op in production where env vars are already set)
load_dotenv()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables or .env")

supabase: Client = create_client(supabase_url, supabase_key)