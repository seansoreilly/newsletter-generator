"""
Module for AI content enhancement using DeepSeek via the OpenRouter Chat Completions API.

This module enriches news articles with:
  - A concise two-sentence summary.
  - A relevance score between 0 and 100.
  - A relevance explanation regarding its relevance to Greater Dandenong Council.
"""

import os
import json
import logging
from typing import Dict
import requests
from dotenv import load_dotenv

# Add logging configuration
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level to DEBUG to see all messages
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # This will output to console/stdout
    ]
)

load_dotenv()

# Endpoint for OpenRouter's Chat Completions API (adjust if necessary)
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def enrich_article(article: Dict) -> Dict:
    """
    Enrich the given article using the OpenRouter Chat Completions API.

    Args:
        article (Dict): Article data containing keys such as 'title' and 'url'.

    Returns:
        Dict: The enriched article updated with the following keys:
            - 'summary': A concise two-sentence summary.
            - 'image_url': A URL to the main image related to the article.
            - 'relevance_score': A relevance score between 0 and 100.
            - 'relevance': A brief explanation of the article's relevance.
    """

    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        logging.error("OPENROUTER_API_KEY not found in environment variables.")
        article["summary"] = "Summary unavailable."
        article["image_url"] = "Image unavailable."
        article["relevance_score"] = "N/A"
        article["relevance"] = "No API key provided."
        return article

    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json",
    }

    # Construct a structured prompt as JSON for a cleaner format.
    prompt_dict = {
        "article_title": article.get("title"),
        "article_url": article.get("url"),
        "instruction": (
            "summary: Generate a concise two-sentence summary of this article. "
            "image_url: Extract and return only the main image img['src'] attribute. "
            "relevance_score: Evaluate the article's relevance to the Greater Dandenong Council and provide a numerical score between 0 and 100. "
            "relevance: Provide a brief explanation of the relevance. "
            "Return your response as a JSON object with the keys \"summary\", \"image_url\", \"relevance_score\", and \"relevance\"."
        )
    }

    prompt = json.dumps(prompt_dict)

    data = {
        # "model": "openai/gpt-3.5-turbo",
        # "model": "perplexity/llama-3.1-sonar-small-128k-online",
        "model": "perplexity/llama-3.1-sonar-huge-128k-online",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        # Increased max_tokens to handle longer responses
        "max_tokens": 500,
        "temperature": 0.7,
        # Add response format instructions
        "response_format": {"type": "json_object"}
    }

    try:
        # Log the raw request details
        logging.debug("Sending request to OpenRouter API")
        logging.debug("Request URL: %s", OPENROUTER_API_URL)
        logging.debug("Request headers: %s", headers)
        logging.debug("Request payload: %s", data)

        response = requests.post(
            OPENROUTER_API_URL, headers=headers, json=data)
        response.raise_for_status()

        # Log the raw response
        raw = response.text
        logging.debug(f"Raw response: {raw}")

        result = response.json()
        # Retrieve the chat response content from OpenRouter
        chat_response = result["choices"][0]["message"]["content"]
        # Clean up the response - remove any leading/trailing whitespace and newlines
        chat_response = chat_response.strip()

        # If response is wrapped in ```, remove it
        if chat_response.startswith('```') and chat_response.endswith('```'):
            chat_response = chat_response[3:-3].strip()

        # If response starts with 'json', remove it
        if chat_response.startswith('json'):
            chat_response = chat_response[4:].strip()

        try:
            # Try to parse the response as JSON
            parsed = json.loads(chat_response)

            # Get the fields with default values if missing
            summary = parsed.get("summary", "Summary not provided")
            relevance = parsed.get(
                "relevance", "Relevance explanation not provided")

            # Handle relevance score - convert to int if possible
            score = parsed.get("relevance_score", 0)
            try:
                score = int(score)
                if not (0 <= score <= 100):
                    score = max(0, min(100, score))  # Clamp between 0 and 100
            except (ValueError, TypeError):
                score = 0
                logging.warning(f"Invalid relevance score format: {
                                parsed.get('relevance_score')}, defaulting to 0")

            article["summary"] = summary
            article["relevance_score"] = score
            article["relevance"] = relevance

            # Log successful parsing
            logging.debug(f"Successfully parsed AI response for article: {
                          article.get('title')}")
            logging.debug(f"Summary: {summary[:100]}...")
            logging.debug(f"Relevance Score: {score}")

        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse AI response as JSON: {str(e)}")
            logging.debug(f"Raw AI response: {chat_response}")

            # Attempt to extract content even if JSON parsing fails
            # Look for patterns in the raw response
            lines = chat_response.split('\n')
            summary = ""
            relevance = ""
            score = 0

            for line in lines:
                line = line.strip()
                if '"summary":' in line:
                    summary = line.split('"summary":')[1].strip().strip('",')
                elif '"relevance":' in line:
                    relevance = line.split('"relevance":')[
                        1].strip().strip('",')
                elif '"relevance_score":' in line:
                    try:
                        score = int(line.split('"relevance_score":')[
                                    1].strip().strip(','))
                    except ValueError:
                        score = 0

            article["summary"] = summary if summary else "Error: Could not parse summary"
            article["relevance_score"] = score
            article["relevance"] = relevance if relevance else "Error: Could not parse relevance"

    except requests.RequestException as e:
        logging.error("API request failed: %s", str(e))
        article["summary"] = "Error: Failed to contact AI service"
        article["relevance_score"] = "N/A"
        article["relevance"] = f"Error: API request failed"

    except Exception as e:
        logging.error("Unexpected error enriching article: %s", str(e))
        article["summary"] = "Error: Unexpected error during enrichment"
        article["relevance_score"] = "N/A"
        article["relevance"] = f"Error: {str(e)}"

    return article


if __name__ == "__main__":
    # Test the enrich_article function with a sample article
    sample_article = {
        "title": "Soil mound clean-up goes to VCAT - Dandenong Star Journal",
        "url": "https://news.google.com/rss/articles/CBMikgFBVV95cUxNRy01TWlTYWJGTl8tVDhTTENvOG9YRk1YcE5zZk5QVko5R01ONzlvZGtISWNHMGY0OTJkdlloQldSZElQNEtZR2FISDNINFZJMGpMT21jbElmWWgtOXFSdEZidGZyZ19HSmdqZzZQY1luT0N2REV1SDJSazkzcW9CNzgwN29obW05RURCWGtTbGNiQQ?oc=5"
    }
    enriched = enrich_article(sample_article)
    print("Enriched Article:")
    print(enriched)
