import pytest
from src.services.email_service import get_email_handler, ApprovalStatus

@pytest.mark.parametrize("email_content,expected_status", [
    (
        "The blog post looks great! Please proceed with publishing.",
        ApprovalStatus.APPROVED
    ),
    (
        "Could you please fix the typos in paragraph 2 and add more examples?",
        ApprovalStatus.NEEDS_REVISION
    ),
    (
        "I've looked at it.",
        ApprovalStatus.UNKNOWN
    ),
])
def test_email_analysis(email_content, expected_status):
    handler = get_email_handler()
    status = handler._determine_approval_status(email_content)
    assert status == expected_status

@pytest.mark.parametrize("test_case", [
    {
        "original_content": """
# Test Blog Post
This is a simple blog post about Python.
It has some typos and neds more examples.
        """,
        "feedback": """
Please fix the following:
1. "neds" should be "needs"
2. Add an example of Python code
3. Expand the introduction
        """,
        "expected_status": ApprovalStatus.NEEDS_REVISION
    },
    {
        "original_content": """
# Perfect Blog Post
This is a well-written post that needs no changes.
        """,
        "feedback": "Looks perfect! Please publish.",
        "expected_status": ApprovalStatus.APPROVED
    }
])
def test_blog_revision_and_cleanup(test_case):
    handler = get_email_handler()
    
    # Create a mock email item for testing
    mock_email = {
        'subject': 'Test Blog Post',
        'sender': 'test@example.com',
        'body': test_case["feedback"],
        'move_to_trash': lambda: None  # Mock the move_to_trash method
    }
    
    # Process the email
    status = handler._determine_approval_status(test_case["feedback"])
    assert status == test_case["expected_status"]
    
    if status == ApprovalStatus.NEEDS_REVISION:
        processed_email = {
            'approval_status': status,
            'subject': mock_email['subject'],
            'sender': mock_email['sender'],
            'feedback': test_case["feedback"]
        }
        
        # Test both revision and cleanup
        handler.handle_approval_response(processed_email, test_case["original_content"])
        
        # Verify email was moved to trash
        try:
            mock_email['move_to_trash']()
            logger.info("✅ Email cleanup test passed")
        except Exception as e:
            pytest.fail(f"Failed to move email to trash: {str(e)}")