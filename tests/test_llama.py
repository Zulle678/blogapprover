from src.services.llama_service import get_llama_service
import logging

logging.basicConfig(level=logging.INFO)

def test_content_revision():
    service = get_llama_service()
    
    # Test content
    original_content = """
    # My Blog Post
    
    This is a test blog post about AI.
    It needs some improvement.
    
    ## Key Points
    * Point 1
    * Point 2
    """
    
    feedback = """
    Please add more detail to the key points and
    improve the introduction paragraph.
    """
    
    try:
        revised = service.revise_content(original_content, feedback)
        print("\nOriginal Content:")
        print(original_content)
        print("\nRevised Content:")
        print(revised)
        
    except Exception as e:
        print(f"Test failed: {str(e)}")

if __name__ == "__main__":
    test_content_revision()