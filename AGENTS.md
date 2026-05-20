# Power Papers — 나침반

전력 관련 최신 논문 수집/공유 웹 시스템. 카카오톡 공유 지원.

## 상황별 지침

| 상황/질문 | 참고 |
|-----------|------|
| "배포가 안 돼요", "500 에러", "사이트 만료됨" | [`docs/deployment.md`](docs/deployment.md) |
| "Git commit/push 어떻게?", "pre-commit hook 설정" | [`docs/git-workflow.md`](docs/git-workflow.md) |
| "크롤러가 왜 안 되지?", "KCI API 키 등록" | [`docs/crawlers.md`](docs/crawlers.md) |
| "API 키 값이 뭐였지?", "키 바꾸려면" | [`docs/api-keys.md`](docs/api-keys.md) |
| "카톡 공유 설정", "메시지 포맷 변경" | [`docs/kakao.md`](docs/kakao.md) |
| "뭐가 바뀌었어?", "이전 작업 내역" | [`docs/changelog.md`](docs/changelog.md) |
| "프로젝트 구조 좀 보여줘" | [`docs/structure.md`](docs/structure.md) |

## Quick Start
```bash
cd C:\dev\daq
.\venv\Scripts\python run.py   # http://localhost:5000
```

## Routes
| Route | 기능 |
|-------|------|
| `/` | 최신 논문 피드 (카드형) |
| `/papers/<id>` | 논문 상세 |
| `/search` | HTMX 키워드/출처 검색 |
| `/settings` | 검색어 관리 |
| `/logs` | 크롤러 로그 |
| `/kakao/share/<id>` | 카톡 나에게 보내기 |
| `/health` | 서버 상태 |
| `/admin/` | 논문 수동 등록 |

## Tech Stack
Flask + SQLAlchemy + Bootstrap 5 + HTMX + APScheduler + SQLite
