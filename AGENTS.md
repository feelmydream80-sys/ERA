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
├── config.py           # 설정 (DB, Kakao API)
├── requirements.txt
├── AGENTS.md
├── app/
│   ├── __init__.py     # Flask 앱 팩토리 + 기본 검색어 시드
│   ├── models.py       # Paper, SearchKeyword 모델
│   ├── admin.py        # Flask-Admin (수동 논문 등록)
│   ├── scheduler.py    # APScheduler (매시간 크롤링)
│   ├── views/
│   │   ├── feed.py     # 메인 피드, 상세보기, /health
│   │   ├── search.py   # HTMX 검색/필터
│   │   ├── kakao.py    # Kakao OAuth + 나에게 보내기
│   │   └── settings.py # 검색어 관리
│   ├── crawlers/
│   │   ├── base.py     # 공통 (키워드 로드, 로깅)
│   │   ├── arxiv.py    # arXiv API (공개)
│   │   ├── ieee.py     # IEEE Xplore 검색
│   │   ├── kci.py      # KCI (한국학술지)
│   │   └── kee.py      # DBpia (한국 전력/에너지)
│   ├── templates/
│   │   ├── base.html, feed.html, detail.html
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
| Health | `/health` | 서버 상태 확인 |
| Admin | `/admin/` | 논문 수동 등록/관리 |

## Crawlers
- 매시간 APScheduler 실행
- IEEE, arXiv, KCI, DBpia 4개 소스
- Settings 페이지에서 검색어 추가/활성화 가능
- 기본 검색어 20개 (영어 10 + 한국어 10)

## KakaoTalk Setup
1. https://developers.kakao.com 에서 앱 생성
2. "카카오 로그인" 활성화 + Redirect URI: `http://localhost:5000/kakao/callback` (앱 > 플랫폼 키 > REST API 키 내부)
3. "카카오톡 메시지 전송" 동의항목 설정 (카카오 로그인 > 동의항목 > 접근권한)
4. "카카오톡 메시지" 제품 설정에서 "나에게 보내기" 활성화 (필요시 권한 신청)
5. REST API 키 + Client Secret을 `config.py`에 입력 (또는 환경변수)

## KakaoTalk Message Format
- **Type**: text template (object_type: "text")
- **API URL**: `POST https://kapi.kakao.com/v2/api/talk/memo/default/send`
- **Button**: "View Paper" → 원문 링크
- **Translation**: Google Translate (deep-translator) 자동 번역 → 한글 제공

Send 예시:
```
📄 A Deep Learning Approach for Smart Grid Optimization
✍️ Kim, Lee, Park
🏷️ IEEE

📝 Abstract
This paper presents a novel deep learning framework...

📝 한글 번역
본 논문은 새로운 딥러닝 프레임워크를 제시합니다...

🔗 https://ieeexplore.ieee.org/xxxx
```

## Changelog
| Date | Change | Reason |
|------|--------|--------|
| 2026-05-15 | Kakao API URL 수정: `/talk/message/send/me` → `/talk/memo/default/send` | 잘못된 URL로 404 발생 |
| 2026-05-15 | Feed 템플릿 → Text 템플릿으로 변경 | 200자 제한으로 abstract+번역 불가 |
| 2026-05-15 | Google 번역 추가 (deep-translator) | 영문 abstract → 한글 번역 제공 |
| 2026-05-15 | Abstract + 번역문 + 링크를 메시지에 포함 | 논문 요약 정보를 카톡에서 바로 확인 |
| 2026-05-15 | 검색어 설정 페이지(/settings) 추가 | 사용자가 검색어 추가/활성화/비활성화 가능 |
| 2026-05-15 | SearchKeyword DB 모델 추가 + 기본 20개 시드 | 영어/한국어 각 10개 기본 검색어 |
| 2026-05-15 | 크롤러 전면 개선 (arXiv, IEEE, KCI, DBpia) | 실제 사이트 검색 기반, 키워드별 검색 |
| 2026-05-15 | 초기 크롤링 백그라운드 스레드로 분리 | 앱 시작 속도 개선 |
