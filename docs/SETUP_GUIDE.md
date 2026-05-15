# Power Papers - Development Guide

> 전력 관련 최신 기술 논문을 수집/공유하는 웹 시스템. 카카오톡 공유 지원.

---

## 목차

1. [개요](#1-개요)
2. [기술 스택](#2-기술-스택)
3. [사전 준비](#3-사전-준비)
4. [환경 구축](#4-환경-구축)
5. [Kakao Developers 설정](#5-kakao-developers-설정)
6. [설정 파일 작성](#6-설정-파일-작성)
7. [소스 코드 구조](#7-소스-코드-구조)
8. [실행](#8-실행)
9. [기능별 사용법](#9-기능별-사용법)
10. [트러블슈팅](#10-트러블슈팅)

---

## 1. 개요

Power Papers는 국내외 전력 관련 최신 기술 논문을 자동으로 수집하고, 카드형 UI로 보여주며, 카카오톡으로 공유할 수 있는 웹 시스템입니다.

### 주요 기능
- **자동 크롤링**: 매시간 IEEE, arXiv, KCI, DBpia에서 전력 관련 논문 수집
- **키워드 관리**: 영어/한국어 검색어를 자유롭게 추가/수정/삭제
- **카드형 피드**: 최신 논문을 카드 형태로 표시, 출처별 필터링
- **카카오톡 공유**: 논문 정보(제목, 저자, 초록, 한글 번역, 링크)를 카톡으로 전송
- **관리자 페이지**: 수동 논문 등록/관리 (Flask-Admin)

---

## 2. 기술 스택

| 계층 | 기술 | 버전 |
|------|------|------|
| Backend | Flask | 3.1+ |
| ORM | Flask-SQLAlchemy | 3.1+ |
| Admin | Flask-Admin | 2.2+ |
| Scheduler | APScheduler | 3.11+ |
| Frontend | Bootstrap 5 + HTMX | - |
| 번역 | deep-translator (Google Translate) | 1.11+ |
| DB | SQLite (로컬 기본) | - |

---

## 3. 사전 준비

### 3.1 필수 설치 항목

- **Python 3.13+** (테스트 환경: 3.13.3)
- **Git** (선택사항, 버전 관리용)
- **카카오 계정** (Kakao Developers 앱 생성용)

### 3.2 설치 확인

```powershell
python --version
# Python 3.13.3

pip --version
```

---

## 4. 환경 구축

### 4.1 프로젝트 클론 (Git 사용 시)

```powershell
git clone <repository-url>
cd power-papers
```

### 4.2 또는 직접 생성

```powershell
mkdir power-papers
cd power-papers
```

### 4.3 가상환경 생성 및 활성화

```powershell
python -m venv venv
.\venv\Scripts\activate
# (venv) 표시 확인
```

### 4.4 패키지 설치

```powershell
pip install flask flask-sqlalchemy flask-admin apscheduler
pip install requests beautifulsoup4 lxml
pip install flask-bootstrap5
pip install deep-translator
```

#### requirements.txt로 한 번에 설치

```powershell
pip install -r requirements.txt
```

### 4.5 디렉토리 구조 생성

```powershell
New-Item -ItemType Directory -Path "app\views", "app\crawlers", "app\templates\kakao", "app\static\css" -Force
```

---

## 5. Kakao Developers 설정

> ⚠️ **이 부분이 가장 까다롭습니다.** 아래 순서를 정확히 따라야 합니다.

### 5.1 앱 생성

1. [Kakao Developers](https://developers.kakao.com) 접속 후 로그인
2. 우측 상단 **"내 애플리케이션"** 클릭
3. **"애플리케이션 추가하기"** 버튼 클릭
4. 앱 이름 입력 (예: `Power Papers`), 회사명 입력 후 저장

### 5.2 REST API 키 확인

1. 생성된 앱의 **"요약 정보"** 페이지에서 **"REST API 키"** 확인
2. 이 키는 `config.py`에 입력할 예정

### 5.3 카카오 로그인 활성화 + Redirect URI 등록

> ⚠️ **주의:** 2025년 12월 3일 UI 개편으로 설정 위치가 변경되었습니다.

1. 좌측 메뉴 **"카카오 로그인"** 클릭
2. **"사용 설정"** → `ON`으로 변경
3. 좌측 메뉴 **"앱"** → **"플랫폼 키"** 클릭
4. **"REST API 키"** 항목을 **클릭하여 펼침**
5. 아래에 있는 **"리다이렉트 URI"** 입력란에 다음 주소 입력:

```
http://localhost:5000/kakao/callback
```

6. 우측 하단 **"저장"** 버튼 **반드시 클릭**

> ⚠️ **트러블슈팅:** KOE006 에러가 발생하면 Redirect URI가 저장되지 않은 것입니다. "저장" 버튼을 누르지 않으면 반영되지 않습니다.

### 5.4 Client Secret 발급

1. 좌측 메뉴 **"앱"** → **"플랫폼 키"** 클릭
2. **"REST API 키"** 펼침
3. **"클라이언트 시크릿"** 항목에서 코드 발급 (또는 생성)
4. 발급된 코드 복사 → `config.py`에 입력

### 5.5 동의항목 설정

1. 좌측 메뉴 **"카카오 로그인"** → **"동의항목"** 클릭
2. 아래로 스크롤하여 **"접근권한"** 섹션 찾기
3. **"카카오톡 메시지 전송"(`talk_message`)** 항목 찾기
4. 우측 **"설정"** 버튼 클릭
5. **"동의 단계"** → `이용 중 동의` 선택
6. **"동의 목적"** 입력 (예: `논문 정보 공유`)
7. **"저장"** 버튼 클릭

> ✅ 결과: `talk_message` 상태가 `이용 중 동의`로 변경되어야 정상입니다.

### 5.6 나에게 보내기 활성화

> ⚠️ **중요:** 동의항목 설정만으로는 부족합니다. 별도로 제품 설정에서 활성화해야 합니다.

1. 좌측 메뉴 **"카카오톡 메시지"** 클릭
2. 페이지에 **"나에게 보내기"** 기능 활성화 (ON/OFF 토글)
3. 활성화 후 **"저장"**

> ⚠️ **트러블슈팅:** `code -1, msg: "Not Found"` 에러는 (1) API URL이 잘못되었거나, (2) "나에게 보내기" 기능이 활성화되지 않았거나, (3) 테스트 멤버가 등록되지 않은 경우입니다.

### 5.7 테스트 멤버 등록 (필요시)

개발 중인 앱은 기본적으로 앱 멤버(owner)만 메시지를 받을 수 있습니다.
1. 좌측 메뉴 **"멤버"** 클릭
2. 자신의 계정이 등록되어 있는지 확인
3. 없으면 **"추가"** 버튼으로 카카오계정(이메일) 입력 후 추가

### 5.8 최종 확인할 설정 값

| 항목 | 값 | 위치 |
|------|-----|------|
| REST API 키 | `2331196ef286dc735ee7735b32a2e6bf` | 앱 > 플랫폼 키 > REST API 키 |
| Client Secret | `9Yd4YywG7cabXMOpT2iISlANNKlYnA5D` | 앱 > 플랫폼 키 > REST API 키 (펼침) |
| Redirect URI | `http://localhost:5000/kakao/callback` | REST API 키 내부 |
| 카카오 로그인 | ON | 카카오 로그인 > 사용 설정 |
| talk_message | 이용 중 동의 | 카카오 로그인 > 동의항목 > 접근권한 |
| 나에게 보내기 | 활성화 | 카카오톡 메시지 |

> 💡 **팁:** Kakao API 테스트 시 자주 마주치는 HTTP 응답:
> - `200 OK` → 성공
> - `401 Unauthorized` → 토큰 만료 또는 scope 누락 (`scope=talk_message` 확인)
> - `404 Not Found` → API URL 오류 (정확한 URL: `/v2/api/talk/memo/default/send`)
> - `KOE006` → Redirect URI 미등록 또는 불일치

---

## 6. 설정 파일 작성

### 6.1 config.py

```python
import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASEDIR, 'papers.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Kakao API 설정 (환경변수 우선, 없으면 직접 입력한 값 사용)
    KAKAO_REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY", "여기에_REST_API_키_입력")
    KAKAO_CLIENT_SECRET = os.environ.get("KAKAO_CLIENT_SECRET", "여기에_Client_Secret_입력")
    KAKAO_REDIRECT_URI = os.environ.get(
        "KAKAO_REDIRECT_URI", "http://localhost:5000/kakao/callback"
    )

    # Kakao API 엔드포인트
    KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
    KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
    KAKAO_SEND_ME_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    PAPERS_PER_PAGE = 20
```

> ⚠️ **주의:** `KAKAO_SEND_ME_URL`은 반드시 `/v2/api/talk/memo/default/send` 여야 합니다. `/v2/api/talk/message/send/me`는 **잘못된 URL**입니다.

### 6.2 환경변수로 설정 (권장, 보안 우수)

```powershell
# PowerShell
$env:KAKAO_REST_API_KEY = "2331196ef286dc735ee7735b32a2e6bf"
$env:KAKAO_CLIENT_SECRET = "9Yd4YywG7cabXMOpT2iISlANNKlYnA5D"
python run.py
```

---

## 7. 소스 코드 구조

### 7.1 전체 구조

```
power-papers/
├── run.py                      # 앱 실행 파일
├── config.py                   # 설정 파일 (DB, Kakao API)
├── requirements.txt            # 패키지 목록
├── AGENTS.md                   # 프로젝트 요약
├── app/
│   ├── __init__.py             # Flask 앱 팩토리 + 기본 검색어 시드
│   ├── models.py               # SQLAlchemy 모델 (Paper, SearchKeyword)
│   ├── admin.py                # Flask-Admin (논문 CRUD)
│   ├── scheduler.py            # APScheduler (매시간 크롤링 실행)
│   ├── views/
│   │   ├── feed.py             # 메인 피드 (/), 상세보기 (/papers/<id>), 건강체크 (/health)
│   │   ├── search.py           # HTMX 검색/필터 (/search)
│   │   ├── kakao.py            # Kakao OAuth + 나에게 보내기
│   │   └── settings.py         # 검색어 관리 (/settings)
│   ├── crawlers/
│   │   ├── base.py             # 공통 크롤러 (키워드 로드, 로깅)
│   │   ├── arxiv.py            # arXiv API 크롤러
│   │   ├── ieee.py             # IEEE Xplore 크롤러
│   │   ├── kci.py              # KCI 한국학술지 크롤러
│   │   └── kee.py              # DBpia 한국 전력/에너지 크롤러
│   ├── templates/
│   │   ├── base.html           # 기본 레이아웃 (Bootstrap 5, HTMX)
│   │   ├── feed.html           # 카드형 피드 페이지
│   │   ├── detail.html         # 논문 상세 페이지
│   │   ├── _paper_cards.html   # 논문 카드 부분 템플릿 (HTMX용)
│   │   ├── settings.html       # 검색어 설정 페이지
│   │   └── admin_edit.html     # 관리자 수정 폼
│   └── static/
│       └── css/
│           └── style.css       # 커스텀 스타일 (다크 테마)
└── papers.db                   # SQLite 데이터베이스 (자동 생성)
```

### 7.2 각 파일 설명

#### run.py
```python
from app import create_app, db
from app.models import Paper
from datetime import datetime

app = create_app()

with app.app_context():
    total = Paper.query.count()

# 시작 배너 출력
print()
print("=" * 50)
print("  Power Papers Server Started")
print("=" * 50)
print(f"  Time    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  DB      : {total} papers stored")
print(f"  Routes  :")
for r in sorted(app.url_map.iter_rules(), key=lambda x: x.rule):
    if not r.rule.startswith("/admin") and r.rule != "/static/<path:filename>":
        print(f"    {r.rule:30s} -> {r.endpoint}")
print(f"  Scheduler: APScheduler active (hourly crawl)")
print(f"  Admin   : http://localhost:5000/admin/")
print("=" * 50)
print()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

#### app/__init__.py
Flask 앱 팩토리. 앱 시작 시:
1. DB 초기화
2. Blueprint 등록 (feed, search, kakao, settings)
3. Flask-Admin 설정
4. APScheduler 시작 (매시간 크롤링)
5. 기본 검색어 20개 자동 시드
6. 첫 크롤링을 백그라운드 스레드로 실행

#### app/models.py
두 개의 모델:
- **Paper**: 논문 정보 (제목, 저자, 초록, 키워드, 출처, URL, 발행일)
- **SearchKeyword**: 검색어 (keyword, language=en/ko, enabled)
- **DEFAULT_KEYWORDS**: 영어 10개 + 한국어 10개 기본값

#### app/views/kakao.py (핵심 로직)
```python
# OAuth 로그인 URL에 scope=talk_message 필수 포함
auth_url = (
    f"{KAKAO_AUTH_URL}"
    f"?client_id={client_id}"
    f"&redirect_uri={redirect_uri}"
    f"&response_type=code"
    f"&scope=talk_message"  # ← 이게 없으면 메시지 전송 권한 없음
)

# 템플릿: feed 대신 text 사용 (200자 제한 → 1000자)
template_object = {
    "object_type": "text",
    "text": text_body,      # 제목 + 저자 + abstract + 번역 + 링크
    "link": { ... },
    "button_title": "View Paper",
}

# 번역: deep-translator GoogleTranslate 활용
from deep_translator import GoogleTranslator
translated = GoogleTranslator(source="en", target="ko").translate(abstract)
```

#### app/crawlers/base.py
```python
class BaseCrawler:
    name = "base"

    def crawl(self):
        raise NotImplementedError

    def log(self, message):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  [{ts}] Crawler[{self.name}] {message}")

    def get_keywords(self, language=None):
        # DB에서 enabled=True인 검색어 로드
        q = SearchKeyword.query.filter_by(enabled=True)
        if language:
            q = q.filter_by(language=language)
        return [kw.keyword for kw in q.all()]
```

#### app/templates/base.html
Bootstrap 5 다크 테마 + HTMX CDN 포함. 내비게이션 메뉴:
- Papers (피드)
- Keywords (설정)
- Health (상태 확인)
- 검색창

#### app/templates/settings.html
검색어 관리 테이블:
- 키워드 추가 폼 (입력 + 언어 선택)
- 전체 키워드 목록 표시 (EN/KO 태그, 활성/비활성 상태)
- Enable/Disable 토글 버튼
- Delete 버튼 (확인창)

---

## 8. 실행

### 8.1 개발 서버 실행

```powershell
cd power-papers
.\venv\Scripts\activate
python run.py
```

### 8.2 접속 URL

| 페이지 | URL | 설명 |
|--------|-----|------|
| 메인 피드 | http://localhost:5000/ | 최신 논문 카드 목록 |
| 검색 | http://localhost:5000/search | 키워드/출처 검색 |
| 상세 | http://localhost:5000/papers/1 | 논문 상세 정보 |
| 설정 | http://localhost:5000/settings/ | 검색어 관리 |
| 건강체크 | http://localhost:5000/health | 서버 상태 API |
| 관리자 | http://localhost:5000/admin/ | 논문 수동 등록/관리 |
| 카카오 공유 | http://localhost:5000/kakao/share/1 | 논문 카톡 전송 |

### 8.3 초기 실행 시 표시되는 정보

```
==================================================
  Power Papers Server Started
==================================================
  Time    : 2026-05-15 09:54:45
  DB      : 60 papers stored
  Routes  :
    /                              -> feed.index
    /health                        -> feed.health
    /kakao/callback                -> kakao.callback
    /kakao/login                   -> kakao.login
    /kakao/share/<int:paper_id>    -> kakao.share
    /kakao/logout                  -> kakao.logout
    /search                        -> search.search
    /settings/                     -> settings.index
  Scheduler: APScheduler active (hourly crawl)
  Admin   : http://localhost:5000/admin/
==================================================
```

---

## 9. 기능별 사용법

### 9.1 논문 크롤링

앱 실행 시 자동으로 크롤링이 시작됩니다:
```
[09:54:45] === Crawler Run Started ===
  [09:54:45] Crawler[IEEE] searching "power system"...
  [09:55:00] Crawler[IEEE] complete: 5 found, 3 new
  [09:55:00] Crawler[arXiv] searching "power system"...
  ...
  [09:55:30] === Crawler Run Finished: 12 new papers (DB total: 72) ===
```

- 매시간 자동 실행 (APScheduler)
- 각 크롤러가 enabled=True인 모든 검색어로 검색
- 중복 방지: source_url 기준

### 9.2 검색어 추가/수정/삭제

1. http://localhost:5000/settings/ 접속
2. **Add Keyword** 폼에 키워드 입력
3. 언어 선택 (English / 한국어)
4. **Add** 버튼 클릭
5. 목록에서 Enable/Disable 토글 또는 Delete

### 9.3 수동 논문 등록

1. http://localhost:5000/admin/ 접속
2. Paper 테이블 옆 **"Create"** 버튼
3. 제목, 저자, 초록, URL 등 입력 후 저장

### 9.4 카카오톡 공유

1. 메인 피드에서 아무 논문 카드 선택
2. 카드 하단 **"Kakao"** 버튼 클릭
3. (최초 1회) Kakao 로그인 화면 → ID/비밀번호 입력 → 동의
4. 자동으로 논문 정보가 카톡으로 전송됨

**카톡으로 전송되는 메시지 예시:**

```
📄 A Deep Learning Approach for Smart Grid Optimization
✍️ Kim, Lee, Park
🏷️ IEEE

📝 Abstract
This paper presents a novel deep learning framework for smart grid optimization...

📝 한글 번역
본 논문은 스마트그리드 최적화를 위한 새로운 딥러닝 프레임워크를 제시합니다...

🔗 https://ieeexplore.ieee.org/xxxx

[View Paper]
```

### 9.5 서버 상태 확인

```bash
# 웹브라우저 또는 curl
curl http://localhost:5000/health

# 응답 예시
{"status":"ok","time":"2026-05-15 10:00:00","total_papers":72,"sources":["IEEE","arXiv","KCI","DBpia"]}
```

---

## 10. 트러블슈팅

### 10.1 "KOE006" - 올바르지 않은 Redirect URI

**원인**: Redirect URI가 Kakao Developers 콘솔에 저장되지 않았거나, 요청값과 일치하지 않음

**해결**:
1. 앱 > 플랫폼 키 > REST API 키 (펼침) > 리다이렉트 URI 확인
2. 저장된 값: `http://localhost:5000/kakao/callback`
3. **저장 버튼 반드시 클릭** (입력만 하면 안 됨)

### 10.2 "Not Found" (code -404) - 메시지 전송 실패

**원인 1: API URL 오류**
- **틀린 URL**: `https://kapi.kakao.com/v2/api/talk/message/send/me` ❌
- **올바른 URL**: `https://kapi.kakao.com/v2/api/talk/memo/default/send` ✅

**원인 2: "나에게 보내기" 기능 미활성화**
- 좌측 메뉴 "카카오톡 메시지" → "나에게 보내기" 활성화 ON

**원인 3: 테스트 멤버 미등록**
- 앱 > 멤버 > 자신의 계정이 등록되어 있는지 확인

### 10.3 "Token expired" (401) - 토큰 만료

**원인**: Kakao access token 만료 (약 1~2시간)

**해결**: `http://localhost:5000/kakao/logout` 접속 후 재로그인

> 또는 브라우저에서 쿠키 삭제 후 다시 시도

### 10.4 토큰 발급 시 `talk_message` scope 누락

**원인**: OAuth 로그인 URL에 `scope=talk_message`가 없음

**해결**: `/kakao/login` URL이 다음을 포함하는지 확인:
```
/oauth/authorize?client_id=...&redirect_uri=...&response_type=code&scope=talk_message
```

### 10.5 크롤러가 0건 반환

**원인 1**: 사이트 접근 차단 (HTTP 403, 429 등)
- 헤더에 User-Agent 추가 필요
- arXiv는 rate limit 있음 (429 Too Many Requests)

**원인 2**: 검색어 없음
- `/settings/` 페이지에서 enabled=True인 검색어가 있는지 확인

### 10.6 번역 실패

**원인**: 네트워크 문제 또는 Google Translate 차단

**해결**: deep-translator는 자동 fallback 처리됨.
번역 실패 시 원문(abstract)만 전송됩니다.

### 10.7 앱 시작 시 "Working outside of application context" 오류

**원인**: 백그라운드 스레드에서 `with app.app_context():` 없이 DB 접근

**해결**: scheduler.py의 `run_all_crawlers()` 함수 내에서 
`Paper.query.count()` 호출이 `with app.app_context():` 블록 안에 있는지 확인

---

## 부록

### A. requirements.txt

```
apscheduler==3.11.2
beautifulsoup4==4.14.3
blinker==1.9.0
certifi==2026.4.22
charset-normalizer==3.4.7
click==8.3.3
colorama==0.4.6
deep-translator==1.11.4
Flask==3.1.3
Flask-Admin==2.2.0
flask-bootstrap5==0.1.dev1
Flask-SQLAlchemy==3.1.1
greenlet==3.5.0
idna==3.15
itsdangerous==2.2.0
Jinja2==3.1.6
lxml==6.1.0
MarkupSafe==3.0.3
requests==2.34.1
soupsieve==2.8.3
SQLAlchemy==2.0.49
typing_extensions==4.15.0
tzdata==2026.2
tzlocal==5.3.1
urllib3==2.7.0
Werkzeug==3.1.8
WTForms==3.2.2
```

### B. Kakao API 설정 요약 카드

```
┌─────────────────────────────────────────────────────────┐
│   Kakao Developers 설정 체크리스트                       │
├─────────────────────────────────────────────────────────┤
│  [✅] 앱 생성                                           │
│  [✅] REST API 키 확인                                   │
│  [✅] Client Secret 발급                                 │
│  [✅] Redirect URI 등록 (http://localhost:5000/kakao/    │
│       callback)                                          │
│  [✅] 카카오 로그인 활성화 ON                             │
│  [✅] 동의항목 > talk_message > 이용 중 동의              │
│  [✅] 카카오톡 메시지 > 나에게 보내기 활성화              │
│  [✅] 멤버에 테스트 계정 등록                             │
│  [✅] config.py에 API 키 + Secret 입력                    │
└─────────────────────────────────────────────────────────┘
```