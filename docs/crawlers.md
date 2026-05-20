# Crawlers

- 매시간 APScheduler 실행
- **활성 소스**: arXiv, IEEE, OpenAlex, CrossRef, KCI-Web (로컬), KCI-API (키 설정 시)
- **제거된 소스**: DBpia (한국 IP 차단 + JS)
- Settings 페이지에서 검색어 추가/활성화 가능
- 기본 검색어 20개 (영어 10 + 한국어 10)

## Data Source Status

| Source | Status | Method | IP Required |
|--------|--------|--------|-------------|
| arXiv | ✅ Working | Free API (export.arxiv.org) | Any |
| IEEE Xplore | ✅ Working | REST API (rest/search) | Any |
| OpenAlex | ✅ Working | Free API (api.openalex.org) | Any |
| Crossref | ✅ Working (no abstract) | Free API (api.crossref.org) | Any |
| **KCI-Web** | ✅ Working | KCI 웹 검색 (`poArtiSearList.kci`) | Korea only |
| **KCI-API** | ✅ Working (with key, no keyword search) | 공공데이터 Open API (`api.odcloud.kr`) | Any |
| DBpia | ❌ Removed | Korean IP blocked + JS | Korea only |

## KCI Open API 등록 방법
1. https://www.data.go.kr/data/15083283/openapi.do 접속
2. 로그인 → "활용신청" → 승인유형 **REST** 선택
3. 발급받은 ServiceKey를 환경변수 `KCI_SERVICE_KEY`에 설정
4. PythonAnywhere: Web 탭 → WSGI 파일에 `os.environ['KCI_SERVICE_KEY'] = '...'` 추가
