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
    KAKAO_SEND_FRIEND_URL = "https://kapi.kakao.com/v2/api/talk/message/send"
    KAKAO_FRIENDS_URL = "https://kapi.kakao.com/v1/api/talk/friends"

    PAPERS_PER_PAGE = 20
