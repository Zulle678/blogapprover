import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Setup logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

# Email Configuration
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT')

# Email Settings
EMAIL_SETTINGS = {
    'USE_SSL': True,
    'VERIFY_SSL': False,  # Set to True in production
    'TIMEOUT': 30,  # seconds
}

# Add validation for email configuration
def validate_email_config():
    """Validate email configuration settings"""
    if not all([EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_ADDRESS]):
        raise ValueError("Missing required email configuration values")

validate_email_config()

# Directory Paths
PENDING_DIR = os.getenv('PENDING_DIR')
APPROVED_DIR = os.getenv('APPROVED_DIR')

# Ollama Configuration
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')

# Llama Configuration
LLAMA_SERVER_URL = os.getenv('LLAMA_SERVER_URL')
LLAMA_MODEL = os.getenv('LLAMA_MODEL')
LLAMA_CONTEXT_SIZE = int(os.getenv('LLAMA_CONTEXT_SIZE', 4096))

# Validate required environment variables
required_vars = [
    'EMAIL_USERNAME', 
    'EMAIL_PASSWORD', 
    'EMAIL_ADDRESS', 
    'EMAIL_RECIPIENT',
    'PENDING_DIR',
    'APPROVED_DIR',
    'OLLAMA_MODEL',
    'LLAMA_SERVER_URL',
    'LLAMA_MODEL'
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Initialize logging
setup_logging()