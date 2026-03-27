from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models, schemas
from .sentiment import analyzer


def create_movie(db: Session, payload: schemas.MovieCreate) -> models.Movie:
    movie = models.Movie(**payload.model_dump())
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


def get_movies(db: Session) -> list[schemas.MovieListItem]:
    movies = db.query(models.Movie).order_by(models.Movie.id.desc()).all()
    output = []

    for movie in movies:
        review_count = len(movie.reviews)
        avg_score = 0.0
        if review_count > 0:
            avg_score = sum(review.sentiment_score for review in movie.reviews) / review_count

        output.append(
            schemas.MovieListItem(
                id=movie.id,
                title=movie.title,
                release_date=movie.release_date,
                director=movie.director,
                genre=movie.genre,
                poster_url=movie.poster_url,
                created_at=movie.created_at,
                average_sentiment_score=round(float(avg_score), 4),
                review_count=review_count,
            )
        )

    return output


def get_movie(db: Session, movie_id: int) -> models.Movie | None:
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()


def delete_movie(db: Session, movie_id: int) -> bool:
    movie = get_movie(db, movie_id)
    if movie is None:
        return False

    db.delete(movie)
    db.commit()
    return True


def create_review(db: Session, payload: schemas.ReviewCreate) -> models.Review:
    sentiment = analyzer.analyze(payload.content)

    review = models.Review(
        movie_id=payload.movie_id,
        author=payload.author,
        content=payload.content,
        sentiment_label=sentiment.label,
        sentiment_score=round(float(sentiment.score), 4),
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_reviews(db: Session, limit: int | None = None) -> list[models.Review]:
    query = db.query(models.Review).order_by(models.Review.created_at.desc())
    if limit is not None:
        query = query.limit(limit)
    return query.all()


def get_reviews_by_movie(db: Session, movie_id: int) -> list[models.Review]:
    return (
        db.query(models.Review)
        .filter(models.Review.movie_id == movie_id)
        .order_by(models.Review.created_at.desc())
        .all()
    )


def delete_review(db: Session, review_id: int) -> bool:
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if review is None:
        return False

    db.delete(review)
    db.commit()
    return True


def get_movie_rating(db: Session, movie_id: int) -> schemas.MovieRating:
    avg_score, review_count = (
        db.query(func.avg(models.Review.sentiment_score), func.count(models.Review.id))
        .filter(models.Review.movie_id == movie_id)
        .one()
    )

    return schemas.MovieRating(
        movie_id=movie_id,
        average_sentiment_score=round(float(avg_score or 0.0), 4),
        review_count=int(review_count or 0),
    )
