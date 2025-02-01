from dotenv import load_dotenv
import os
from typing import List, Dict


class NewsletterGenerator:
    def __init__(self):
        load_dotenv()
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')

    def collect_news(self) -> List[Dict]:
        """Collects news articles from NewsAPI"""
        # This will be implemented with actual API calls
        return [
            {
                "category": "Greater Dandenong News",
                "title": "Article Title",
                "url": "https://example.com/article",
                "image_url": "https://example.com/image.jpg",
                "source": "News Source Name"
            }
        ]

    def enrich_articles(self, articles: List[Dict]) -> List[Dict]:
        """Uses DeepSeek to add summaries and relevance to articles"""
        enriched = []
        for article in articles:
            # Will make actual DeepSeek API call here
            enriched_article = {
                **article,
                "summary": "AI-generated 2-sentence summary",
                "relevance": "AI-generated explanation of relevance to Greater Dandenong",
            }
            enriched.append(enriched_article)
        return enriched

    def generate_html(self, articles: List[Dict]) -> str:
        """Uses DeepSeek to generate HTML email from enriched articles"""
        # Will make actual DeepSeek API call here
        return "<html>Generated email content</html>"

    def send_email(self, html_content: str) -> None:
        """Sends the email via SendGrid"""
        # Will implement SendGrid sending logic
        pass

    def generate_newsletter(self):
        # 1. Collect news articles
        articles = self.collect_news()

        # 2. Generate summaries and relevance using DeepSeek
        enriched_articles = self.enrich_articles(articles)

        # 3. Generate HTML email using DeepSeek
        html_content = self.generate_html(enriched_articles)

        # 4. Send via SendGrid
        self.send_email(html_content)
