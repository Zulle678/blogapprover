from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import logging
from pathlib import Path
from src.config.settings import PENDING_DIR, APPROVED_DIR

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class MarkdownHandler(FileSystemEventHandler):
    """Handler for monitoring markdown files in the pending directory."""
    
    def on_created(self, event):
        """Handle creation of new files."""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if file_path.suffix.lower() == '.md':
            logger.info(f"📝 New markdown file detected: {file_path.name}")
            self.process_markdown_file(file_path)

    def on_modified(self, event):
        """Handle modifications to existing files."""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if file_path.suffix.lower() == '.md':
            logger.info(f"🔄 Markdown file modified: {file_path.name}")
            self.process_markdown_file(file_path)

    def process_markdown_file(self, file_path: Path):
        """
        Process the markdown file.
        To be implemented with actual processing logic.
        """
        logger.info(f"⚙️ Processing file: {file_path.name}")
        # TODO: Implement processing logic here

def watch_directory(directory_path: str = PENDING_DIR):
    """
    Initialize and start the directory observer.
    
    Args:
        directory_path (str): Path to the directory to monitor
    """
    # Ensure directories exist
    for dir_path in [PENDING_DIR, APPROVED_DIR]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    event_handler = MarkdownHandler()
    observer = Observer()
    observer.schedule(event_handler, directory_path, recursive=False)
    
    logger.info(f"🔍 Starting monitoring of {directory_path}")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("👋 Stopping file monitor (Ctrl+C detected)")
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    watch_directory()