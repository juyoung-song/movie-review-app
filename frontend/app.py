from __future__ import annotations

from datetime import datetime
import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
TIMEOUT = 8

st.set_page_config(page_title="Movie Review Sentiment", layout="wide")
st.title("Movie Review Sentiment Web App")
st.caption("Streamlit + FastAPI + SQLite")


def request_json(method: str, path: str, **kwargs):
    try:
        response = requests.request(method, f"{BACKEND_URL}{path}", timeout=TIMEOUT, **kwargs)
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            return None, f"{response.status_code}: {detail}"
        if not response.text:
            return {}, None
        return response.json(), None
    except requests.RequestException as exc:
        return None, str(exc)


def load_movies():
    data, error = request_json("GET", "/movies")
    if error:
        st.error(f"영화 목록 조회 실패: {error}")
        return []
    return data


def load_reviews_by_movie(movie_id: int):
    data, error = request_json("GET", f"/movies/{movie_id}/reviews")
    if error:
        st.error(f"영화별 리뷰 조회 실패: {error}")
        return []
    return data


def sentiment_badge(label: str, score: float) -> str:
    if label == "positive":
        icon = "🟢"
    elif label == "negative":
        icon = "🔴"
    else:
        icon = "🟡"
    return f"{icon} {label} ({score:.2f})"


with st.sidebar:
    st.subheader("영화 추가")
    with st.form("create_movie_form", clear_on_submit=True):
        title = st.text_input("제목")
        release_date = st.text_input("개봉일", placeholder="YYYY-MM-DD")
        director = st.text_input("감독")
        genre = st.text_input("장르")
        poster_url = st.text_input("포스터 URL")
        submit_movie = st.form_submit_button("등록")

    if submit_movie:
        payload = {
            "title": title.strip(),
            "release_date": release_date.strip(),
            "director": director.strip(),
            "genre": genre.strip(),
            "poster_url": poster_url.strip(),
        }
        if not all(payload.values()):
            st.warning("모든 값을 입력해주세요.")
        else:
            _, error = request_json("POST", "/movies", json=payload)
            if error:
                st.error(f"영화 등록 실패: {error}")
            else:
                st.success("영화를 등록했습니다.")
                st.rerun()

movies = load_movies()

left, right = st.columns([1.6, 1.2], gap="large")

with left:
    st.subheader("영화 목록")
    if not movies:
        st.info("등록된 영화가 없습니다.")
    else:
        for movie in movies:
            with st.container(border=True):
                poster_col, info_col = st.columns([1, 2])
                with poster_col:
                    st.image(movie["poster_url"], use_container_width=True)
                with info_col:
                    st.markdown(f"### {movie['title']}")
                    st.write(f"개봉일: {movie['release_date']}")
                    st.write(f"감독: {movie['director']}")
                    st.write(f"장르: {movie['genre']}")
                    st.write(f"평균 감성 점수: {movie['average_sentiment_score']:.2f}")
                    st.write(f"리뷰 수: {movie['review_count']}")

                    _, err = request_json("GET", f"/movies/{movie['id']}/rating")
                    if err:
                        st.caption(f"평점 조회 오류: {err}")

                    if st.button("영화 삭제", key=f"delete_movie_{movie['id']}"):
                        _, error = request_json("DELETE", f"/movies/{movie['id']}")
                        if error:
                            st.error(f"삭제 실패: {error}")
                        else:
                            st.success("영화를 삭제했습니다.")
                            st.rerun()

with right:
    st.subheader("리뷰 등록")
    if not movies:
        st.info("리뷰를 작성하려면 먼저 영화를 등록해주세요.")
    else:
        movie_options = {f"{m['id']} - {m['title']}": m["id"] for m in movies}
        with st.form("create_review_form", clear_on_submit=True):
            selected_label = st.selectbox("영화 선택", options=list(movie_options.keys()))
            author = st.text_input("작성자")
            content = st.text_area("리뷰 내용", height=140)
            submit_review = st.form_submit_button("리뷰 등록")

        if submit_review:
            payload = {
                "movie_id": movie_options[selected_label],
                "author": author.strip(),
                "content": content.strip(),
            }
            if not payload["author"] or not payload["content"]:
                st.warning("작성자와 리뷰 내용을 입력해주세요.")
            else:
                result, error = request_json("POST", "/reviews", json=payload)
                if error:
                    st.error(f"리뷰 등록 실패: {error}")
                else:
                    st.success("리뷰가 등록되었습니다.")
                    st.markdown("**감성 분석 결과**")
                    st.write(sentiment_badge(result["sentiment_label"], result["sentiment_score"]))
                    st.rerun()

    st.subheader("영화별 최근 리뷰 10개")
    if not movies:
        st.caption("영화가 없어서 조회할 리뷰가 없습니다.")
    else:
        selected_movie_for_reviews = st.selectbox(
            "리뷰를 볼 영화 선택",
            options=[f"{m['id']} - {m['title']}" for m in movies],
            key="movie_reviews_select",
        )
        selected_movie_id = int(selected_movie_for_reviews.split(" - ")[0])
        movie_reviews = load_reviews_by_movie(selected_movie_id)

        latest_reviews = movie_reviews[:10]

        if not latest_reviews:
            st.caption("이 영화에 등록된 리뷰가 없습니다.")
        else:
            rows = []
            for review in latest_reviews:
                created_at = review.get("created_at")
                if created_at:
                    try:
                        created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        pass
                rows.append(
                    {
                        "review_id": review["id"],
                        "registered_at": created_at,
                        "author": review["author"],
                        "content": review["content"],
                        "sentiment": f"{review['sentiment_label']} ({review['sentiment_score']:.2f})",
                    }
                )
            st.dataframe(rows, use_container_width=True, hide_index=True)

            selected_review_id = st.selectbox(
                "삭제할 리뷰 ID 선택",
                options=[row["review_id"] for row in rows],
                key=f"delete_review_select_{selected_movie_id}",
            )
            if st.button("선택 리뷰 삭제", key=f"delete_review_btn_{selected_movie_id}"):
                _, error = request_json("DELETE", f"/reviews/{selected_review_id}")
                if error:
                    st.error(f"리뷰 삭제 실패: {error}")
                else:
                    st.success("리뷰를 삭제했습니다.")
                    st.rerun()
