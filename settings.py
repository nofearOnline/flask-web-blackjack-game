from os import environ
from dotenv import load_dotenv

load_dotenv()

SERVER_ADDRESS = environ.get("SERVER_ADDRESS", "http://localhost:5000")