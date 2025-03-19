import os

from dotenv import load_dotenv


def get_api_url(release_name: str) -> str:
    api_url = ""
    if release_name:
        api_url = f"https://api.dev.deeppack.ai/{release_name}"
    else:
        api_url = "https://api.dev.deeppack.ai"
    return api_url


# Load environment variables from .env file
load_dotenv()

# Access the WEB_URL variable
release_name = os.getenv("RELEASE_NAME")

# API key
api_key = os.getenv("API_KEY")

# API Url and headers
api_url = get_api_url(release_name)

web_url = api_url.replace("api", "instadeep")
headers = {"Content-Type": "application/json", "x-deeppack-api-key": api_key}
