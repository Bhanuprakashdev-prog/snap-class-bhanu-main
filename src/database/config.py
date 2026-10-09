import os
import tomllib
from supabase import create_client, Client

# 1. First check environment variables (Standard for Cloud Deployments: Docker, Render, Railway, Vercel)
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

# 2. Fallback to .streamlit/secrets.toml if present locally (without importing streamlit)
if not supabase_url or not supabase_key:
    secrets_path = os.path.join(os.path.dirname(__file__), "..", "..", ".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        try:
            with open(secrets_path, "rb") as f:
                secrets = tomllib.load(f)
                supabase_url = supabase_url or secrets.get("SUPABASE_URL")
                supabase_key = supabase_key or secrets.get("SUPABASE_KEY")
        except Exception as e:
            print(f"Warning: Could not parse {secrets_path}: {e}")

if not supabase_url or not supabase_key:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables or .streamlit/secrets.toml")

supabase: Client = create_client(supabase_url, supabase_key)