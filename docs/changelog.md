# Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-05-19 | `pre-commit` hook 추가: commit 시 자동 크롤링 + `papers.db` stage | 사용자가 git commit만 하면 자동 수집 |
| 2026-05-19 | `kci_openapi.py`: `open.kci.go.kr` → `api.odcloud.kr` (공공데이터포털 REST) | 잘못된 KCI 자체 API endpoint 수정, 실제 키로 동작 |
| 2026-05-19 | CSS fade-in 애니메이션 추가 | 페이지 전환 시 부드러운 화면 전환 |
| 2026-05-19 | `scheduler.py`: per-source 로그 + CrawlLog DB 모델 + `/logs` 게시판 + 수동 실행 버튼 | 크롤러 동작 상태 확인 가능 |
| 2026-05-19 | KCI 웹크롤러 `poTotalSearList.kci` → `poArtiSearList.kci` | KCI 논문 검색 정상화 |
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
