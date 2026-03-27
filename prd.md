# 🎬 Movie Review Sentiment Web App PRD

---

# 1. 프로젝트 개요 (Overview)

## 1.1 배경

본 프로젝트는 AI 엔지니어링 스프린트의 마지막 미션으로,  
프론트엔드, 백엔드, 그리고 모델 서빙까지 통합된 웹 애플리케이션을 구현하는 것을 목표로 한다.

초기 단계에서는 Python 기초 문제 해결에서 시작하였으나,  
본 미션에서는 실제 서비스 형태의 AI 기반 웹 애플리케이션을 개발한다.

---

## 1.2 목표

- 영화 정보를 관리하는 웹 서비스 구축
- 사용자 리뷰 데이터를 기반으로 감성 분석 수행
- 프론트엔드 + 백엔드 + AI 모델을 통합한 서비스 구현
- 실제 배포 가능한 수준의 프로젝트 완성

---

# 2. 미션 가이드라인 (Requirements)

## 2.1 프론트엔드 (Streamlit)

### 기능

#### 1) 영화 목록 표시
- 제목
- 포스터 이미지
- (옵션) 평균 평점 표시

#### 2) 영화 추가
입력:
- 제목
- 개봉일
- 감독
- 장르
- 포스터 URL

---

### (심화 기능)

#### 3) 리뷰 등록
- 저장된 영화 선택
- 작성자 이름 입력
- 리뷰 내용 입력

#### 4) 리뷰 감성 분석
- 리뷰 작성 후 자동 실행
- 감성 분석 결과 표시

#### 5) 리뷰 표시
- 최근 10개 리뷰 표시
- 항목:
  - 영화 ID
  - 등록일
  - 리뷰 내용
  - 감성 분석 결과

---

### 배포
- Streamlit Cloud 사용

---

### 참고
- 모든 데이터는 **백엔드에서 관리**
- Streamlit 내부 저장 금지

---

## 2.2 백엔드 (FastAPI)

### 기능

#### 1) 영화 관리
- 영화 등록
- 전체 영화 조회
- 특정 영화 조회
- 특정 영화 삭제

---

### (심화 기능)

#### 2) 리뷰 관리
- 리뷰 등록
- 전체 리뷰 조회
- 특정 영화 리뷰 조회
- 리뷰 삭제

#### 3) 평점 조회
- 감성 분석 점수 평균

#### 4) 리뷰 감성 분석
- 적절한 모델 적용
- 경량화 고려

---

## 2.3 제출 요구사항

### 필수 제출물

#### 1) 보고서 PDF
- 서비스 개요
- 서비스 구조도
- 프론트엔드 / 백엔드 / 모델 서빙 설명
- 데이터베이스 구조도 (ERD)
- FastAPI Docs 전체 캡처
- 서비스 동작 캡처 이미지

#### 2) 데이터 조건
- 영화 3개 이상 등록
- 각 영화당 리뷰 10개 이상 등록

#### 3) 코드 제출
- frontend/
- backend/

---

# 3. 시스템 아키텍처 (Architecture)

## 3.1 전체 구조


User
↓
Streamlit (Frontend)
↓ HTTP
FastAPI (Backend)
↓
SQLite DB
↓
Sentiment Model


---

## 3.2 구성 요소

### Frontend
- Streamlit UI
- API 호출 담당

### Backend
- FastAPI REST API
- 데이터 처리 및 저장

### Database
- SQLite
- 영화 / 리뷰 데이터 저장

### AI Model
- 감성 분석 모델
- 리뷰 입력 시 즉시 실행

---

# 4. 데이터 설계 (Database Design)

## 4.1 Movie Table

| 컬럼 | 설명 |
|------|------|
| id | PK |
| title | 영화 제목 |
| release_date | 개봉일 |
| director | 감독 |
| genre | 장르 |
| poster_url | 포스터 |
| created_at | 생성일 |

---

## 4.2 Review Table

| 컬럼 | 설명 |
|------|------|
| id | PK |
| movie_id | FK (Movie) |
| author | 작성자 |
| content | 리뷰 내용 |
| sentiment_label | 감성 결과 |
| sentiment_score | 감성 점수 |
| created_at | 생성일 |

---

## 4.3 관계

- Movie (1) : Review (N)

---

# 5. API 설계 (API Design)

## 5.1 Movie API

### 영화 등록
POST /movies

### 전체 조회
GET /movies

### 단일 조회
GET /movies/{movie_id}

### 삭제
DELETE /movies/{movie_id}

### 평점 조회
GET /movies/{movie_id}/rating

---

## 5.2 Review API

### 리뷰 등록
POST /reviews

### 전체 조회
GET /reviews

### 특정 영화 리뷰 조회
GET /movies/{movie_id}/reviews

### 삭제
DELETE /reviews/{review_id}

---

# 6. 기능 흐름 (User Flow)

## 6.1 영화 등록
1. 사용자 입력
2. Streamlit → FastAPI 요청
3. DB 저장
4. 화면 갱신

---

## 6.2 리뷰 등록 + 감성 분석

1. 리뷰 입력
2. FastAPI 요청
3. 감성 분석 모델 실행
4. 결과 생성 (label, score)
5. DB 저장
6. UI 표시

---

## 6.3 평점 계산

1. 특정 영화 리뷰 조회
2. sentiment_score 평균 계산
3. UI 표시

---

# 7. 개발 단계 (Development Plan)

## Phase 1
- FastAPI 기본 구축
- Movie CRUD 구현

## Phase 2
- Review CRUD 구현

## Phase 3
- 감성 분석 모델 연결

## Phase 4
- Streamlit UI 구현

## Phase 5
- 통합 테스트

## Phase 6
- 배포

---

# 8. 배포 전략 (Deployment)

## Backend
- Render / Railway / Fly.io

## Frontend
- Streamlit Cloud

---

# 9. 기술 스택 (Tech Stack)

- FastAPI
- Streamlit
- SQLite
- SQLAlchemy
- Pydantic
- Transformers (Hugging Face)

---

# 10. 제약사항 (Constraints)

- 데이터는 반드시 백엔드에서 관리
- Streamlit 내부 저장 금지
- 리뷰 작성 시 감성 분석 자동 실행

---

# 11. 성공 기준 (Success Criteria)

- 영화 CRUD 정상 동작
- 리뷰 CRUD 정상 동작
- 감성 분석 결과 정상 출력
- 영화별 평균 점수 계산 가능
- Streamlit UI 정상 동작
- 배포 완료
- 제출 요구사항 충족

---

# 12. 향후 개선 방향 (Future Work)

- 모델 성능 개선
- 한국어 특화 감성 분석 모델 적용
- 사용자 인증 기능
- 추천 시스템 추가
- Redis 캐싱 적용
- PostgreSQL로 확장

---