from mangum import Mangum
from app.main import app

import os

# strip stage prefix so /prod/health → /health for FastAPI
stage = os.environ.get("STAGE_NAME", "/prod")
handler = Mangum(app, lifespan="off", api_gateway_base_path=stage)
