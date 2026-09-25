# backend/vercel_api.py
from mangum import Mangum
from .main import app  # <-- this imports the FastAPI app you already have

# Vercel will invoke this `handler`
handler = Mangum(app)