"""News ingestion and sentiment scoring."""
from __future__ import annotations

import datetime as dt
import logging
import os
from dataclasses import dataclass
from typing import List, Tuple

import requests
from transformers import pipeline

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    published_at: dt.datetime
    title: str
    url: str
    sentiment: float


class NewsSentimentClient:
    """Fetch crypto headlines and estimate sentiment using a transformer pipeline."""

    NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

    def __init__(self, model_name: str = "ProsusAI/finbert") -> None:
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            raise RuntimeError("NEWS_API_KEY missing. Add it to your .env file.")
        self._api_key = api_key
        self._sentiment_pipeline = pipeline("sentiment-analysis", model=model_name)

    def fetch_news(self, query: str = "cryptocurrency") -> List[NewsItem]:
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 20,
        }
        headers = {"X-Api-Key": self._api_key}
        resp = requests.get(self.NEWS_ENDPOINT, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        articles = data.get("articles", [])
        results: List[NewsItem] = []
        for article in articles:
            title = article.get("title") or ""
            if not title:
                continue
            inference = self._sentiment_pipeline(title)[0]
            score = inference["score"] if inference["label"] == "positive" else -inference["score"]
            published_at = dt.datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00"))
            results.append(
                NewsItem(
                    published_at=published_at,
                    title=title,
                    url=article.get("url", ""),
                    sentiment=score,
                )
            )
        logger.info("Fetched %s news items for query '%s'", len(results), query)
        return results

    def summarise_sentiment(
        self, lookback_minutes: int = 180, query: str = "cryptocurrency"
    ) -> Tuple[float, List[NewsItem]]:
        now = dt.datetime.now(dt.timezone.utc)
        items = self.fetch_news(query)
        recent = [item for item in items if now - item.published_at <= dt.timedelta(minutes=lookback_minutes)]
        if not recent:
            return 0.0, []
        sentiment = sum(item.sentiment for item in recent) / len(recent)
        return sentiment, recent
