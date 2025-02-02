"""
News collection module for the Greater Dandenong Council newsletter.

This module handles fetching news articles from Google News RSS feeds across multiple categories:
- Greater Dandenong News
- Surrounding Councils 
- State & Federal Announcements
- Industry News

Articles are filtered by relevance and recency, excluding specific domains where appropriate.
Each article is collected with metadata including title, URL, source, and image URL.

The module uses feedparser to process RSS feeds and implements rate limiting and error handling
for reliable article collection.
"""

import logging
from typing import List, Dict
from urllib.parse import quote
from datetime import datetime, timedelta, timezone
import calendar
import feedparser

# Constant to limit the number of articles per category
ARTICLE_LIMIT = 10


class NewsCollector:
    """Collect articles for all categories"""

    def __init__(self):
        self.base_url = "https://news.google.com/rss/search?q={query}&hl=en-AU&gl=AU&ceid=AU:en&output=rss"
        self.categories = {
            "Greater Dandenong News": {
                "query": '"Greater Dandenong" OR "City of Greater Dandenong" -weather -forecast -temperature when:3d',
                "excluded_domains": ["greaterdandenong.vic.gov.au"]
            },
            "Surrounding Councils": {
                "query": '(casey OR kingston OR monash OR frankston) -weather -forecast when:3d',
                "excluded_domains": []
            },
            "State & Federal Announcements": {
                "query": '"Victorian Government" "local council" OR "Victorian Premier" "Greater Dandenong" -weather -temperature when:3d',
                "excluded_domains": []
            },
            "Industry News": {
                "query": '"local government" "Victoria" OR "council innovation" OR "municipal development" -weather -forecast when:3d',
                "excluded_domains": []
            }
        }

    def get_articles(self) -> List[Dict]:
        """Collect articles for all categories"""
        all_articles = []

        for category, search_params in self.categories.items():
            try:
                category_articles = self.fetch_category_articles(
                    category, search_params)
                all_articles.extend(category_articles)
            except Exception as e:
                logging.error(f"Error fetching articles for {
                              category}: {str(e)}")
                continue

        return all_articles

    def fetch_category_articles(self, category: str, search_params: Dict) -> List[Dict]:
        """Fetch articles for a specific category"""
        encoded_query = quote(search_params["query"])
        feed_url = self.base_url.format(query=encoded_query) + "&sort=date"
        feed = feedparser.parse(feed_url)
        category_articles = []
        # Updated UTC time handling
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=3)

        for entry in feed.entries[:ARTICLE_LIMIT]:
            if hasattr(entry, 'published_parsed'):
                timestamp = calendar.timegm(entry.published_parsed)
                pub_date = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                if pub_date < cutoff_date:
                    print(f"Skipping old article from {
                          pub_date}: {entry.title[:50]}...")
                    continue
            else:
                print(f"Skipping article without date: {entry.title[:50]}...")
                continue

            if self._validate_article(entry, search_params["excluded_domains"]):
                category_articles.append({
                    "category": category,
                    "title": entry.title,
                    "url": entry.link,
                    "source": entry.source.title if hasattr(entry, 'source') else "Google News",
                    "image_url": self._extract_image_url(entry),
                    "date": pub_date.strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else 'Unknown'
                })

        return category_articles

    def _validate_article(self, entry, excluded_domains: List[str]) -> bool:
        """Validate article and check against excluded domains"""
        if not hasattr(entry, 'title'):
            print(f"Rejecting article - missing title: {entry.link}")
            return False

        for domain in excluded_domains:
            if domain in entry.link:
                print(f"Filtered out article from {domain}: {entry.link}")
                return False

        return True

    def _extract_image_url(self, entry) -> str:
        """Extract image URL from entry or return a default image"""
        # Try to find image in media content
        if hasattr(entry, 'media_content'):
            for media in entry.media_content:
                if media.get('type', '').startswith('image/'):
                    return media['url']

        # If no image found, return a default image URL
        return "https://via.placeholder.com/300x200"


if __name__ == "__main__":
    collector = NewsCollector()

    # Test specific category
    TEST_CATEGORY = "Greater Dandenong News"
    search_params = collector.categories[TEST_CATEGORY]

    print(f"Testing category: {TEST_CATEGORY}")
    print(f"Search URL: {collector.base_url.format(
        query=quote(search_params['query']))}")

    articles = collector.fetch_category_articles(TEST_CATEGORY, search_params)

    for article in articles:
        print(f"\nTitle: {article['title']}")
        print(f"URL: {article['url']}")
        print(f"Image: {article['image_url']}")
        print("-" * 80)
