from datetime import datetime
from typing import List, Dict


class Newsletter:
    def __init__(self):
        self.articles: List[Dict] = []
        self.enriched_articles: List[Dict] = []
        self.html_content: str = ""
        self.last_run: datetime = None
        self.categories: Dict[str, int] = {}

    def add_articles(self, articles: List[Dict]):
        self.articles = articles
        # Update category distribution
        self.categories = {}
        for article in articles:
            cat = article['category']
            if cat not in self.categories:
                self.categories[cat] = 0
            self.categories[cat] += 1

    def set_enriched_articles(self, articles: List[Dict]):
        self.enriched_articles = articles

    def set_html_content(self, html: str):
        self.html_content = html

    def update_last_run(self):
        self.last_run = datetime.now()


if __name__ == "__main__":
    # Test the Newsletter class
    newsletter = Newsletter()

    # Test adding articles
    test_articles = [
        {"title": "Test 1", "category": "Sports"},
        {"title": "Test 2", "category": "Sports"},
        {"title": "Test 3", "category": "Politics"}
    ]
    newsletter.add_articles(test_articles)

    # Verify category counting
    assert newsletter.categories["Sports"] == 2
    assert newsletter.categories["Politics"] == 1

    # Test enriched articles
    newsletter.set_enriched_articles([{"title": "Enriched"}])
    assert len(newsletter.enriched_articles) == 1

    # Test HTML content
    newsletter.set_html_content("<html>Test</html>")
    assert newsletter.html_content == "<html>Test</html>"

    # Test last run
    newsletter.update_last_run()
    assert newsletter.last_run is not None

    print("All Newsletter tests passed!")
