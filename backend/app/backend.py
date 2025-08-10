from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .router import api_router

from dotenv import load_dotenv
# Load environment variables
load_dotenv()

from .observability import init_observability
# Initialize observability
init_observability()

app = FastAPI()

# Allow CORS for local React dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)



