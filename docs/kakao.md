# KakaoTalk

## Setup
1. https://developers.kakao.com 에서 앱 생성
2. "카카오 로그인" 활성화 + Redirect URI: `http://localhost:5000/kakao/callback` (앱 > 플랫폼 키 > REST API 키 내부)
3. "카카오톡 메시지 전송" 동의항목 설정 (카카오 로그인 > 동의항목 > 접근권한)
4. "카카오톡 메시지" 제품 설정에서 "나에게 보내기" 활성화 (필요시 권한 신청)
5. REST API 키 + Client Secret을 `config.py`에 입력 (또는 환경변수)

## 기능 설명

### "Send to Me" (나에게 보내기)
- REST API + OAuth 방식
- 사용자가 **Send to Me** 버튼 클릭 → Kakao 로그인 → `talk_message` 권한 동의 → 논문 전송
- Kakao Developers에 `https://feelmydream.pythonanywhere.com/kakao/callback` Redirect URI 등록 필수

### "Share to KakaoTalk" (친구 공유)
- JavaScript SDK 방식 (OAuth 불필요, Biz App 불필요)
- `Kakao.Share.sendDefault()` 사용
- Kakao Developers에 `https://feelmydream.pythonanywhere.com` JavaScript SDK 도메인 등록 필수
- PC에서는 카카오톡 데스크탑 앱 필요

## Message Format
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
