import feedparser
from bs4 import BeautifulSoup
import re
from typing import List, Dict

# Pre-defined RSS feeds for demonstration
RSS_FEEDS = {
    "Technology": "https://news.google.com/rss/search?q=technology&hl=en-US&gl=US&ceid=US:en",
    "Business": "https://news.google.com/rss/search?q=business&hl=en-US&gl=US&ceid=US:en",
    "Science": "https://news.google.com/rss/search?q=science&hl=en-US&gl=US&ceid=US:en",
    "Health": "https://news.google.com/rss/search?q=health&hl=en-US&gl=US&ceid=US:en",
    "World": "https://news.google.com/rss/search?q=world&hl=en-US&gl=US&ceid=US:en"
}

def clean_html(raw_html: str) -> str:
    """Removes HTML tags from a string."""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text()
    # Remove extra whitespace
    return re.sub(r'\s+', ' ', text).strip()

def fetch_news(topic: str, max_articles: int = 15) -> List[Dict]:
    """
    Fetches news articles from Google News RSS feed based on topic.
    Returns a list of dictionaries containing title, link, summary, and published date.
    """
    if topic in RSS_FEEDS:
        rss_url = RSS_FEEDS[topic]
    else:
        # Construct search query for custom topics
        query = topic.replace(" ", "+")
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        
    try:
        feed = feedparser.parse(rss_url)
        articles = []
        
        for entry in feed.entries[:max_articles]:
            summary_clean = clean_html(entry.summary) if hasattr(entry, 'summary') else "No summary available."
            
            # Google news RSS sometimes puts the full article link inside a google news redirect, 
            # but we can try to use it as is for demonstration.
            article = {
                "title": entry.title,
                "link": entry.link,
                "summary": summary_clean,
                "published": entry.published if hasattr(entry, 'published') else "Unknown"
            }
            articles.append(article)
            
        return articles
    
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

if __name__ == "__main__":
    # Test the function
    news = fetch_news("Technology", max_articles=2)
    for n in news:
        print(f"Title: {n['title']}\nSummary: {n['summary'][:100]}...\n")
