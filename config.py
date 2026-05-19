import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASEDIR, 'papers.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    KAKAO_REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY", "2331196ef286dc735ee7735b32a2e6bf")
    KAKAO_CLIENT_SECRET = os.environ.get("KAKAO_CLIENT_SECRET", "9Yd4YywG7cabXMOpT2iISlANNKlYnA5D")
    KAKAO_REDIRECT_URI = os.environ.get(
        "KAKAO_REDIRECT_URI", "http://localhost:5000/kakao/callback"
    )
    KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
    KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
    KAKAO_SEND_ME_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    # Kakao JavaScript SDK key (from Kakao Developers > Platform Keys)
    # IMPORTANT: This is DIFFERENT from the REST API key
    KAKAO_JAVASCRIPT_KEY = os.environ.get("KAKAO_JAVASCRIPT_KEY", "f95d003dc4f3c29be2866a308947b71d")

    WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "power-papers-webhook-secret-2026")

    # KCI Open API ServiceKey (from data.go.kr)
    # Register: https://www.data.go.kr/data/3049042/openapi.do
    KCI_SERVICE_KEY = os.environ.get("KCI_SERVICE_KEY", "")

    PAPERS_PER_PAGE = 20
