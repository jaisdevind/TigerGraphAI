from mangum import Mangum
from .main import app

# Export a handler that Vercel expects for Python serverless functions
handler = Mangum(app)
