# Power Papers - Project Guide

## Overview
전력 관련 최신 기술 논문을 수집/공유하는 웹 시스템. 카카오톡 공유 지원.

## Tech Stack
- Flask + Flask-SQLAlchemy + Flask-Admin
- APScheduler (매시간 크롤링)
- Bootstrap 5 + HTMX (카드형 피드 UI)
- SQLite (로컬)

## Project Structure
```
C:\dev\daq\
├── run.py              # 실행 파일
├── config.py           # 설정 (DB, Kakao API, KCI)
├── requirements.txt
├── AGENTS.md           # ← 이 파일 (나침반)
├── .githooks/
│   └── pre-commit      # Git pre-commit hook
├── docs/               # 상세 지침 모음
│   ├── git-workflow.md
│   ├── deployment.md
│   ├── api-keys.md
│   ├── crawlers.md
│   ├── kakao.md
│   └── changelog.md
├── app/
│   ├── __init__.py     # Flask 앱 팩토리 + 기본 검색어 시드
│   ├── models.py       # Paper, SearchKeyword, CrawlLog 모델
│   ├── admin.py        # Flask-Admin (수동 논문 등록)
│   ├── scheduler.py    # APScheduler (매시간 크롤링)
│   ├── views/
│   │   ├── feed.py     # 메인 피드, 상세보기, /health
│   │   ├── search.py   # HTMX 검색/필터
│   │   ├── kakao.py    # Kakao OAuth + 나에게 보내기
│   │   ├── settings.py # 검색어 관리
│   │   └── logs.py     # 크롤 로그 게시판 (/logs)
│   ├── crawlers/
│   │   ├── base.py        # 공통 (키워드 로드, 로깅)
│   │   ├── arxiv.py       # arXiv API (공개)
│   │   ├── ieee.py        # IEEE Xplore REST API
│   │   ├── openalex.py    # OpenAlex API (오픈액세스)
│   │   ├── crossref.py    # Crossref API (DOI 기반)
│   │   ├── kci.py         # KCI 웹 스크래핑 (한국 IP)
│   │   ├── kci_openapi.py # KCI Open API (키 필요)
│   │   └── kee.py         # (deprecated) DBpia
│   ├── templates/
│   │   ├── base.html, feed.html, logs.html
│   │   ├── _paper_cards.html, settings.html
│   │   └── admin_edit.html
│   └── static/css/
│       └── style.css
```

## Run
```bash
cd C:\dev\daq
.\venv\Scripts\python run.py
# http://localhost:5000
# Admin: http://localhost:5000/admin/
```

## Features
| Feature | Route | Description |
|---------|-------|-------------|
| Feed | `/` | 카드형 최신 논문 피드 |
| Detail | `/papers/<id>` | 논문 상세보기 |
| Search | `/search` | 키워드/출처 검색 (HTMX) |
| Settings | `/settings` | 검색어 추가/수정/삭제 |
| Kakao Share | `/kakao/share/<id>` | 카톡 나에게 보내기 |
| Crawl Logs | `/logs` | 크롤러 상태/로그 확인 |
| Health | `/health` | 서버 상태 확인 |
| Admin | `/admin/` | 논문 수동 등록/관리 |

---

## 지침 목차

| 필요한 지침 | 파일 |
|------------|------|
| Git 커밋/푸시 워크플로우, pre-commit hook 설정 | [`docs/git-workflow.md`](docs/git-workflow.md) |
| PythonAnywhere 배포 절차, 문제 해결 | [`docs/deployment.md`](docs/deployment.md) |
| API 키 정보 표 | [`docs/api-keys.md`](docs/api-keys.md) |
| 크롤러 목록, Data Source Status, KCI 등록 | [`docs/crawlers.md`](docs/crawlers.md) |
| KakaoTalk 설정, 메시지 포맷 | [`docs/kakao.md`](docs/kakao.md) |
| 변경 이력 | [`docs/changelog.md`](docs/changelog.md) |
