import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", None)
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

"""
echo=True is definitely something I want inside create_engine, to see the SQL expression that's going on under the hood.
NOTE: It lives conceptually at the engine level because it controls SQL logging behavior for the engine. Understand that responsibility.
"""
engine = create_engine(DATABASE_URL, echo=True)