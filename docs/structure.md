# Project Structure

```
C:\dev\daq\
├── run.py              # 실행 파일
├── config.py           # 설정 (DB, Kakao API, KCI)
├── requirements.txt
├── AGENTS.md           # 나침반
├── .githooks/
│   └── pre-commit      # Git pre-commit hook
├── docs/               # 상세 지침
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
