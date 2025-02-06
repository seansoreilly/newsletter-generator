import logging
import traceback
import sys
from datetime import datetime

def generate_newsletter(generator):
    """Generate and send the newsletter if the frequency threshold is met"""
    if not generator.should_generate():
        hours_remaining = generator.frequency_hours - (
            (datetime.now() - generator.last_run).total_seconds() / 3600)
        logging.info("Skipping newsletter generation - next run in %.1f hours",
                     hours_remaining)
        return

    try:
        # 1. Collect news articles
        logging.info("Collecting news articles...")
        articles = generator.collect_news()
        if not articles:
            logging.error("No articles collected")
            return

        logging.info("Collected %d articles across categories", len(articles))

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
        enriched_articles = generator.enrich_articles(articles)
        if not enriched_articles:
            logging.error("No articles were successfully enriched")
            return

        # 3. Generate HTML email using DeepSeek
        logging.info("Generating HTML email template...")
        html_content = generator.generate_html(enriched_articles)

        # 4. Send via SendGrid
        logging.info("Sending newsletter via SendGrid...")
        send_email(html_content)

        # Update last run timestamp
        generator.last_run = datetime.now()
        logging.info("Newsletter generation completed successfully!")

    except Exception as e:
        logging.error("Newsletter generation failed!")
        logging.error("Error details: %s", str(e))
        logging.error("Stack trace:\n%s", traceback.format_exc())
        sys.exit(1) 