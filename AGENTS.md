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
├── sync.ps1            # 크롤링 → 커밋 → 푸시 자동화
├── requirements.txt
├── AGENTS.md
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

## Pre-commit Hook (자동 크롤링)

커밋할 때마다 자동으로 크롤러가 실행되어 신규 논문을 수집하고 `papers.db`를 갱신합니다.

### 1회 설정
```powershell
cd C:\dev\daq
git config core.hooksPath .githooks
```

설정 후에는 `git commit` 실행 시 다음 순서로 동작:
1. 모든 크롤러 실행 (arXiv, IEEE, OpenAlex, CrossRef, KCI 웹, KCI OpenAPI)
2. 신규 논문 → `papers.db` 저장
3. 변경된 `papers.db` 자동 stage
4. commit 정상 진행

### `.git/hooks`에 직접 복사
`.githooks/` 디렉토리를 사용할 수 없는 환경에서는:
```bash
cp .githooks/pre-commit .git/hooks/pre-commit
```

---

## Deployment — PythonAnywhere

운영 URL: `https://feelmydream.pythonanywhere.com`

### 언제 이 메뉴얼을 참고할까?

| 상황 | 참고 섹션 |
|------|-----------|
| PythonAnywhere에 **최초 배포**할 때 | 전체 (2. 최초 배포 절차) |
| 로컬에서 코드 **수정 후 반영**할 때 | 4. 소스 코드 업데이트 절차 |
| 사이트가 **500 에러** 날 때 | 5.1 activate_this.py 없음 오류 |
| 사이트 **만료 안내 메일** 받았을 때 | 5.2 사이트 만료 |
| **Kakao API 키** 변경/발급 시 | 6. API 키 정보 |
| 다른 사람에게 **배포 방법 공유**할 때 | 전체 |

---

### 1. 개요

| 항목 | 내용 |
|------|------|
| 사이트 URL | `https://feelmydream.pythonanywhere.com` |
| GitHub 저장소 | `https://github.com/feelmydream80-sys/ERA.git` |
| Python 버전 | 3.10 |
| WSGI 파일 | `/var/www/feelmydream_pythonanywhere_com_wsgi.py` |
| 프로젝트 경로 | `/home/feelmydream/daq/` |
| 가상환경 | `/home/feelmydream/daq/venv/` |

---

### 2. 최초 배포 절차

