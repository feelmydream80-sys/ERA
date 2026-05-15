import json
import requests
from deep_translator import GoogleTranslator
from flask import Blueprint, redirect, request, session, url_for, render_template, flash
from flask import current_app

bp = Blueprint("kakao", __name__, url_prefix="/kakao")


def _build_kakao_message(paper):
    abstract_text = (paper.abstract or "").strip()
    abstract_short = abstract_text[:400]

    translated = ""
    if abstract_text and len(abstract_text) > 10:
        try:
            source_lang = "en" if all(ord(c) < 128 for c in abstract_text[:100]) else "auto"
            translated = GoogleTranslator(source=source_lang, target="ko").translate(abstract_text[:800])
        except Exception as e:
            current_app.logger.warn(f"Translation failed: {e}")

    lines = [f"📄 {paper.title[:100]}"]
    if paper.authors:
        lines.append(f"✍️ {paper.authors[:80]}")
    lines.append(f"🏷️ {paper.source}")
    if abstract_short:
        lines.append(f"\n📝 Abstract\n{abstract_short}")
    if translated:
        lines.append(f"\n📝 한글 번역\n{translated[:400]}")
    lines.append(f"\n🔗 {paper.source_url}")
    text_body = "\n".join(lines)
    if len(text_body) > 900:
        text_body = text_body[:897] + "..."

    return {
        "template_object": json.dumps({
            "object_type": "text",
            "text": text_body,
            "link": {
                "web_url": paper.source_url,
                "mobile_web_url": paper.source_url,
            },
            "button_title": "View Paper",
        })
    }


@bp.route("/login")
def login():
    redirect_uri = current_app.config["KAKAO_REDIRECT_URI"]
    client_id = current_app.config["KAKAO_REST_API_KEY"]
    if not client_id:
        flash("Kakao API key not configured", "danger")
        return redirect(url_for("feed.index"))
    paper_id = request.args.get("paper_id")
    if paper_id:
        session["share_paper_id"] = paper_id
    mode = request.args.get("mode", "me")
    session["kakao_mode"] = mode
    scope = "talk_message,friends" if mode == "friend" else "talk_message"
    auth_url = (
        f"{current_app.config['KAKAO_AUTH_URL']}"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={scope}"
    )
    return redirect(auth_url)


