APPROVAL_ANALYSIS_PROMPT = """
You are an AI assistant helping to determine if an email response for a blog post review is an approval or requires revisions.

Email to analyze:
{email_content}

Task:
Analyze the email content and determine the reviewer's intention.

Guidelines:
1. Look for clear approval signals like confirming the post is ready to publish
2. Identify any suggestions for changes, improvements, or corrections
3. Consider the overall tone and context of the response
4. Check for specific feedback or revision requests
5. Note any conditions for approval

Required Response Format:
{
    "status": "APPROVED|NEEDS_REVISION|UNKNOWN",
    "confidence": <float between 0 and 1>,
    "reasoning": "<brief explanation of decision>",
    "feedback": "<extracted feedback if any>"
}

Respond only with the JSON object, no additional text.
"""