from exchangelib import Credentials, Account, DELEGATE, Message, HTMLBody
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
import logging
from ..config.settings import (
    EMAIL_USERNAME, 
    EMAIL_PASSWORD, 
    EMAIL_ADDRESS
)
import markdown
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter

class EmailHandler:
    def __init__(self):
        self.account = None
        self._setup_account()

    def _setup_account(self):
        """Initialize the Exchange account connection"""
        try:
            logger.info("Setting up Exchange email connection...")
            credentials = Credentials(
                username=EMAIL_USERNAME,
                password=EMAIL_PASSWORD
            )
            
            self.account = Account(
                primary_smtp_address=EMAIL_ADDRESS,
                credentials=credentials,
                autodiscover=True,
                access_type=DELEGATE
            )
            logger.info("✅ Exchange connection established")
            
        except Exception as e:
            logger.error(f"❌ Exchange connection failed: {str(e)}")
            raise

    def send_markdown_email(self, subject: str, markdown_content: str, to_recipients: list):
        """
        Send an email with markdown content converted to HTML
        
        Args:
            subject (str): Email subject
            markdown_content (str): Content in markdown format
            to_recipients (list): List of recipient email addresses
        """
        try:
            # Convert markdown to HTML
            html_content = markdown.markdown(markdown_content)
            
            message = Message(
                account=self.account,
                subject=subject,
                body=HTMLBody(html_content),
                to_recipients=to_recipients
            )
            message.send()
            logger.info(f"📧 Email sent to {', '.join(to_recipients)}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {str(e)}")
            raise

    def check_inbox(self, hours_back=24):
        """
        Check inbox for unread messages within specified time period
        
        Args:
            hours_back (int): Number of hours to look back for emails
        
        Returns:
            list: List of processed email items
        """
        try:
            # Calculate time threshold
            time_threshold = datetime.now() - timedelta(hours=hours_back)
            
            # Filter for unread messages
            unread_messages = self.account.inbox.filter(
                is_read=False,
                datetime_received__gt=time_threshold
            )
            
            processed_items = []
            for item in unread_messages:
                try:
                    processed_item = self._process_email(item)
                    if processed_item:
                        processed_items.append(processed_item)
                    
                    # Mark as read
                    item.is_read = True
                    item.save()
                    
                except Exception as e:
                    logger.error(f"❌ Error processing email {item.subject}: {str(e)}")
                    continue
            
            return processed_items
            
        except Exception as e:
            logger.error(f"❌ Error checking inbox: {str(e)}")
            raise

    def _process_email(self, email_item):
        """
        Process individual email items
        
        Args:
            email_item: Exchange email item
            
        Returns:
            dict: Processed email data or None if processing fails
        """
        try:
            # Extract relevant information
            return {
                'subject': email_item.subject,
                'sender': email_item.sender.email_address,
                'received_time': email_item.datetime_received,
                'body': email_item.body,
                'has_attachments': email_item.has_attachments,
                'attachments': [
                    {
                        'name': attachment.name,
                        'content_type': attachment.content_type
                    }
                    for attachment in email_item.attachments
                ] if email_item.has_attachments else []
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing email: {str(e)}")
            return None

def get_email_handler():
    """Factory function to create and return an EmailHandler instance"""
    return EmailHandler()

if __name__ == "__main__":
    # Test the email connection
    handler = get_email_handler()
    if handler.is_connected():
        print("✅ Email connection test successful")
    else:
        print("❌ Email connection test failed")