@bp.route("/logout")
def logout():
    token = session.pop("kakao_access_token", None)
    session.pop("kakao_refresh_token", None)
    if token:
        requests.post(
            "https://kapi.kakao.com/v1/user/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
    flash("Kakao account disconnected", "info")
    return redirect(url_for("feed.index"))


@bp.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        flash("Authorization failed", "danger")
        return redirect(url_for("feed.index"))

    token_url = current_app.config["KAKAO_TOKEN_URL"]
    data = {
        "grant_type": "authorization_code",
        "client_id": current_app.config["KAKAO_REST_API_KEY"],
        "client_secret": current_app.config["KAKAO_CLIENT_SECRET"],
        "redirect_uri": current_app.config["KAKAO_REDIRECT_URI"],
        "code": code,
    }
    resp = requests.post(token_url, data=data)
    if resp.status_code != 200:
        flash(f"Token exchange failed: {resp.text}", "danger")
        return redirect(url_for("feed.index"))

    token_data = resp.json()
    session["kakao_access_token"] = token_data.get("access_token")
    session["kakao_refresh_token"] = token_data.get("refresh_token")
    current_app.logger.info(f"Kakao token obtained, scopes: {token_data.get('scope', 'none')}")

    paper_id = session.pop("share_paper_id", None)
    mode = session.pop("kakao_mode", "me")
    if paper_id:
        if mode == "friend":
            return redirect(url_for("kakao.friend_list", paper_id=paper_id))
        return redirect(url_for("kakao.share", paper_id=paper_id))
    flash("Kakao account connected!", "success")
    return redirect(url_for("feed.index"))


@bp.route("/share/<int:paper_id>")
def share(paper_id):
    from app.models import Paper
    paper = Paper.query.get_or_404(paper_id)
    token = session.get("kakao_access_token")

    if not token:
        return redirect(url_for("kakao.login", paper_id=paper_id))

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/x-www-form-urlencoded"}
    send_url = current_app.config["KAKAO_SEND_ME_URL"]
    template_args = _build_kakao_message(paper)

    resp = requests.post(send_url, headers=headers, data=template_args)
    if resp.status_code == 200:
        flash("Paper sent to your KakaoTalk!", "success")
    elif resp.status_code == 401:
        session.pop("kakao_access_token", None)
        flash("Token expired. Please login again.", "warning")
        return redirect(url_for("kakao.login", paper_id=paper_id))
    else:
        body = resp.json()
        msg = body.get("msg", "Unknown error")
        code = body.get("code", -1)
        current_app.logger.error(f"Kakao send failed: {resp.status_code} - {body}")
        if code == -1 and msg == "Not Found":
            flash(
                "Kakao 'Send to Me' not enabled. "
                "Go to Kakao Developers > '카카오톡 메시지' > enable '나에게 보내기', "
                "then click here → "
                f"<a href='{url_for('kakao.logout')}' class='alert-link'>Re-login</a>",
                "danger",
            )
        else:
            flash(f"Failed to send (code {code}): {msg}", "danger")

    return redirect(url_for("feed.index"))


@bp.route("/friend-list/<int:paper_id>")
def friend_list(paper_id):
    from app.models import Paper
    paper = Paper.query.get_or_404(paper_id)
    token = session.get("kakao_access_token")

    if not token:
        html = (
            '<div class="text-center py-4">'
            '<p class="mb-3">카카오 로그인이 필요합니다.</p>'
            f'<a href="{url_for("kakao.login", paper_id=paper_id, mode="friend")}" '
            'class="btn btn-warning">Login with Kakao</a>'
            '</div>'
        )
        return html, 200, {"Content-Type": "text/html"}

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(current_app.config["KAKAO_FRIENDS_URL"], headers=headers)

    if resp.status_code == 401:
        session.pop("kakao_access_token", None)
        html = (
            '<div class="text-center py-4">'
            '<p class="mb-3">토큰이 만료되었습니다. 다시 로그인해 주세요.</p>'
            f'<a href="{url_for("kakao.login", paper_id=paper_id, mode="friend")}" '
            'class="btn btn-warning">Login with Kakao</a>'
            '</div>'
        )
        return html, 200, {"Content-Type": "text/html"}

    if resp.status_code == 403:
        html = (
            '<div class="text-center py-4">'
            '<p class="text-warning mb-3">Friends API 사용 권한이 없습니다.</p>'
            '<p class="small text-muted mb-3">'
            'Kakao Developers > <b>앱 설정 > 멤버</b>에서<br>'
            '자신의 카카오 계정을 앱 멤버로 추가한 후<br>'
            '다시 로그인해 주세요.'
            '</p>'
            f'<a href="{url_for("kakao.logout")}" class="btn btn-warning">Logout &amp; Retry</a>'
            '</div>'
        )
        return html, 200, {"Content-Type": "text/html"}

    if resp.status_code != 200:
        html = (
            '<div class="text-center py-4 text-danger">'
            f"<p>친구 목록을 불러오지 못했습니다. (code: {resp.status_code})</p>"
            '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>'
            '</div>'
        )
        return html, 200, {"Content-Type": "text/html"}

    data = resp.json()
    friends = data.get("elements", [])
    return render_template(
        "_friend_list.html",
        friends=friends,
        paper_id=paper_id,
        total_count=data.get("total_count", 0),
    )


@bp.route("/share/friend/<int:paper_id>", methods=["POST"])
def share_friend(paper_id):
    from app.models import Paper
    paper = Paper.query.get_or_404(paper_id)
    token = session.get("kakao_access_token")
    receiver_uuid = request.form.get("receiver_uuid")

    if not token:
        return "unauthorized", 401

    if not receiver_uuid:
        return "missing receiver_uuid", 400

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/x-www-form-urlencoded"}
    send_url = current_app.config["KAKAO_SEND_FRIEND_URL"]
    template_args = _build_kakao_message(paper)
    template_args["receiver_uuids"] = json.dumps([receiver_uuid])

    resp = requests.post(send_url, headers=headers, data=template_args)

    if resp.status_code == 200:
        return '<div class="text-center py-4 text-success"><h5>✓ Sent to friend!</h5></div>', 200, {"Content-Type": "text/html"}
    elif resp.status_code == 401:
        session.pop("kakao_access_token", None)
        return "token_expired", 401
    else:
        try:
            body = resp.json()
            msg = body.get("msg", "Unknown error")
            code = body.get("code", -1)
        except Exception:
            msg = resp.text[:200]
            code = -1
        current_app.logger.error(f"Kakao send to friend failed: {resp.status_code} - {resp.text[:300]}")
        html = (
            '<div class="text-center py-4 text-danger">'
            f"<p>전송 실패 (code {code}): {msg}</p>"
            '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>'
            '</div>'
        )
        return html, 200, {"Content-Type": "text/html"}
