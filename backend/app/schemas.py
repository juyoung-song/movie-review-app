from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


SentimentLabel = Literal["positive", "neutral", "negative"]


class MovieCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    release_date: str = Field(..., min_length=4, max_length=20)
    director: str = Field(..., min_length=1, max_length=100)
    genre: str = Field(..., min_length=1, max_length=100)
    poster_url: str = Field(..., min_length=1, max_length=500)


class MovieRead(BaseModel):
    id: int
    title: str
    release_date: str
    director: str
    genre: str
    poster_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class MovieListItem(MovieRead):
    average_sentiment_score: float = 0.0
    review_count: int = 0


class ReviewCreate(BaseModel):
    movie_id: int
    author: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)


class ReviewRead(BaseModel):
    id: int
    movie_id: int
    author: str
    content: str
    sentiment_label: SentimentLabel
    sentiment_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class MovieRating(BaseModel):
    movie_id: int
    average_sentiment_score: float
    review_count: int
