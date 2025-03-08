# Blog Approver

A Python application that handles blog post approval workflow with automated content revision and email notifications.

## Features

- 📝 Monitors directory for new markdown blog posts
- 🤖 AI-powered content revision using Llama/Ollama
- 📧 Email notifications through Exchange server
- ✨ Markdown to HTML conversion for emails

## Architecture

The application follows a service-based architecture with three main components:

### 1. File Service ([`src/services/file_service.py`](src/services/file_service.py))
- Monitors specified directory for markdown files
- Handles file creation and modification events
- Uses `watchdog` library for file system events

### 2. LLM Service ([`src/services/llama_service.py`](src/services/llama_service.py))
- Integrates with Llama/Ollama API
- Provides content revision capabilities
- Maintains original markdown formatting

### 3. Email Service ([`src/services/email_service.py`](src/services/email_service.py))
- Handles email communication through Exchange server
- Supports markdown to HTML conversion
- Manages email inbox monitoring

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd blogapprover

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt

# Email Configuration
EMAIL_USERNAME=your_username
EMAIL_PASSWORD=your_password
EMAIL_ADDRESS=your_email@example.com
EMAIL_RECIPIENT=recipient@example.com

# Directory Paths
PENDING_DIR=/path/to/pending
APPROVED_DIR=/path/to/approved

# LLM Configuration
LLAMA_SERVER_URL=http://localhost:11434
LLAMA_MODEL=your_model_name
LLAMA_CONTEXT_SIZE=4096

python src/main.py

# Test email functionality
python tests/test_email.py

# Test LLM service
python tests/test_llama.py

blogapprover/
├── src/
│   ├── config/
│   │   └── settings.py     # Configuration management
│   ├── services/
│   │   ├── email_service.py
│   │   ├── file_service.py
│   │   └── llama_service.py
│   └── main.py            # Application entry point
└── tests/
    ├── test_email.py
    └── test_llama.py

Error Handling
The application includes comprehensive error handling:

Service initialization errors
File system monitoring errors
Email communication errors
LLM API errors
All errors are logged with appropriate severity levels.

Logging
The application uses Python's built-in logging with:

INFO level for normal operations
ERROR level for failures
WARNING level for non-critical issues
Timestamps and module information in log messages
Dependencies
exchangelib: Exchange server communication
watchdog: File system monitoring
markdown: Markdown to HTML conversion
python-dotenv: Environment variable management
requests: HTTP client for LLM API    


Security Notes
SSL verification is disabled by default for development
Enable SSL verification in production
Secure storage of credentials using environment variables
No sensitive data logged
Future Improvements
Add webhook support for notifications
Implement content approval workflow
Add support for multiple LLM providers
Enhance markdown processing capabilities
Add API endpoints for manual control