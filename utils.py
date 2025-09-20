import os
from dotenv import load_dotenv

load_dotenv()

def load_env_var(var_name):
    """Utility for loading env vars (Software Engineering tech stack)."""
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"{var_name} not found in .env")
    return value