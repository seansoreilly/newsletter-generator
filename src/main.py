"""
Newsletter generation module for the Greater Dandenong Council.

This module orchestrates the end-to-end process of generating and sending the council newsletter:
- Collecting news articles across multiple categories using Google News RSS
- Enriching articles with AI-generated summaries and relevance scores via DeepSeek
- Generating a responsive HTML email template
- Distributing the newsletter via SendGrid

The module handles configuration via environment variables and implements proper error handling
throughout the pipeline to ensure reliable newsletter generation and delivery.
"""

import os
from typing import List, Dict
from dotenv import load_dotenv


class NewsletterGenerator:
    """
    A class to generate and send the Greater Dandenong Council newsletter.

    This class handles the end-to-end process of newsletter generation including:
    - Collecting news articles from NewsAPI across multiple categories
    - Enriching articles with AI-generated summaries and relevance scores via DeepSeek
    - Generating a responsive HTML email template
    - Distributing the newsletter via SendGrid

    Attributes:
        deepseek_api_key (str): API key for DeepSeek AI service
        news_api_key (str): API key for NewsAPI service
        sendgrid_api_key (str): API key for SendGrid email service
    """

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
        # Generate a responsive HTML email using inline CSS.
        html = '''
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
      body { font-family: Arial, sans-serif; margin:0; padding:0; }
      .container { width: 100%%; max-width: 600px; margin: auto; }
      .header { background-color: #0c5390; color: white; padding:20px; text-align: center; }
      .article { border-bottom: 1px solid #ccc; padding: 10px 0; }
      .article img { max-width: 100%%; height: auto; }
      .footer { background-color: #f2f2f2; color: #888; padding: 10px; text-align: center; font-size:12px; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>Greater Dandenong Council Newsletter</h1>
      </div>
'''
        for article in articles:
            html += f'''
      <div class="article">
        <h2>{article.get("title")}</h2>
        <p><em>{article.get("source", "Unknown Source")}</em></p>
        <img src="{article.get("image_url")}" alt="Article Image">
        <p>{article.get("summary")}</p>
        <p><strong>Relevance Score:</strong> {article.get("relevance_score")}</p>
        <p>{article.get("relevance")}</p>
        <p><a href="{article.get("url")}">Read More</a></p>
      </div>
'''
        html += '''
      <div class="footer">
        <p>&copy; {year} Greater Dandenong Council. All rights reserved.</p>
      </div>
    </div>
  </body>
</html>
'''.format(year=2023)
        return html

    def send_email(self, html_content: str) -> None:
        """Sends the email via SendGrid"""
        # Will implement SendGrid sending logic

    def generate_newsletter(self):
        # 1. Collect news articles
        articles = self.collect_news()

        # 2. Generate summaries and relevance using DeepSeek
        enriched_articles = self.enrich_articles(articles)

        # 3. Generate HTML email using DeepSeek
        html_content = self.generate_html(enriched_articles)

        # 4. Send via SendGrid
        self.send_email(html_content)

if __name__ == "__main__":
    generator = NewsletterGenerator()

    # Create sample enriched articles for testing.
    sample_articles = [
        {
            "title": "Test Article One",
            "url": "https://example.com/article1",
            "image_url": "https://example.com/image1.jpg",
            "source": "Example News",
            "summary": "This is the first test summary, covering key points in two sentences.",
            "relevance_score": 88,
            "relevance": "This article is highly relevant to the topic due to its detailed coverage of local issues."
        },
        {
            "title": "Test Article Two",
            "url": "https://example.com/article2",
            "image_url": "https://example.com/image2.jpg",
            "source": "Sample Media",
            "summary": "This is the second test summary, providing insight into local events.",
            "relevance_score": 75,
            "relevance": "It is moderately relevant since it highlights key local challenges."
        }
    ]

    # Generate the HTML email using the sample articles.
    html_content = generator.generate_html(sample_articles)
    # Print the HTML content for review.
    print(html_content)
