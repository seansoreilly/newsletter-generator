import json
import requests
import logging

def parse_ai_response(response_text):
    """
    Parses the AI response, handling both raw JSON and markdown-formatted JSON responses
    """
    try:
        # First try to parse as regular JSON
        return json.loads(response_text)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON from markdown
        if "```json" in response_text:
            try:
                # Extract content between ```json and ```
                content_start = response_text.find("```json") + len("```json")
                content_end = response_text.rfind("```")
                json_content = response_text[content_start:content_end].strip()
                return json.loads(json_content)
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(f"Failed to parse markdown JSON content: {e}")
                raise

def clean_payload(payload):
    """
    Cleans the payload by converting string JSON content into proper JSON objects
    """
    if "choices" in payload:
        for choice in payload["choices"]:
            if "message" in choice:
                msg = choice["message"]
                if "content" in msg and isinstance(msg["content"], str):
                    content = msg["content"]
                    # Remove markdown code fences if present
                    if content.startswith("```json"):
                        content = content[len("```json"):].strip()
                    if content.endswith("```"):
                        content = content[:-len("```")].strip()
                    
                    # Parse the content string into a JSON object
                    try:
                        msg["content"] = json.loads(content)
                    except json.JSONDecodeError as e:
                        logging.error(f"Failed to parse JSON content: {e}")
                        # Keep original content if parsing fails
                        continue
    return payload

def send_ai_request(payload):
    """
    Sends request to AI service and handles the response
    """
    # Clean payload to convert string JSON into proper JSON objects
    cleaned_payload = clean_payload(payload)

    try:
        response = requests.post("http://api_endpoint", json=cleaned_payload)
        response_data = parse_ai_response(response.text)
        
        # If the response contains choices with content, extract the actual content
        if "choices" in response_data:
            for choice in response_data["choices"]:
                if "message" in choice and "content" in choice["message"]:
                    content = choice["message"]["content"]
                    if isinstance(content, str):
                        # Parse the content if it's a string
                        try:
                            choice["message"]["content"] = json.loads(content)
                        except json.JSONDecodeError:
                            # If parsing fails, keep as is
                            pass
        
        return response_data
    except Exception as e:
        logging.error(f"Error in AI request: {str(e)}")
        logging.error(f"Response text: {response.text if 'response' in locals() else 'No response'}")
        raise

# ... (other code in the file) 