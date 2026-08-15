import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    OPINET_API_KEY = os.getenv("OPINET_API_KEY", "")
    JSON_AS_ASCII = False
