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
from enum import Enum
from typing import Optional, Dict, Any
from ..services.llama_service import get_llama_service
from ..prompts.email_prompts import APPROVAL_ANALYSIS_PROMPT
from ..prompts.blog_prompts import BLOG_REVISION_SYSTEM_PROMPT, BLOG_REVISION_PROMPT
import json

class ApprovalStatus(Enum):
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"
    UNKNOWN = "unknown"

logger = logging.getLogger(__name__)
BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter

class EmailHandler:
    def __init__(self):
        self.account = None
        self.llm_service = get_llama_service()
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
        Check inbox for unread messages, process them, and clean up
        
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
                        self.handle_approval_response(processed_item)
                    
                    # Move to deleted items instead of just marking as read
                    item.move_to_trash()
                    logger.info(f"🗑️ Moved processed email '{item.subject}' to trash")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing email {item.subject}: {str(e)}")
                    continue
            
            return processed_items
            
        except Exception as e:
            logger.error(f"❌ Error checking inbox: {str(e)}")
            raise

    def _process_email(self, email_item) -> Optional[Dict[str, Any]]:
        """
        Process individual email items and determine approval status
        
        Args:
            email_item: Exchange email item
            
        Returns:
            dict: Processed email data with approval status or None if processing fails
        """
        try:
            # Extract basic information
            processed_data = {
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
                ] if email_item.has_attachments else [],
                'approval_status': self._determine_approval_status(email_item.body),
                'feedback': email_item.body if email_item.body else ''
            }
            
            logger.info(f"📧 Processed email with status: {processed_data['approval_status'].value}")
            return processed_data
            
        except Exception as e:
            logger.error(f"❌ Error processing email: {str(e)}")
            return None

    def _determine_approval_status(self, email_body: str) -> ApprovalStatus:
        """
        Use LLM to analyze email content and determine if it's an approval or revision request
        
        Args:
            email_body (str): The email body content
            
        Returns:
            ApprovalStatus: The determined approval status
        """
        if not email_body:
            return ApprovalStatus.UNKNOWN

        try:
            # Format prompt with email content
            prompt = APPROVAL_ANALYSIS_PROMPT.format(email_content=email_body)
            
            # Get LLM analysis
            response = self.llm_service.analyze_text(prompt)
            
            try:
                # Parse JSON response
                analysis = json.loads(response)
                
                # Log the analysis
                logger.info(f"📊 LLM Analysis: {analysis['reasoning']} (Confidence: {analysis['confidence']})")
                
                # Determine status based on LLM analysis
                status = analysis.get('status', 'UNKNOWN')
                if status == 'APPROVED':
                    logger.info("✅ LLM determined: Approval")
                    return ApprovalStatus.APPROVED
                elif status == 'NEEDS_REVISION':
                    logger.info("📝 LLM determined: Needs Revision")
                    return ApprovalStatus.NEEDS_REVISION
                else:
                    logger.warning("❓ LLM determined: Unknown")
                    return ApprovalStatus.UNKNOWN
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse LLM response: {str(e)}")
                return ApprovalStatus.UNKNOWN
                
        except Exception as e:
            logger.error(f"❌ Error in LLM analysis: {str(e)}")
            return ApprovalStatus.UNKNOWN

    def handle_approval_response(self, processed_email: Dict[str, Any], original_content: str) -> None:
        """
        Handle the email response based on its approval status
        
        Args:
            processed_email (Dict[str, Any]): The processed email data
            original_content (str): The original blog post content
        """
        try:
            status = processed_email['approval_status']
            subject = processed_email['subject']
            feedback = processed_email['feedback']
            
            if status == ApprovalStatus.NEEDS_REVISION:
                logger.info(f"📝 Revising post '{subject}' based on feedback")
                
                # Prepare revision prompt
                revision_prompt = BLOG_REVISION_PROMPT.format(
                    system_prompt=BLOG_REVISION_SYSTEM_PROMPT,
                    original_content=original_content,
                    feedback=feedback
                )
                
                # Get revised content
                revised_content = self.llm_service.revise_content(revision_prompt)
                
                if revised_content:
                    logger.info("✅ Blog post revised successfully")
                    # Here you would save the revised content and notify the author
                    self.send_markdown_email(
                        subject=f"Re: {subject} - Blog Post Revised",
                        markdown_content=(
                            "Your blog post has been revised based on the feedback.\n\n"
                            "## Original Feedback\n"
                            f"{feedback}\n\n"
                            "## Revised Content\n"
                            f"{revised_content}"
                        ),
                        to_recipients=[processed_email['sender']]
                    )
                else:
                    logger.error("❌ Failed to revise blog post")
            
            # ...existing approval handling code...
            
        except Exception as e:
            logger.error(f"❌ Error handling approval response: {str(e)}")
            raise

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