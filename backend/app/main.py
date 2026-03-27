from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, schemas
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Movie Review Sentiment API",
    description="영화/리뷰 CRUD와 리뷰 감성 분석 기능을 제공하는 API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Movie Review Sentiment API is running"}


@app.post("/movies", response_model=schemas.MovieRead, summary="영화 등록", status_code=status.HTTP_201_CREATED)
def create_movie(payload: schemas.MovieCreate, db: Session = Depends(get_db)):
    return crud.create_movie(db, payload)


@app.get("/movies", response_model=List[schemas.MovieListItem], summary="전체 영화 조회")
def read_movies(db: Session = Depends(get_db)):
    return crud.get_movies(db)


@app.get("/movies/{movie_id}", response_model=schemas.MovieRead, summary="특정 영화 조회")
def read_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@app.delete("/movies/{movie_id}", summary="특정 영화 삭제")
def remove_movie(movie_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_movie(db, movie_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"message": "Movie deleted"}


@app.get("/movies/{movie_id}/rating", response_model=schemas.MovieRating, summary="평점 조회")
def read_movie_rating(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return crud.get_movie_rating(db, movie_id)


@app.post("/reviews", response_model=schemas.ReviewRead, summary="리뷰 등록", status_code=status.HTTP_201_CREATED)
def create_review(payload: schemas.ReviewCreate, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, payload.movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    try:
        return crud.create_review(db, payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Sentiment model error: {exc}") from exc


@app.get("/reviews", response_model=List[schemas.ReviewRead], summary="전체 리뷰 조회")
def read_reviews(
    limit: int | None = Query(default=None, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return crud.get_reviews(db, limit=limit)


@app.get("/movies/{movie_id}/reviews", response_model=List[schemas.ReviewRead], summary="특정 영화 리뷰 조회")
def read_movie_reviews(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return crud.get_reviews_by_movie(db, movie_id)


@app.delete("/reviews/{review_id}", summary="리뷰 삭제")
def remove_review(review_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_review(db, review_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted"}
