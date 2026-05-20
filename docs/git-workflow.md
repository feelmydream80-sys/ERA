# Git Workflow

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

### 기본 워크플로우

`git commit` 실행 시 `pre-commit` hook이 자동으로 크롤러를 실행하고 `papers.db`를 갱신합니다.

```powershell
cd C:\dev\daq
git commit -m "변경 내용"
git push origin master
```

### 크롤링 없이 코드만 커밋

크롤링 없이 코드만 올리려면 `--no-verify` 옵션 사용:
```bash
cd C:\dev\daq
git add .
git commit --no-verify -m "변경 내용 설명"
git push origin master
```

(이 경우 `papers.db`는 이전 commit 시점의 데이터가 올라갑니다.)

### PythonAnywhere 자동 반영

GitHub Webhook이 이미 설정되어 있어, `git push`만 하면 자동으로 적용됩니다.

**동작 방식:**
1. 로컬: `git commit && git push origin master`
2. GitHub가 PythonAnywhere의 `/webhook/update`로 POST 전송
3. PA에서 `git pull origin master` 실행 + WSGI touch → 자동 Reload
4. `papers.db`도 함께 pull 되어 KCI 논문 포함 모든 데이터 적용

### 패키지 변경 시
```bash
cd /home/feelmydream/daq
source venv/bin/activate
pip install -r requirements.txt
```
(이후 PythonAnywhere Reload 필수)
