# PythonAnywhere Deployment

운영 URL: `https://feelmydream.pythonanywhere.com`

## 언제 이 메뉴얼을 참고할까?

| 상황 | 참고 섹션 |
|------|-----------|
| PythonAnywhere에 **최초 배포**할 때 | 최초 배포 절차 |
| 사이트가 **500 에러** 날 때 | activate_this.py 없음 오류 |
| 사이트 **만료 안내 메일** 받았을 때 | 사이트 만료 |
| **Kakao API 키** 변경/발급 시 | API 키 정보 (`api-keys.md`) |
| 다른 사람에게 **배포 방법 공유**할 때 | 전체 |

## 개요

| 항목 | 내용 |
|------|------|
| 사이트 URL | `https://feelmydream.pythonanywhere.com` |
| GitHub 저장소 | `https://github.com/feelmydream80-sys/ERA.git` |
| Python 버전 | 3.10 |
| WSGI 파일 | `/var/www/feelmydream_pythonanywhere_com_wsgi.py` |
| 프로젝트 경로 | `/home/feelmydream/daq/` |
| 가상환경 | `/home/feelmydream/daq/venv/` |

## 최초 배포 절차

### 사전 준비
- GitHub 계정
- PythonAnywhere 계정 (https://www.pythonanywhere.com)
- Kakao Developers 앱 (https://developers.kakao.com)

### Kakao Developers 설정

**Redirect URI 등록**
카카오 개발자 콘솔 → 내 앱 → **앱 설정 > 플랫폼 > Web**:

| 구분 | URI |
|------|-----|
| Redirect URI (기존) | `http://localhost:5000/kakao/callback` |
| Redirect URI (추가) | `https://feelmydream.pythonanywhere.com/kakao/callback` |

**JavaScript SDK 도메인 등록**
같은 페이지 **JavaScript SDK 도메인** 항목:

| 구분 | 도메인 |
|------|--------|
| 로컬 개발 | `http://localhost:5000` |
| 운영 | `https://feelmydream.pythonanywhere.com` |

### PythonAnywhere — 코드 배포

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

### PythonAnywhere — Web 설정

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

### 접속 확인

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

## 주의사항 및 문제 해결

### `activate_this.py` 없음 오류
Python 3.10+ 기본 `venv`에는 `activate_this.py`가 없습니다.
```python
# 올바른 방법
sys.path.insert(0, '/home/feelmydream/daq/venv/lib/python3.10/site-packages')

# 잘못된 방법 (오류 발생!)
# activate_this = '/home/feelmydream/daq/venv/bin/activate_this.py'
```

### 사이트 만료
무료 티어는 **한 달에 한 번** 로그인해서 Web 탭의 **"Run until 1 month from today"** 버튼을 눌러야 유지됩니다. 만료 일주일 전 이메일 발송.

### APScheduler 제약
PythonAnywhere 무료 티어는 항상 켜져 있지 않아 매시간 크롤링이 정상 작동하지 않을 수 있습니다. Scheduled Tasks로 하루 1회 크롤링으로 대체 가능합니다.

### KCI/DBpia 크롤링 제약
한국 IP가 필요한 사이트는 PythonAnywhere(해외 IP)에서 차단될 수 있습니다. arXiv, IEEE 위주로 수집됩니다.
