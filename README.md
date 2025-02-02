# Greater Dandenong Council Newsletter Generator

An AI-powered system that automatically generates and distributes a professional HTML email newsletter featuring recent news articles relevant to the Greater Dandenong Council.

## Features

- Automated news collection from Google News RSS feeds across four categories:
  - Greater Dandenong News
  - Surrounding Councils
  - State & Federal Announcements
  - Industry News
- AI-powered content enhancement using DeepSeek:
  - Concise two-sentence summaries
  - Relevance scoring (0-100)
  - Relevance explanations
- Responsive HTML email generation
- Automated email distribution via SendGrid
- Comprehensive error handling and logging

## Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following configuration:
```env
# API Keys
OPENROUTER_API_KEY=your_openrouter_api_key
SENDGRID_API_KEY=your_sendgrid_api_key

# Email Configuration
SENDER_EMAIL=your_sender_email
RECIPIENTS=recipient1@example.com,recipient2@example.com

# Newsletter Configuration
NEWSLETTER_FREQUENCY_HOURS=24
EMAIL_SUBJECT=Greater Dandenong Council Newsletter
```

## Configuration Details

### API Keys
- **OPENROUTER_API_KEY**: Required for AI content enhancement using DeepSeek
- **SENDGRID_API_KEY**: Required for email distribution

### Email Settings
- **SENDER_EMAIL**: The email address newsletters will be sent from
- **RECIPIENTS**: Comma-separated list of email addresses to receive the newsletter
- **EMAIL_SUBJECT**: Subject line for the newsletter emails

### Newsletter Settings
- **NEWSLETTER_FREQUENCY_HOURS**: Minimum hours between newsletter generations (default: 24)

## Usage

### Running the Newsletter Generator

```bash
python src/main.py
```

This will:
1. Collect recent news articles
2. Generate AI summaries and relevance scores
3. Create a responsive HTML email
4. Send the newsletter to configured recipients

### Testing Individual Components

Each module can be tested independently:

```bash
# Test news collection
python src/news_collector.py

# Test AI enhancement
python src/ai_enhancement.py

# Test email sending
python src/email_sender.py
```

## Architecture

### 1. News Collection (`news_collector.py`)
- Uses Google News RSS feeds
- Filters articles by relevance and recency
- Ensures 3-5 articles per category
- Excludes specific domains (e.g., greaterdandenong.vic.gov.au)

### 2. AI Enhancement (`ai_enhancement.py`)
- Connects to DeepSeek via OpenRouter API
- Generates article summaries
- Calculates relevance scores
- Provides relevance explanations

### 3. HTML Generation (`main.py`)
- Uses DeepSeek for template generation
- Ensures mobile responsiveness
- Implements inline CSS styling
- Maintains email client compatibility

### 4. Email Distribution (`email_sender.py`)
- Handles SendGrid integration
- Manages recipient lists
- Tracks delivery status
- Implements error handling

## Error Handling

The system implements comprehensive error handling:

1. **News Collection**
   - Handles RSS feed failures
   - Filters invalid articles
   - Ensures minimum article requirements

2. **AI Enhancement**
   - Handles API timeouts and errors
   - Provides fallback summaries
   - Validates AI responses

3. **Email Distribution**
   - Tracks delivery failures
   - Handles invalid recipients
   - Logs delivery status

## Logging

Logs are stored in the following files:
- `newsletter.log`: General operation logs
- `error.log`: Error-specific logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Here]
