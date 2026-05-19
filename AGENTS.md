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

#### 4.1 로컬에서 수정 및 GitHub Push
```bash
cd C:\dev\daq       # 로컬
git add .
git commit -m "변경 내용 설명"
git push origin master
```

#### 4.2 PythonAnywhere에 반영

**Bash 콘솔에서 Pull**
```bash
cd /home/feelmydream/daq
git pull origin master
```

**Web 탭 → Reload 버튼 클릭**

#### 4.3 자동 업데이트 (Scheduled Tasks)

Tasks 탭 → **Create scheduled task**:

```
Command:
cd /home/feelmydream/daq && git pull origin master && touch /var/www/feelmydream_pythonanywhere_com_wsgi.py
```

※ `touch`로 WSGI 파일 타임스탬프를 갱신하면 PythonAnywhere가 자동 재시작합니다.

#### 4.4 GitHub Webhook 자동 업데이트 (선택)

Webhook을 설정하면 **로컬에서 `git push`만 하면 PythonAnywhere가 자동으로 업데이트 + Reload** 됩니다.

**설정 방법 (1회):**

GitHub 저장소 → Settings → Webhooks → Add webhook:
- **Payload URL**: `https://feelmydream.pythonanywhere.com/webhook/update`
- **Content type**: `application/json`
- **Secret**: `power-papers-webhook-secret-2026`
- **Events**: `push`만 선택
- **Active**: 체크

**동작 방식:**
1. 로컬: `git push origin master`
2. GitHub → PythonAnywhere `/webhook/update` POST 전송
3. 앱이 sleep이면 깨어남 → `git pull` 실행 → WSGI touch → 자동 Reload

**문제 발생 시:** Flask 로그(Error log)에서 `Webhook:` 메시지 확인

#### 4.5 패키지 변경 시
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
| 2026-05-19 | 논문 카드에 **한글 요약 토글** 추가 (abstract_ko) + 상세 페이지에도 표시 | 사용자가 카드에서 바로 한글 요약을 펼쳐볼 수 있도록 개선 |
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
