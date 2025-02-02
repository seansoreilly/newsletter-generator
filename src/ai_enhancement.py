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
    Enrich the given article using DeepSeek via the OpenRouter Chat Completions API.

    Args:
        article (Dict): Article data containing keys such as 'title' and 'url'.

    Returns:
        Dict: The enriched article updated with the following keys:
            - 'summary': A concise two-sentence summary.
            - 'relevance_score': A relevance score between 0 and 100.
            - 'relevance': A brief explanation of the article's relevance.
    """
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        logging.error("OPENROUTER_API_KEY not found in environment variables.")
        article["summary"] = "Summary unavailable."
        article["relevance_score"] = "N/A"
        article["relevance"] = "No API key provided."
        return article

    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json",
        # Optionally, add HTTP-Referer and X-Title headers if needed:
        # "HTTP-Referer": "<YOUR_SITE_URL>",
        # "X-Title": "<YOUR_SITE_NAME>",
    }

    # Construct the prompt. We instruct the model to return a JSON object.
    prompt = (
        f"Article Title: {article.get('title')}\n"
        f"Article URL: {article.get('url')}\n\n"
        "Please generate a concise two-sentence summary of this article, then evaluate its relevance to "
        "the Greater Dandenong Council. Provide a numerical relevance score between 0 and 100 and a brief explanation "
        "of the relevance. Return your response as a JSON object with the keys 'summary', 'relevance_score', and 'relevance'."
    )

    data = {
        # "model": "openai/gpt-3.5-turbo",
        "model": "perplexity/llama-3.1-sonar-small-128k-online",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        # Optionally include max_tokens, temperature, etc.
        "max_tokens": 150,
        "temperature": 0.7
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
        # Attempt to parse the response as JSON
        parsed = json.loads(chat_response)
        article["summary"] = parsed.get("summary", "Summary unavailable.")
        article["relevance_score"] = parsed.get("relevance_score", "N/A")
        article["relevance"] = parsed.get(
            "relevance", "No explanation provided.")
    except Exception as e:
        logging.error("Error enriching article: %s", str(e))
        article["summary"] = "Summary unavailable due to an error."
        article["relevance_score"] = "N/A"
        article["relevance"] = f"Error: {str(e)}"

    return article


if __name__ == "__main__":
    # Test the enrich_article function with a sample article
    sample_article = {
        "title": "Council roasted over coffee cups - Dandenong Star Journal",
        "url": "https://news.google.com/rss/articles/CBMikgFBVV95cUxQYl9adl83X3Q3TEZma1V3WmhCQ1dmczBQVXRVdGw4c29BRFRRU2w1OXhYMXRMZUU3UTNPUlE5X3VFVVh6bkxpZkZQYUFEbHpJZjk1YTBpZ3ItUEloMlJOR1lRWUF2anBLMjRhMUdPSVhIejFWT2FhSUNGOHlCRHBlbG91YWJqdDQ0TlJBdzBUcHJSQQ?oc=5"
    }
    enriched = enrich_article(sample_article)
    print("Enriched Article:")
    print(enriched)
