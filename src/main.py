"""
Newsletter generation module for the Greater Dandenong Council.

This module orchestrates the end-to-end process of generating and sending the council newsletter:
- Collecting news articles across multiple categories using Google News RSS feeds
- Enriching articles with AI-generated summaries and relevance scores via DeepSeek
- Generating a responsive HTML email template using DeepSeek
- Distributing the newsletter via SendGrid

The module handles configuration via environment variables and implements proper error handling
throughout the pipeline to ensure reliable newsletter generation and delivery.
"""

import os
import sys
import logging
import traceback
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv
from news_collector import NewsCollector
from ai_enhancement import enrich_article
from email_sender import send_email


# Ensure src directory is in Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('newsletter.log'),
        logging.StreamHandler()
    ]
)


class NewsletterGenerator:
    """
    A class to generate and send the Greater Dandenong Council newsletter.

    This class handles the end-to-end process of newsletter generation including:
    - Collecting news articles from Google News RSS feeds across multiple categories
    - Enriching articles with AI-generated summaries and relevance scores via DeepSeek
    - Generating a responsive HTML email template using DeepSeek
    - Distributing the newsletter via SendGrid

    Attributes:
        sendgrid_api_key (str): API key for SendGrid email service
        openrouter_api_key (str): API key for OpenRouter/DeepSeek
        frequency_hours (int): Hours between newsletter generations
        last_run (datetime): Timestamp of last newsletter generation
    """

    def __init__(self):
        load_dotenv()
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.frequency_hours = int(
            os.getenv('NEWSLETTER_FREQUENCY_HOURS', '24'))
        self.last_run = None
        self.collector = NewsCollector()

    def should_generate(self) -> bool:
        """Check if enough time has passed since last newsletter generation"""
        if self.last_run is None:
            return True
        hours_since_last_run = (
            datetime.now() - self.last_run).total_seconds() / 3600
        return hours_since_last_run >= self.frequency_hours

    def collect_news(self) -> List[Dict]:
        """Collects news articles from Google News RSS feeds"""
        articles = self.collector.get_articles()

        # Group articles by category and limit to 3-5 per category
        categorized = {}
        for article in articles:
            category = article['category']
            if category not in categorized:
                categorized[category] = []
            if len(categorized[category]) < 5:  # Maximum 5 articles per category
                categorized[category].append(article)

        # Ensure minimum of 3 articles per category where available
        final_articles = []
        for category_articles in categorized.values():
            if len(category_articles) >= 3:  # Only include if minimum threshold met
                final_articles.extend(category_articles)

        return final_articles

    def enrich_articles(self, articles: List[Dict]) -> List[Dict]:
        """Uses OpenRouter to add summaries and relevance to articles"""
        enriched = []
        for article in articles:
            try:
                enriched_article = enrich_article(article)
                enriched.append(enriched_article)
            except Exception as e:
                logging.error("Error enriching article %s: %s",
                              article.get('title'), str(e))
                continue
        return enriched

    def generate_html(self, articles: List[Dict]) -> str:
        """Generate a responsive HTML email using DeepSeek.

        Args:
            articles (List[Dict]): List of enriched articles containing title, url,
                                 image_url, source, summary, relevance_score, and relevance.

        Returns:
            str: A responsive HTML email template with the articles formatted for email clients.
        """
        try:
            # Group articles by category
            categorized = {}
            for article in articles:
                category = article['category']
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(article)

            # Create a structured prompt for DeepSeek
            prompt = {
                "task": "Generate a responsive HTML email newsletter",
                "requirements": {
                    "styling": "Use inline CSS for styling",
                    "responsive": "Must be mobile-responsive",
                    "compatibility": "Ensure email client compatibility"
                },
                "categories": categorized
            }

            # Use the same OpenRouter client setup as in ai_enhancement.py
            import requests
            import json

            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "perplexity/llama-3.1-sonar-huge-128k-online",
                "messages": [
                    {
                        "role": "user",
                        "content": json.dumps(prompt)
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30  # 30 second timeout
            )
            response.raise_for_status()

            # Extract the HTML from the response
            result = response.json()
            html_content = result["choices"][0]["message"]["content"]

            # Validate that it's proper HTML
            if not html_content.strip().startswith('<!DOCTYPE html>'):
                raise ValueError("Generated content is not valid HTML")

            return html_content

        except Exception as e:
            logging.error("Error generating HTML template: %s", str(e))
            # Fallback to a simple but functional template
            return self._generate_fallback_html(articles)

    def _generate_fallback_html(self, articles: List[Dict]) -> str:
        """Generate a simple fallback HTML template if OpenRouter fails"""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .article { margin-bottom: 30px; border-bottom: 1px solid #eee; }
        img { max-width: 100%; height: auto; }
    </style>
</head>
<body>
"""
        # Group articles by category
        categorized = {}
        for article in articles:
            category = article['category']
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(article)

        # Generate HTML for each category
        for category, category_articles in categorized.items():
            html += f'<h2>{category}</h2>'
            for article in category_articles:
                html += f"""
    <div class="article">
        <h3>{article.get("title")}</h3>
        <p><em>{article.get("source", "Unknown Source")}</em></p>
        <img src="{article.get("image_url")}" alt="Article Image">
        <p>{article.get("summary")}</p>
        <p><strong>Relevance Score:</strong> {article.get("relevance_score")}</p>
        <p>{article.get("relevance")}</p>
        <p><a href="{article.get("url")}">Read More</a></p>
    </div>
"""
        html += f"""
    <div style="text-align: center; margin-top: 20px; color: #666;">
        <p>&copy; {datetime.now().year} Greater Dandenong Council. All rights reserved.</p>
    </div>
</body>
</html>
"""
        return html

    def generate_newsletter(self):
        """Generate and send the newsletter if the frequency threshold is met"""
        if not self.should_generate():
            hours_remaining = self.frequency_hours - (
                (datetime.now() - self.last_run).total_seconds() / 3600)
            logging.info("Skipping newsletter generation - next run in %.1f hours",
                         hours_remaining)
            return

        try:
            # 1. Collect news articles
            logging.info("Collecting news articles...")
            articles = self.collect_news()
            if not articles:
                logging.error("No articles collected")
                return

            logging.info(
                "Collected %d articles across categories", len(articles))

            # Log article distribution
            categories = {}
            for article in articles:
                cat = article['category']
                if cat not in categories:
                    categories[cat] = 0
                categories[cat] += 1

            for category, count in categories.items():
                logging.info("Category '%s': %d articles", category, count)

            # 2. Generate summaries and relevance using DeepSeek
            logging.info("Enriching articles with AI content...")
            enriched_articles = self.enrich_articles(articles)
            if not enriched_articles:
                logging.error("No articles were successfully enriched")
                return

            # 3. Generate HTML email using DeepSeek
            logging.info("Generating HTML email template...")
            html_content = self.generate_html(enriched_articles)

            # 4. Send via SendGrid
            logging.info("Sending newsletter via SendGrid...")
            send_email(html_content)

            # Update last run timestamp
            self.last_run = datetime.now()
            logging.info("Newsletter generation completed successfully!")

        except Exception as e:
            logging.error("Newsletter generation failed!")
            logging.error("Error details: %s", str(e))
            logging.error("Stack trace:\n%s", traceback.format_exc())
            sys.exit(1)


if __name__ == "__main__":
    logging.info("Starting newsletter generation process...")

    # Verify environment variables
    required_vars = ['SENDGRID_API_KEY',
                     'OPENROUTER_API_KEY', 'SENDER_EMAIL', 'RECIPIENTS']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logging.error("Missing required environment variables: %s",
                      ', '.join(missing_vars))
        sys.exit(1)

    try:
        # Initialize newsletter generator
        logging.info("Initializing newsletter generator...")
        generator = NewsletterGenerator()

        # Test article collection
        logging.info("Testing article collection...")
        articles = generator.collect_news()
        logging.info(f"Collected {len(articles)} articles across categories")

        # Log article distribution
        categories = {}
        for article in articles:
            cat = article['category']
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1

        for category, count in categories.items():
            logging.info("Category '%s': %d articles", category, count)

        # Test article enrichment
        logging.info("Testing article enrichment...")
        enriched = generator.enrich_articles(
            articles[:2])  # Test with 2 articles
        if enriched:
            logging.info("Article enrichment successful")
            logging.info("Sample enrichment for '%s':", enriched[0]['title'])
            logging.info("- Summary: %s...", enriched[0]['summary'][:100])
            logging.info("- Relevance Score: %s",
                         enriched[0]['relevance_score'])

        # Test HTML generation
        logging.info("Testing HTML generation...")
        html = generator.generate_html(enriched)
        if html and html.strip().startswith('<!DOCTYPE html>'):
            logging.info("HTML generation successful")

        # Test email sending
        if input("Send test email? (y/n): ").lower() == 'y':
            logging.info("Sending test email...")
            send_email(html)
            logging.info("Test email sent successfully")

        logging.info("All components tested successfully!")

        if input("Run full newsletter generation? (y/n): ").lower() == 'y':
            logging.info("Starting full newsletter generation...")
            generator.generate_newsletter()
            logging.info("Newsletter generation completed successfully!")

    except Exception as e:
        logging.error("Newsletter generation failed!")
        logging.error("Error details: %s", str(e))
        logging.error("Stack trace:\n%s", traceback.format_exc())
        sys.exit(1)
