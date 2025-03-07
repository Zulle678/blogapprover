import requests
import logging
from ..config.settings import (
    LLAMA_SERVER_URL, 
    LLAMA_MODEL, 
    LLAMA_CONTEXT_SIZE
)

logger = logging.getLogger(__name__)

class LlamaService:
    def __init__(self):
        self.base_url = LLAMA_SERVER_URL
        self.model = LLAMA_MODEL
        self.context_size = LLAMA_CONTEXT_SIZE
        
    def _make_request(self, prompt: str) -> dict:
        """Make a request to the Llama server"""
        payload = {
            'model': self.model,
            'prompt': prompt,
            'max_tokens': self.context_size
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/1.0/text/completion",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Llama server request failed: {str(e)}")
            raise

    def revise_content(self, original_content: str, feedback: str) -> str:
        """
        Revise content based on feedback using Llama
        
        Args:
            original_content (str): The original markdown content
            feedback (str): Feedback to incorporate
            
        Returns:
            str: Revised content
        """
        prompt = (
            f"# Original Content\n\n{original_content}\n\n"
            f"# Feedback\n\n{feedback}\n\n"
            "# Instructions\n\n"
            "Please revise the original content incorporating the feedback. "
            "Maintain the original markdown formatting. "
            "Return only the revised content without any additional commentary."
        )
        
        try:
            response = self._make_request(prompt)
            revised_content = response.get('choices', [{}])[0].get('text', '').strip()
            
            if not revised_content:
                logger.warning("⚠️ Llama returned empty response, falling back to original")
                return original_content
                
            logger.info("✅ Content successfully revised")
            return revised_content
            
        except Exception as e:
            logger.error(f"❌ Content revision failed: {str(e)}")
            return original_content

def get_llama_service():
    """Factory function to create and return a LlamaService instance"""
    return LlamaService()