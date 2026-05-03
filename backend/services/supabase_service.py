"""
Supabase Service — Handles interactions with Supabase Auth and Storage.
"""
import os
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

# Initialize Supabase Admin Client (using service key for backend operations)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def verify_supabase_token(token: str):
    """
    Verify a Supabase JWT token and return user data.
    """
    try:
        # In a real scenario, you'd use the gotrue-js equivalent or verify JWT manually.
        # supabase-py's auth.get_user(token) is the easiest way.
        user = supabase.auth.get_user(token)
        return user.user
    except Exception as e:
        print(f"Supabase Auth Error: {e}")
        return None

def upload_to_supabase(bucket: str, path: str, file_content: bytes):
    """
    Upload a file to Supabase Storage.
    """
    try:
        res = supabase.storage.from_(bucket).upload(path, file_content)
        return res
    except Exception as e:
        print(f"Supabase Storage Error: {e}")
        return None

def get_public_url(bucket: str, path: str):
    """
    Get public URL for a file in Supabase Storage.
    """
    return supabase.storage.from_(bucket).get_public_url(path)
