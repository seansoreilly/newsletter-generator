# Project Instructions: AI Agent for Email Newsletter Generation

## Project Overview

Develop an AI agent designed to create and send a professional HTML email newsletter for the Greater Dandenong Council. The newsletter will feature recent news articles organized into four distinct categories:

1. **Greater Dandenong News**
2. **Surrounding Councils**
3. **State & Federal Announcements**
4. **Industry News**

## Technical Architecture

### 1. News Article Collection

- Use Google News RSS feeds to gather articles for each category
- Each article will be stored in JSON format with the following structure:

```json
{
  "category": "Category Name",
  "title": "Article Title",
  "url": "Article URL",
  "image_url": "Image URL",
  "source": "Source Name"
}
```

### 2. AI Content Enhancement

Using DeepSeek via the OpenRouter API to

- Check that the individual articles are relevant to Greater Dandenong Council
- Generate a concise 2-sentence summary
- Provide a relevance score between 0 and 100
- Provide a relevance explanation for Greater Dandenong Council

Enriched article structure:

```json
{
  "category": "Category Name",
  "title": "Article Title",
  "url": "Article URL",
  "image_url": "Image URL",
  "source": "Source Name",
  "summary": "AI-generated summary",
  "relevance_score": "AI-generated relevance score",
  "relevance": "AI-generated relevance explanation"
}
```

### 3. HTML Email Generation

- Uses inline CSS for styling
- Is mobile-responsive
- Includes proper image handling
- Features clear category separation
- Maintains email client compatibility

### 4. Email Distribution

SendGrid will handle the email distribution with:

- Proper error handling
- Delivery tracking
- Recipient list management

## Article Requirements

- Exclude articles from `greaterdandenong.vic.gov.au`
- Only use real, verified news articles
- Articles must be recent (within the last week)
- Each category should have 3-5 articles

## API Integration

### Google News

- Used for initial article collection
- Filter by region and relevance
- Collect required article metadata

### OpenRouter API

- Two main functions:
  1. Generate article summaries, relevance explanations and relevance scores.  The AI model used for this must have access to the internet.
  2. Create the complete HTML email template

### SendGrid API

- Handle email distribution
- Track delivery status
- Manage recipient lists

## Error Handling Requirements

1. Failed API calls must be logged
2. Email delivery failures must be reported
3. Invalid article data must be filtered out

## Configuration Requirements

The system should accept the following configuration:

- API keys (OpenRouter, SendGrid)
- Recipient list
- Email subject format
- Frequency of newsletter generation

## Success Criteria

1. Articles are properly categorized
2. Summaries are concise and relevant
3. HTML email renders correctly across devices
4. Successful delivery to all recipients
5. All content is recent and verified

## Notes

- The system is designed to run automatically
- All API interactions should include proper error handling
- Content quality should be consistently high
