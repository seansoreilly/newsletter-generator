import os
import sys
import logging
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.newsletter import Newsletter
from news_collector import NewsCollector
from ai_enhancement import enrich_article
from email_sender import send_email
from newsletter_generator import generate_newsletter


class NewsletterService:
    def __init__(self):
        load_dotenv()
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.frequency_hours = int(
            os.getenv('NEWSLETTER_FREQUENCY_HOURS', '24'))
        self.collector = NewsCollector()
        self.newsletter = Newsletter()

    def should_generate(self) -> bool:
        if self.newsletter.last_run is None:
            return True
        hours_since_last_run = (
            datetime.now() - self.newsletter.last_run).total_seconds() / 3600
        return hours_since_last_run >= self.frequency_hours

    def collect_news(self, limit: int = None) -> List[Dict]:
        articles = self.collector.get_articles()
        if limit:
            articles = articles[:limit]
        self.newsletter.add_articles(articles)
        return articles

    def enrich_articles(self, articles: List[Dict]) -> List[Dict]:
        enriched = []
        for article in articles:
            try:
                enriched_article = enrich_article(article)
                enriched.append(enriched_article)
            except Exception as e:
                logging.error("Error enriching article %s: %s",
                              article.get('title'), str(e))
                continue
        self.newsletter.set_enriched_articles(enriched)
        return enriched

    def generate_html(self) -> str:
        html = generate_newsletter(self.newsletter.enriched_articles)
        self.newsletter.set_html_content(html)
        return html

    def send_newsletter(self) -> bool:
        try:
            send_email(self.newsletter.html_content)
            self.newsletter.update_last_run()
            return True
        except Exception as e:
            logging.error("Failed to send newsletter: %s", str(e))
            return False


if __name__ == "__main__":
    # Configure logging for tests
    logging.basicConfig(level=logging.INFO)

    # Initialize service
    service = NewsletterService()

    # Test frequency check
    assert service.should_generate() == True, "Should generate when no last run"

    # Test article collection
    articles = service.collect_news(limit=2)
    assert len(articles) <= 2, "Article limit not respected"
    assert len(service.newsletter.categories) > 0, "Categories not populated"

    # Test article enrichment
    if articles:
        enriched = service.enrich_articles(
            articles[:1])  # Test with one article
        assert len(enriched) <= 1, "Enrichment count mismatch"
        if enriched:
            assert 'summary' in enriched[0], "Enrichment missing summary"

    print("All NewsletterService tests passed!")