#### 2.1 사전 준비
- GitHub 계정
- PythonAnywhere 계정 (https://www.pythonanywhere.com)
- Kakao Developers 앱 (https://developers.kakao.com)

#### 2.2 Kakao Developers 설정

**2.2.1 Redirect URI 등록**
카카오 개발자 콘솔 → 내 앱 → **앱 설정 > 플랫폼 > Web**:

| 구분 | URI |
|------|-----|
| Redirect URI (기존) | `http://localhost:5000/kakao/callback` |
| Redirect URI (추가) | `https://feelmydream.pythonanywhere.com/kakao/callback` |

**2.2.2 JavaScript SDK 도메인 등록**
같은 페이지 **JavaScript SDK 도메인** 항목:

| 구분 | 도메인 |
|------|--------|
| 로컬 개발 | `http://localhost:5000` |
| 운영 | `https://feelmydream.pythonanywhere.com` |

#### 2.3 PythonAnywhere — 코드 배포

**Bash 콘솔에서 Git Clone**
```bash
cd /home/feelmydream
git clone https://github.com/feelmydream80-sys/ERA.git daq
```

**가상환경 생성 및 패키지 설치**
```bash
cd /home/feelmydream/daq
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

설치 확인:
```bash
pip list | grep deep_translator
```
→ `deep-translator 1.11.4` 출력되어야 정상

**데이터베이스 생성**
```bash
cd /home/feelmydream/daq
source venv/bin/activate
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    from app import seed_default_keywords
    seed_default_keywords()
    print('DB created successfully')
"
```

※ 기존 로컬 `papers.db`를 그대로 사용하려면 로컬 파일을 PythonAnywhere Files 탭에서 `/home/feelmydream/daq/papers.db`로 업로드하면 됩니다.

#### 2.4 PythonAnywhere — Web 설정

**Web App 생성**
1. Web 탭 → **Add a new web app**
2. **Manual configuration** 선택
3. Python 3.10 선택

**WSGI 파일 설정**
Web 탭 → **WSGI configuration file** 링크 클릭 → 전체 내용을 아래로 교체:

```python
import sys
import os

# 가상환경 site-packages 직접 추가
# Python 3.10 기본 venv는 activate_this.py가 없음
sys.path.insert(0, '/home/feelmydream/daq/venv/lib/python3.10/site-packages')

path = '/home/feelmydream/daq'
if path not in sys.path:
    sys.path.append(path)

os.environ['SECRET_KEY'] = 'power-papers-prod-secret-key-2026'
os.environ['KAKAO_REST_API_KEY'] = '2331196ef286dc735ee7735b32a2e6bf'
os.environ['KAKAO_CLIENT_SECRET'] = '9Yd4YywG7cabXMOpT2iISlANNKlYnA5D'
os.environ['KAKAO_JAVASCRIPT_KEY'] = 'f95d003dc4f3c29be2866a308947b71d'
os.environ['KAKAO_REDIRECT_URI'] = 'https://feelmydream.pythonanywhere.com/kakao/callback'
os.environ['KCI_SERVICE_KEY'] = ''  # 공공데이터포털(data.go.kr)에서 발급받은 ServiceKey (선택)
os.environ['WEBHOOK_SECRET'] = 'power-papers-webhook-secret-2026'

from app import create_app
application = create_app()
```

**Virtualenv 경로 설정**
Web 탭 → **Virtualenv** 섹션에 입력:
```
/home/feelmydream/daq/venv
```

**Static Files 설정**
Web 탭 → **Static files** 섹션:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/feelmydream/daq/app/static/` |

**Force HTTPS**
Web 탭 → **Security** → **Force HTTPS** 체크

**Reload**
Web 탭 상단 **Reload** 버튼 클릭

#### 2.5 접속 확인

브라우저에서 `https://feelmydream.pythonanywhere.com` 접속

| 기능 | URL | 확인 |
|------|-----|------|
| 메인 피드 | `/` | ⬜ |
| 논문 상세 | 피드에서 논문 클릭 | ⬜ |
| 검색 | 검색창 입력 | ⬜ |
| 설정 | `/settings/` | ⬜ |
| Admin | `/admin/` | ⬜ |
| Health | `/health` | ⬜ |
| Send to Me | 논문 → Send to Me 버튼 | ⬜ |
| Share to KakaoTalk | 논문 → Share 버튼 | ⬜ |

---

### 3. KakaoTalk 기능 설명

#### 3.1 "Send to Me" (나에게 보내기)
- REST API + OAuth 방식
- 사용자가 **Send to Me** 버튼 클릭 → Kakao 로그인 → `talk_message` 권한 동의 → 논문 전송
- Kakao Developers에 `https://feelmydream.pythonanywhere.com/kakao/callback` Redirect URI 등록 필수

#### 3.2 "Share to KakaoTalk" (친구 공유)
- JavaScript SDK 방식 (OAuth 불필요, Biz App 불필요)
- `Kakao.Share.sendDefault()` 사용
- Kakao Developers에 `https://feelmydream.pythonanywhere.com` JavaScript SDK 도메인 등록 필수
- PC에서는 카카오톡 데스크탑 앱 필요

---

### 4. 소스 코드 업데이트 절차

#### 4.1 기본 워크플로우

`git commit` 실행 시 `pre-commit` hook이 자동으로 크롤러를 실행하고 `papers.db`를 갱신합니다.

```powershell
cd C:\dev\daq
git commit -m "변경 내용"
git push origin master
```

#### 4.2 크롤링 없이 코드만 커밋

크롤링 없이 코드만 올리려면 `--no-verify` 옵션 사용:
```bash
cd C:\dev\daq
git add .
git commit --no-verify -m "변경 내용 설명"
git push origin master
```

(이 경우 `papers.db`는 이전 commit 시점의 데이터가 올라갑니다.)

#### 4.3 PythonAnywhere 자동 반영

GitHub Webhook이 이미 설정되어 있어, `git push`만 하면 자동으로 적용됩니다.

**동작 방식:**
1. 로컬: `.\sync.ps1` (또는 `git commit && git push origin master`)
2. GitHub가 PythonAnywhere의 `/webhook/update`로 POST 전송
3. PA에서 `git pull origin master` 실행 + WSGI touch → 자동 Reload
4. `papers.db`도 함께 pull 되어 KCI 논문 포함 모든 데이터 적용

#### 4.4 패키지 변경 시
```bash
cd /home/feelmydream/daq
source venv/bin/activate
pip install -r requirements.txt
```
(이후 Reload 필수)

---

### 5. 주의사항 및 문제 해결

#### 5.1 `activate_this.py` 없음 오류
Python 3.10+ 기본 `venv`에는 `activate_this.py`가 없습니다.
```python
# 올바른 방법
sys.path.insert(0, '/home/feelmydream/daq/venv/lib/python3.10/site-packages')

# 잘못된 방법 (오류 발생!)
# activate_this = '/home/feelmydream/daq/venv/bin/activate_this.py'
```

#### 5.2 사이트 만료
무료 티어는 **한 달에 한 번** 로그인해서 Web 탭의 **"Run until 1 month from today"** 버튼을 눌러야 유지됩니다. 만료 일주일 전 이메일 발송.

#### 5.3 APScheduler 제약
PythonAnywhere 무료 티어는 항상 켜져 있지 않아 매시간 크롤링이 정상 작동하지 않을 수 있습니다. Scheduled Tasks로 하루 1회 크롤링으로 대체 가능합니다.

#### 5.4 KCI/DBpia 크롤링 제약
한국 IP가 필요한 사이트는 PythonAnywhere(해외 IP)에서 차단될 수 있습니다. arXiv, IEEE 위주로 수집됩니다.

---

### 6. API 키 정보

| 키 | 값 | 설정 위치 |
|-----|-----|-----------|
| `KAKAO_REST_API_KEY` | `2331196ef286dc735ee7735b32a2e6bf` | WSGI 파일 또는 환경변수 |
| `KAKAO_CLIENT_SECRET` | `9Yd4YywG7cabXMOpT2iISlANNKlYnA5D` | WSGI 파일 또는 환경변수 |
| `KAKAO_JAVASCRIPT_KEY` | `f95d003dc4f3c29be2866a308947b71d` | WSGI 파일 또는 환경변수 |
| `SECRET_KEY` | `power-papers-prod-secret-key-2026` | WSGI 파일 또는 환경변수 (운영 시 변경 권장) |
| `WEBHOOK_SECRET` | `power-papers-webhook-secret-2026` | WSGI 파일 또는 환경변수 (GitHub Webhook 시크릿) |
| `KCI_SERVICE_KEY` | (data.go.kr 발급) | WSGI 파일 또는 환경변수 (없으면 KCI OpenAPI 수집 스킵) |

---

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
- **활성 소스**: arXiv, IEEE (REST API), OpenAlex, CrossRef (4개)
- **비활성 소스**: KCI 공공데이터 Open API (ServiceKey 설정 시 활성화)
- **제거된 소스**: KCI 웹스크래핑, DBpia (한국 IP 차단)
- Settings 페이지에서 검색어 추가/활성화 가능
- 기본 검색어 20개 (영어 10 + 한국어 10)

### Data Source Status (2026-05-19 기준)

| Source | Status | Method | IP Required |
|--------|--------|--------|-------------|
| arXiv | ✅ Working | Free API (export.arxiv.org) | Any |
| IEEE Xplore | ✅ Working | REST API (rest/search) | Any |
| OpenAlex | ✅ Working | Free API (api.openalex.org) | Any |
| Crossref | ✅ Working (no abstract) | Free API (api.crossref.org) | Any |
| KCI (OpenAPI) | ✅ Working (with key, no keyword search) | 공공데이터 Open API (api.odcloud.kr) | Any |
| KCI (Scraping) | ❌ Removed | Korean IP blocked | Korea only |
| DBpia | ❌ Removed | Korean IP blocked + JS | Korea only |

### KCI Open API 등록 방법
1. https://www.data.go.kr/data/15083283/openapi.do 접속
2. 로그인 → "활용신청" → 승인유형 **REST** 선택
3. 발급받은 ServiceKey를 환경변수 `KCI_SERVICE_KEY`에 설정
4. PythonAnywhere: Web 탭 → WSGI 파일에 `os.environ['KCI_SERVICE_KEY'] = '...'` 추가

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
| 2026-05-19 | sync.ps1 추가: 크롤링+커밋+푸시 자동화, papers.db Git 추적, AGENTS.md 업데이트 | 로컬 수집 DB를 push하여 PA에 KCI 논문도 반영 |
| 2026-05-19 | KCI 공공데이터 Open API → KCI 웹사이트 Open API로 전환 (`open.kci.go.kr`) | 잘못된 data.go.kr endpoint 수정 |
| 2026-05-19 | `sync.ps1` 추가: 크롤링+커밋+푸시 자동화, `papers.db` Git 추적 | 로컬 수집 DB를 push하여 PA에 KCI 논문도 반영 |
| 2026-05-19 | `pre-commit` hook 추가: commit 시 자동 크롤링 + `papers.db` stage | 사용자가 git commit만 하면 자동 수집 |
| 2026-05-19 | `kci_openapi.py`: `open.kci.go.kr` → `api.odcloud.kr` (공공데이터포털 REST) | 잘못된 KCI 자체 API endpoint 수정, 실제 키로 동작 |
| 2026-05-19 | CSS fade-in 애니메이션 추가 | 페이지 전환 시 부드러운 화면 전환 |
| 2026-05-19 | `scheduler.py`: per-source 로그 + CrawpLog DB 모델 + `/logs` 게시판 + 수동 실행 버튼 | 크롤러 동작 상태 확인 가능 |
| 2026-05-19 | KCI 웹크롤러 `poTotalSearList.kci` → `poArtiSearList.kci` | KCI 논문 검색 정상화 |
|------|--------|--------|
| 2026-05-19 | 논문 카드 Hover 시 **한글 요약 오버레이** 표시 + 카드 크기 고정 | 사용자가 마우스만 올리면 한글 요약 확인, 버튼 클릭 방식에서 Hover 방식으로 변경 |
| 2026-05-19 | 초기 시작 시 크롤링 제거 + `/favicon.ico` 라우트 추가 | cold start 502/504 timeout 방지, 404 해결 |
| 2026-05-19 | 크롤러 중복 URL 버그 수정: `seen_urls` set + `db.session.rollback()` | 동일 URL이 여러 키워드에서 중복 수집되어 UNIQUE constraint 위반 |
| 2026-05-19 | GitHub Webhook 자동 업데이트 추가 (`/webhook/update`) | git push만 하면 PythonAnywhere 자동 반영 |
| 2026-05-19 | AGENTS.md에 PythonAnywhere 배포 메뉴얼 추가 (Deployment 섹션) | PythonAnywhere 운영/업데이트 절차 문서화 |
| 2026-05-19 | Kakao REST API 친구 공유 제거 → JS SDK 공유로 대체 | Biz App 필수로 REST API 친구 공유 불가 |
| 2026-05-19 | WSGI 파일에 `activate_this.py` 대신 `sys.path.insert(0, ...)` 사용 | Python 3.10 venv에 `activate_this.py` 없음 |
| 2026-05-15 | Kakao API URL 수정: `/talk/message/send/me` → `/talk/memo/default/send` | 잘못된 URL로 404 발생 |
| 2026-05-15 | Feed 템플릿 → Text 템플릿으로 변경 | 200자 제한으로 abstract+번역 불가 |
| 2026-05-15 | Google 번역 추가 (deep-translator) | 영문 abstract → 한글 번역 제공 |
| 2026-05-15 | Abstract + 번역문 + 링크를 메시지에 포함 | 논문 요약 정보를 카톡에서 바로 확인 |
| 2026-05-15 | 검색어 설정 페이지(/settings) 추가 | 사용자가 검색어 추가/활성화/비활성화 가능 |
| 2026-05-15 | SearchKeyword DB 모델 추가 + 기본 20개 시드 | 영어/한국어 각 10개 기본 검색어 |
| 2026-05-15 | 크롤러 전면 개선 (arXiv, IEEE, KCI, DBpia) | 실제 사이트 검색 기반, 키워드별 검색 |
| 2026-05-15 | 초기 크롤링 백그라운드 스레드로 분리 | 앱 시작 속도 개선 |
| 2026-05-19 | IEEE 크롤러 REST API로 전면 개편 (HTML 스크래핑 제거) | SPA 페이지 구조 + 안티봇으로 HTML 수집 불가 |
| 2026-05-19 | OpenAlex 크롤러 추가 (api.openalex.org) | 무료 API, 초록/저자/인용 수 모두 제공 |
| 2026-05-19 | Crossref 크롤러 추가 (api.crossref.org) | DOI 기반 보조 소스 |
| 2026-05-19 | KCI 공공데이터 Open API 크롤러 추가 (apis.data.go.kr) | IP 무관, ServiceKey 등록 시 활성화 |
| 2026-05-19 | KCI 웹스크래핑 + DBpia 크롤러 비활성화 | 한국 IP 차단으로 수집 불가 |
| 2026-05-19 | AGENTS.md: Data Source Status 표 + KCI Open API 등록 가이드 추가 | 사용자가 바로 ServiceKey 등록 가능하도록 |
