# from flask import Flask, jsonify, request, redirect, session
# from github_tool import get_pr_info
# from claude_brain import summarize_pr, check_contributor, load_whitelist, save_whitelist
# from jira_tool import create_jira_ticket
# from slack_tool import post_slack_message
# from calendar_tool import create_calendar_event, save_token
# import json, os, requests as req
# from datetime import datetime


# app = Flask(__name__)
# app.secret_key = os.getenv("SECRET_KEY", "nexrelease-secret-2026")

# GITHUB_CLIENT_ID     = os.getenv("GITHUB_CLIENT_ID", "")
# GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
# GITHUB_OAUTH_URL     = "https://github.com/login/oauth/authorize"
# GITHUB_TOKEN_URL     = "https://github.com/login/oauth/access_token"
# GITHUB_API_URL       = "https://api.github.com/user"
# GITHUB_EMAILS_URL    = "https://api.github.com/user/emails"

# NOTIFICATIONS_DIR = "user_notifications"
# os.makedirs(NOTIFICATIONS_DIR, exist_ok=True)

# def notif_file(username):
#     return os.path.join(NOTIFICATIONS_DIR, f"{username.lower()}.json")

# def load_notifications(username):
#     f = notif_file(username)
#     if not os.path.exists(f):
#         return []
#     with open(f) as fp:
#         return json.load(fp)

# def save_notifications(username, notifications):
#     with open(notif_file(username), "w") as fp:
#         json.dump(notifications, fp)

# def add_notification(username, pr_number, pr_title, author, jira_url,
#                      slack_posted, meeting, security, pr_url,
#                      summary, checklist, risks, slack_message, pending=False):
#     notifications = load_notifications(username)
#     notifications.insert(0, {
#         "id": len(notifications),
#         "time": datetime.now().strftime("%H:%M"),
#         "pr_number": pr_number, "pr_title": pr_title, "author": author,
#         "jira_url": jira_url, "slack_posted": slack_posted, "meeting": meeting,
#         "security": security, "pr_url": pr_url, "summary": summary,
#         "checklist": checklist, "risks": risks, "slack_message": slack_message,
#         "pending": pending
#     })
#     save_notifications(username, notifications)

# PROFILES_FILE = "user_profiles.json"

# def load_profiles():
#     if not os.path.exists(PROFILES_FILE):
#         return {}
#     with open(PROFILES_FILE) as f:
#         return json.load(f)

# def save_profiles(profiles):
#     with open(PROFILES_FILE, "w") as f:
#         json.dump(profiles, f)

# def get_profile(username):
#     return load_profiles().get(username.lower(), {})

# def save_profile(username, data):
#     profiles = load_profiles()
#     profiles[username.lower()] = data
#     save_profiles(profiles)

# def get_user_jira(username):
#     profile = get_profile(username)
#     return {
#         "jira_domain":      profile.get("jira_domain", ""),
#         "jira_email":       profile.get("jira_email", ""),
#         "jira_api_token":   profile.get("jira_api_token", ""),
#         "jira_project_key": profile.get("jira_project_key", "KAN"),
#     }

# def get_user_slack(username):
#     profile = get_profile(username)
#     return {
#         "slack_token":   profile.get("slack_token", ""),
#         "slack_channel": profile.get("slack_channel", "releases"),
#     }

# def ensure_owner_whitelisted(repo):
#     if not repo or "/" not in repo:
#         return
#     owner = repo.split("/")[0]
#     members = load_whitelist()
#     if owner.lower() not in [m.lower() for m in members]:
#         members.append(owner)
#         save_whitelist(members)

# def get_github_user(access_token):
#     resp = req.get(GITHUB_API_URL, headers={
#         "Authorization": f"token {access_token}", "Accept": "application/json"
#     })
#     return resp.json() if resp.status_code == 200 else None

# def get_github_email(access_token):
#     resp = req.get(GITHUB_EMAILS_URL, headers={
#         "Authorization": f"token {access_token}", "Accept": "application/json"
#     })
#     if resp.status_code == 200:
#         for e in resp.json():
#             if e.get("primary") and e.get("verified"):
#                 return e.get("email", "")
#         for e in resp.json():
#             if e.get("verified"):
#                 return e.get("email", "")
#     return ""

# def get_github_repos(access_token):
#     resp = req.get(
#         "https://api.github.com/user/repos?per_page=100&sort=updated&type=all",
#         headers={"Authorization": f"token {access_token}", "Accept": "application/json"}
#     )
#     return [r["full_name"] for r in resp.json()] if resp.status_code == 200 else []

# def get_repo_prs_list(access_token, repo):
#     resp = req.get(
#         f"https://api.github.com/repos/{repo}/pulls?state=closed&per_page=20",
#         headers={"Authorization": f"token {access_token}", "Accept": "application/json"}
#     )
#     if resp.status_code == 200:
#         return [{"number": p["number"], "title": p["title"]}
#                 for p in resp.json() if p.get("merged_at")]
#     return []

# # ── GitHub OAuth ───────────────────────────────────────────────────────────────
# @app.route("/oauth/login")
# def oauth_login():
#     if not GITHUB_CLIENT_ID:
#         return redirect("/?error=no_oauth_config")
#     return redirect(f"{GITHUB_OAUTH_URL}?client_id={GITHUB_CLIENT_ID}&scope=read:user user:email repo")

# @app.route("/oauth/callback")
# def oauth_callback():
#     code = request.args.get("code")
#     if not code:
#         return redirect("/?error=oauth_cancelled")
#     if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
#         return redirect("/?error=no_oauth_config")

#     resp = req.post(GITHUB_TOKEN_URL, json={
#         "client_id": GITHUB_CLIENT_ID, "client_secret": GITHUB_CLIENT_SECRET, "code": code
#     }, headers={"Accept": "application/json"})
#     access_token = resp.json().get("access_token", "")
#     if not access_token:
#         return redirect("/?error=oauth_failed")

#     github_user = get_github_user(access_token)
#     if not github_user:
#         return redirect("/?error=user_fetch_failed")

#     github_email = get_github_email(access_token) or github_user.get("email") or f"{github_user['login']}@github.local"

#     session["github_username"] = github_user["login"]
#     session["github_email"]    = github_email
#     session["github_token"]    = access_token
#     session["github_avatar"]   = github_user.get("avatar_url", "")
#     session["github_name"]     = github_user.get("name") or github_user["login"]

#     members = load_whitelist()
#     if github_user["login"].lower() not in [m.lower() for m in members]:
#         members.append(github_user["login"])
#         save_whitelist(members)

#     profile = get_profile(github_user["login"])
#     if profile.get("jira_api_token") and profile.get("slack_token"):
#         return redirect("/app")
#     return redirect("/setup")

# @app.route("/oauth/logout")
# def oauth_logout():
#     session.clear()
#     return redirect("/")

# # ── Google Calendar OAuth ──────────────────────────────────────────────────────
# @app.route("/oauth/google")
# def google_oauth():
#     try:
#         from google_auth_oauthlib.flow import Flow
#         if not os.path.exists("credentials.json"):
#             return jsonify({"error": "credentials.json not found."})
#         flow = Flow.from_client_secrets_file(
#             "credentials.json",
#             scopes=["https://www.googleapis.com/auth/calendar"],
#             redirect_uri="http://localhost:5000/oauth/google/callback"
#         )
#         auth_url, state = flow.authorization_url(access_type="offline", prompt="consent")
#         with open("oauth_state.txt", "w") as f:
#             f.write(state)
#         return jsonify({"auth_url": auth_url})
#     except Exception as e:
#         return jsonify({"error": str(e)})

# @app.route("/oauth/google/callback")
# def google_oauth_callback():
#     try:
#         from google_auth_oauthlib.flow import Flow
#         state = open("oauth_state.txt").read() if os.path.exists("oauth_state.txt") else None
#         flow = Flow.from_client_secrets_file(
#             "credentials.json",
#             scopes=["https://www.googleapis.com/auth/calendar"],
#             state=state,
#             redirect_uri="http://localhost:5000/oauth/google/callback"
#         )
#         flow.fetch_token(authorization_response=request.url)
#         save_token(flow.credentials)
#         return "<html><body style='background:#07080f;color:#0d9488;font-family:monospace;display:flex;align-items:center;justify-content:center;height:100vh;'><div style='text-align:center'><div style='font-size:48px'>✅</div><div style='font-size:20px;margin-top:16px'>Google Calendar Connected!</div><script>setTimeout(()=>window.close(),2000)</script></div></body></html>"
#     except Exception as e:
#         return f"<html><body style='background:#07080f;color:#f43f5e;font-family:monospace;display:flex;align-items:center;justify-content:center;height:100vh;'><div>❌ {str(e)}</div></body></html>"

# @app.route("/oauth/google/status")
# def google_oauth_status():
#     return jsonify({"connected": os.path.exists("token.pickle")})

# # ── Landing ────────────────────────────────────────────────────────────────────
# @app.route("/")
# def landing():
#     if session.get("github_username"):
#         return redirect("/app")

#     error = request.args.get("error", "")
#     error_messages = {
#         "oauth_failed":      "GitHub authentication failed. Please try again.",
#         "oauth_cancelled":   "Login was cancelled. Please try again.",
#         "user_fetch_failed": "Could not retrieve your GitHub profile. Please try again.",
#         "no_oauth_config":   "OAuth is not configured on this server.",
#     }
#     error_text = error_messages.get(error, "")
#     has_oauth  = bool(GITHUB_CLIENT_ID)

#     return f"""<!DOCTYPE html>
# <html lang="en">
# <head>
# <meta charset="UTF-8"/>
# <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
# <title>NexRelease — Sign In</title>
# <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Outfit:wght@400;600;700;800;900&display=swap" rel="stylesheet"/>
# <style>
# :root{{--bg:#07080f;--card:#121526;--border2:#252844;--accent:#7c3aed;--accent2:#0ea5e9;--teal:#0d9488;--rose:#f43f5e;--text:#e2e4f0;--muted:#4a5080;--muted2:#6b7199;--mono:'DM Mono',monospace;--sans:'Outfit',sans-serif;}}
# *,*::before,*::after{{margin:0;padding:0;box-sizing:border-box;}}
# body{{font-family:var(--sans);background:var(--bg);color:var(--text);min-height:100vh;display:flex;align-items:center;justify-content:center;}}
# body::before{{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 600px 400px at 20% 30%,rgba(124,58,237,0.08) 0%,transparent 70%),radial-gradient(ellipse 500px 300px at 80% 70%,rgba(14,165,233,0.06) 0%,transparent 70%);pointer-events:none;}}
# body::after{{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(124,58,237,0.025) 1px,transparent 1px),linear-gradient(90deg,rgba(124,58,237,0.025) 1px,transparent 1px);background-size:48px 48px;pointer-events:none;}}
# .card{{background:var(--card);border:1px solid var(--border2);border-radius:24px;padding:52px 48px;max-width:460px;width:92%;text-align:center;position:relative;overflow:hidden;animation:fadeUp 0.5s ease both;}}
# .card::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(124,58,237,0.6),rgba(14,165,233,0.6),transparent);}}
# .logo{{display:flex;align-items:center;justify-content:center;gap:14px;margin-bottom:8px;}}
# .logo-icon{{width:52px;height:52px;border-radius:14px;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;font-size:26px;box-shadow:0 0 32px rgba(124,58,237,0.45);}}
# .logo-text{{font-size:28px;font-weight:900;letter-spacing:-1px;}}
# .logo-text .nex{{color:transparent;background:linear-gradient(90deg,#a78bfa,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
# .by-line{{font-family:var(--mono);font-size:11px;color:var(--muted2);margin-bottom:32px;}}
# h2{{font-size:22px;font-weight:800;margin-bottom:10px;}}
# .sub{{font-size:14px;color:var(--muted2);line-height:1.7;margin-bottom:28px;}}
# .features{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:32px;text-align:left;}}
# .feat{{background:rgba(124,58,237,0.06);border:1px solid rgba(124,58,237,0.15);border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:10px;color:var(--muted2);}}
# .feat strong{{color:#a78bfa;display:block;margin-bottom:3px;}}
# .oauth-btn{{display:flex;align-items:center;justify-content:center;gap:12px;width:100%;padding:15px;background:linear-gradient(135deg,#1a1a2e,#16213e);color:var(--text);border:1px solid rgba(255,255,255,0.12);border-radius:12px;font-family:var(--sans);font-size:15px;font-weight:700;cursor:pointer;text-decoration:none;transition:transform 0.15s,box-shadow 0.2s;margin-bottom:16px;}}
# .oauth-btn:hover{{transform:translateY(-2px);box-shadow:0 8px 28px rgba(0,0,0,0.4);}}
# .github-icon{{width:22px;height:22px;fill:var(--text);flex-shrink:0;}}
# .error-box{{background:rgba(244,63,94,0.08);border:1px solid rgba(244,63,94,0.25);border-radius:8px;padding:12px 14px;font-family:var(--mono);font-size:11px;color:#f87171;margin-bottom:20px;text-align:left;display:{"block" if error_text else "none"};}}
# .security-note{{font-family:var(--mono);font-size:10px;color:var(--muted);margin-top:18px;line-height:2;padding-top:18px;border-top:1px solid var(--border2);}}
# .security-note .ok{{color:var(--teal);}}
# @keyframes fadeUp{{from{{opacity:0;transform:translateY(16px);}}to{{opacity:1;transform:translateY(0);}}}}
# </style>
# </head>
# <body>
# <div class="card">
#   <div class="logo">
#     <div class="logo-icon">⚡</div>
#     <div class="logo-text"><span class="nex">Nex</span>Release</div>
#   </div>
#   <div class="by-line">by Schrodingers</div>
#   <h2>AI Release Coordinator</h2>
#   <div class="sub">Automate PR coordination with Jira, Slack and go/no-go meetings — powered by MCP agents.</div>
#   <div class="features">
#     <div class="feat"><strong>🔀 PR Agent</strong>Reads & summarizes every PR</div>
#     <div class="feat"><strong>🎫 Jira</strong>Auto-creates tickets</div>
#     <div class="feat"><strong>💬 Slack</strong>Posts release notes</div>
#     <div class="feat"><strong>🔐 Security</strong>Detects unauthorized contributors</div>
#   </div>
#   {'<div class="error-box">⚠ ' + error_text + '</div>' if error_text else ''}
#   {'<a href="/oauth/login" class="oauth-btn"><svg class="github-icon" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>Continue with GitHub</a>' if has_oauth else '<div style="background:rgba(74,80,128,0.1);border:1px solid rgba(74,80,128,0.2);border-radius:10px;padding:16px;font-family:var(--mono);font-size:11px;color:var(--muted2);">⚠️ GitHub OAuth not configured.</div>'}
#   <div class="security-note"><span class="ok">🔒 Secure authentication only.</span><br>Login requires a verified GitHub account.<br>We never see or store your GitHub password.</div>
# </div>
# </body>
# </html>"""

# # ── Setup ──────────────────────────────────────────────────────────────────────
# @app.route("/setup", methods=["GET", "POST"])
# def setup():
#     username = session.get("github_username")
#     if not username:
#         return redirect("/")

#     if request.method == "POST":
#         jira_domain      = request.form.get("jira_domain", "").strip().replace("https://", "").replace("http://", "")
#         jira_email       = request.form.get("jira_email", "").strip()
#         jira_api_token   = request.form.get("jira_api_token", "").strip()
#         jira_project_key = request.form.get("jira_project_key", "KAN").strip() or "KAN"
#         slack_token      = request.form.get("slack_token", "").strip()
#         slack_channel    = request.form.get("slack_channel", "releases").strip() or "releases"

#         if not jira_domain or not jira_email or not jira_api_token or not slack_token:
#             return redirect("/setup?error=missing")

#         save_profile(username, {
#             "jira":              jira_email,
#             "jira_domain":       jira_domain,
#             "jira_email":        jira_email,
#             "jira_api_token":    jira_api_token,
#             "jira_project_key":  jira_project_key,
#             "slack":             slack_token,
#             "slack_token":       slack_token,
#             "slack_channel":     slack_channel,
#         })
#         return redirect("/app")

#     error        = request.args.get("error", "")
#     github_email = session.get("github_email", "")
#     github_name  = session.get("github_name", username)
#     avatar       = session.get("github_avatar", "")

#     return f"""<!DOCTYPE html>
# <html lang="en">
# <head>
# <meta charset="UTF-8"/>
# <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
# <title>NexRelease — Connect Tools</title>
# <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Outfit:wght@400;600;700;800;900&display=swap" rel="stylesheet"/>
# <style>
# :root{{--bg:#07080f;--card:#121526;--surface:#0d0f1a;--border2:#252844;--accent:#7c3aed;--accent2:#0ea5e9;--teal:#0d9488;--rose:#f43f5e;--text:#e2e4f0;--muted:#4a5080;--muted2:#6b7199;--mono:'DM Mono',monospace;--sans:'Outfit',sans-serif;}}
# *{{margin:0;padding:0;box-sizing:border-box;}}
# body{{font-family:var(--sans);background:var(--bg);color:var(--text);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px;}}
# .card{{background:var(--card);border:1px solid var(--border2);border-radius:24px;padding:44px 40px;max-width:540px;width:100%;position:relative;overflow:hidden;animation:fadeUp 0.4s ease both;}}
# .card::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(124,58,237,0.5),rgba(14,165,233,0.5),transparent);}}
# .user-bar{{display:flex;align-items:center;gap:12px;background:rgba(124,58,237,0.06);border:1px solid rgba(124,58,237,0.15);border-radius:10px;padding:12px 16px;margin-bottom:28px;}}
# .avatar{{width:38px;height:38px;border-radius:50%;border:2px solid rgba(124,58,237,0.3);}}
# .avatar-fallback{{width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;color:#fff;flex-shrink:0;}}
# .user-info{{flex:1;}}
# .user-name{{font-size:14px;font-weight:700;}}
# .user-email{{font-family:var(--mono);font-size:11px;color:var(--teal);}}
# h2{{font-size:22px;font-weight:800;margin-bottom:8px;}}
# .sub{{font-size:13px;color:var(--muted2);line-height:1.6;margin-bottom:24px;}}
# .section-label{{font-family:var(--mono);font-size:10px;color:var(--muted2);text-transform:uppercase;letter-spacing:0.1em;margin:20px 0 10px;display:flex;align-items:center;gap:8px;}}
# .section-label::after{{content:'';flex:1;height:1px;background:var(--border2);}}
# .form-group{{display:flex;flex-direction:column;gap:6px;margin-bottom:12px;}}
# label{{font-family:var(--mono);font-size:10px;color:var(--muted2);text-transform:uppercase;letter-spacing:0.1em;}}
# input{{background:var(--surface);border:1px solid var(--border2);color:var(--text);padding:11px 14px;border-radius:9px;font-family:var(--mono);font-size:13px;outline:none;width:100%;transition:border-color 0.2s;}}
# input:focus{{border-color:var(--accent);box-shadow:0 0 0 3px rgba(124,58,237,0.1);}}
# .two-col{{display:grid;grid-template-columns:1fr 1fr;gap:12px;}}
# .hint{{background:rgba(14,165,233,0.05);border:1px solid rgba(14,165,233,0.15);border-radius:7px;padding:9px 12px;font-family:var(--mono);font-size:10px;color:#7dd3fc;margin-top:6px;line-height:1.8;}}
# .btn{{width:100%;padding:14px;background:linear-gradient(135deg,var(--accent),#6d28d9);color:#fff;border:none;border-radius:11px;font-family:var(--sans);font-size:15px;font-weight:700;cursor:pointer;margin-top:16px;transition:transform 0.15s;}}
# .btn:hover{{transform:translateY(-2px);}}
# .error-box{{background:rgba(244,63,94,0.08);border:1px solid rgba(244,63,94,0.2);border-radius:8px;padding:10px 14px;font-family:var(--mono);font-size:11px;color:#f87171;margin-bottom:16px;display:{"block" if error else "none"};}}
# .logout-link{{font-family:var(--mono);font-size:11px;color:var(--muted2);text-align:center;margin-top:20px;}}
# .logout-link a{{color:var(--rose);text-decoration:none;}}
# @keyframes fadeUp{{from{{opacity:0;transform:translateY(16px);}}to{{opacity:1;transform:translateY(0);}}}}
# </style>
# </head>
# <body>
# <div class="card">
#   <div class="user-bar">
#     {'<img class="avatar" src="' + avatar + '" alt=""/>' if avatar else '<div class="avatar-fallback">' + username[0].upper() + '</div>'}
#     <div class="user-info">
#       <div class="user-name">{github_name}</div>
#       <div class="user-email">✓ {github_email}</div>
#     </div>
#   </div>
#   <h2>Connect Your Tools</h2>
#   <div class="sub">Your credentials are stored privately — Jira tickets go to <strong>your</strong> Jira, not anyone else's.</div>
#   <div class="error-box">All required fields must be filled in.</div>
#   <form method="POST">
#     <div class="section-label">Jira</div>
#     <div class="form-group">
#       <label>Jira Domain *</label>
#       <input type="text" name="jira_domain" placeholder="yourname.atlassian.net" required/>
#       <div class="hint">Just the domain — e.g. prateekmanocha22.atlassian.net</div>
#     </div>
#     <div class="two-col">
#       <div class="form-group">
#         <label>Jira Email *</label>
#         <input type="email" name="jira_email" placeholder="you@email.com" value="{github_email}" required/>
#       </div>
#       <div class="form-group">
#         <label>Project Key</label>
#         <input type="text" name="jira_project_key" placeholder="KAN" value="KAN"/>
#       </div>
#     </div>
#     <div class="form-group">
#       <label>Jira API Token *</label>
#       <input type="password" name="jira_api_token" placeholder="your Jira API token" required/>
#       <div class="hint">Get it at id.atlassian.com → Security → API tokens</div>
#     </div>
#     <div class="section-label">Slack</div>
#     <div class="two-col">
#       <div class="form-group">
#         <label>Slack Bot Token *</label>
#         <input type="password" name="slack_token" placeholder="xoxb-..." required/>
#       </div>
#       <div class="form-group">
#         <label>Channel</label>
#         <input type="text" name="slack_channel" placeholder="releases" value="releases"/>
#       </div>
#     </div>
#     <div class="hint">Get Slack token at api.slack.com → Your App → OAuth & Permissions</div>
#     <button type="submit" class="btn">🚀 Launch NexRelease Agent</button>
#   </form>
#   <div class="logout-link"><a href="/oauth/logout">← Use a different account</a></div>
# </div>
# </body>
# </html>"""

# # ── Main app ───────────────────────────────────────────────────────────────────
# @app.route("/app")
# def main_app():
#     username = session.get("github_username")
#     if not username:
#         return redirect("/")
#     profile = get_profile(username)
#     if not profile.get("jira_api_token") or not profile.get("slack_token"):
#         return redirect("/setup")

#     github_name  = session.get("github_name", username)
#     avatar       = session.get("github_avatar", "")
#     access_token = session.get("github_token", "")
#     repos        = get_github_repos(access_token) if access_token else []
#     repos_json   = json.dumps(repos)

#     return f"""<!DOCTYPE html>
# <html lang="en">
# <head>
# <meta charset="UTF-8"/>
# <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
# <title>NexRelease</title>
# <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;600;700;800;900&display=swap" rel="stylesheet"/>
# <style>
# :root {{
#   --bg:#07080f;--surface:#0d0f1a;--card:#121526;--card2:#161929;--border:#1e2240;--border2:#252844;--accent:#7c3aed;--accent2:#0ea5e9;--teal:#0d9488;--red:#dc2626;--rose:#f43f5e;--gold:#f59e0b;--text:#e2e4f0;--muted:#4a5080;--muted2:#6b7199;--mono:'DM Mono',monospace;--sans:'Outfit',sans-serif;
# }}
# *,*::before,*::after{{margin:0;padding:0;box-sizing:border-box;}}
# html{{scroll-behavior:smooth;}}
# body{{font-family:var(--sans);background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden;}}
# body::before{{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 600px 400px at 10% 20%,rgba(124,58,237,0.06) 0%,transparent 70%),radial-gradient(ellipse 500px 300px at 90% 80%,rgba(14,165,233,0.05) 0%,transparent 70%);pointer-events:none;z-index:0;}}
# body::after{{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(124,58,237,0.025) 1px,transparent 1px),linear-gradient(90deg,rgba(124,58,237,0.025) 1px,transparent 1px);background-size:48px 48px;pointer-events:none;z-index:0;}}
# .layout{{position:relative;z-index:1;display:grid;grid-template-columns:1fr 300px;min-height:100vh;}}
# .main-col{{overflow-y:auto;border-right:1px solid var(--border);}}
# .wrap{{max-width:820px;margin:0 auto;padding:0 36px 100px;}}
# header{{display:flex;align-items:center;justify-content:space-between;padding:28px 0 40px;border-bottom:1px solid var(--border);margin-bottom:48px;flex-wrap:wrap;gap:12px;}}
# .logo{{display:flex;flex-direction:column;gap:4px;}}
# .logo-row{{display:flex;align-items:center;gap:14px;}}
# .logo-icon{{width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;font-size:20px;box-shadow:0 0 24px rgba(124,58,237,0.4);}}
# .logo-text{{font-size:22px;font-weight:900;letter-spacing:-0.8px;}}
# .logo-text .nex{{color:transparent;background:linear-gradient(90deg,#a78bfa,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
# .logo-subtitle{{font-family:var(--mono);font-size:10px;color:var(--muted2);padding-left:54px;}}
# .header-right{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;}}
# .user-pill{{font-family:var(--mono);font-size:11px;padding:6px 12px;border-radius:20px;border:1px solid rgba(124,58,237,0.3);color:#a78bfa;display:flex;align-items:center;gap:8px;background:rgba(124,58,237,0.06);}}
# .user-pill img{{width:18px;height:18px;border-radius:50%;}}
# .status-pill{{font-family:var(--mono);font-size:11px;padding:6px 12px;border-radius:20px;border:1px solid rgba(13,148,136,0.4);color:var(--teal);display:flex;align-items:center;gap:7px;background:rgba(13,148,136,0.06);}}
# .pulse-dot{{width:7px;height:7px;background:var(--teal);border-radius:50%;animation:pulse 2s infinite;}}
# .logout-btn{{font-family:var(--mono);font-size:10px;color:var(--rose);background:transparent;border:1px solid rgba(244,63,94,0.25);border-radius:6px;padding:5px 10px;cursor:pointer;text-decoration:none;}}
# .logout-btn:hover{{background:rgba(244,63,94,0.08);}}
# .hero{{margin-bottom:44px;}}
# .hero-eyebrow{{font-family:var(--mono);font-size:11px;color:var(--accent2);letter-spacing:0.15em;text-transform:uppercase;margin-bottom:16px;display:flex;align-items:center;gap:10px;}}
# .hero-eyebrow::before{{content:'';width:20px;height:1px;background:var(--accent2);}}
# .hero h1{{font-size:clamp(28px,4vw,46px);font-weight:900;line-height:1.08;letter-spacing:-2px;margin-bottom:14px;}}
# .grad-purple{{background:linear-gradient(90deg,#a78bfa,#7c3aed,#0ea5e9);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
# .hero p{{font-size:15px;color:var(--muted2);line-height:1.75;max-width:520px;}}
# .pipeline{{display:flex;align-items:center;margin-bottom:40px;overflow-x:auto;padding:4px 0 8px;}}
# .pipe-step{{display:flex;flex-direction:column;align-items:center;gap:7px;flex-shrink:0;}}
# .pipe-icon{{width:48px;height:48px;background:var(--card);border:1px solid var(--border2);border-radius:13px;display:flex;align-items:center;justify-content:center;font-size:20px;transition:all 0.35s;}}
# .pipe-step.active .pipe-icon{{border-color:var(--accent);box-shadow:0 0 0 3px rgba(124,58,237,0.15);transform:translateY(-4px);}}
# .pipe-step.done .pipe-icon{{border-color:var(--teal);background:rgba(13,148,136,0.08);}}
# .pipe-label{{font-family:var(--mono);font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;}}
# .pipe-step.active .pipe-label,.pipe-step.done .pipe-label{{color:var(--teal);}}
# .pipe-arrow{{width:28px;height:2px;background:var(--border2);flex-shrink:0;margin-bottom:22px;position:relative;transition:background 0.4s;}}
# .pipe-arrow.lit{{background:linear-gradient(90deg,var(--teal),var(--accent2));}}
# .pipe-arrow::after{{content:'';position:absolute;right:-5px;top:-3px;border:4px solid transparent;border-left-color:inherit;}}
# .pipe-arrow.lit::after{{border-left-color:var(--accent2);}}
# .panel{{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:28px;margin-bottom:20px;position:relative;overflow:hidden;}}
# .panel::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(124,58,237,0.3),transparent);}}
# .panel-title{{font-size:11px;font-weight:700;color:var(--muted2);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:20px;display:flex;align-items:center;gap:10px;}}
# .panel-title::before{{content:'';width:3px;height:14px;background:var(--accent);border-radius:2px;}}
# .repo-row{{display:flex;gap:12px;align-items:flex-end;flex-wrap:wrap;margin-bottom:14px;}}
# .repo-group{{display:flex;flex-direction:column;gap:6px;flex:1;min-width:180px;}}
# .repo-group label,.field label{{font-family:var(--mono);font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;}}
# select{{background:var(--surface);border:1px solid var(--border2);color:var(--text);padding:10px 14px;border-radius:9px;font-family:var(--mono);font-size:13px;outline:none;width:100%;}}
# select:focus{{border-color:var(--accent);box-shadow:0 0 0 3px rgba(124,58,237,0.12);}}
# select option{{background:var(--surface);}}
# .field{{display:flex;flex-direction:column;gap:6px;}}
# input[type="number"],input[type="text"]{{background:var(--surface);border:1px solid var(--border2);color:var(--text);padding:10px 14px;border-radius:9px;font-family:var(--mono);font-size:13px;outline:none;transition:border-color 0.2s,box-shadow 0.2s;}}
# input[type="number"]{{width:100px;}}
# input[type="text"]{{width:200px;}}
# input:focus{{border-color:var(--accent);box-shadow:0 0 0 3px rgba(124,58,237,0.12);}}
# .run-btn{{padding:11px 24px;background:linear-gradient(135deg,var(--accent),#6d28d9);color:#fff;border:none;border-radius:9px;font-family:var(--sans);font-size:14px;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:8px;transition:transform 0.15s,box-shadow 0.2s;box-shadow:0 4px 20px rgba(124,58,237,0.3);}}
# .run-btn:hover{{transform:translateY(-2px);box-shadow:0 8px 28px rgba(124,58,237,0.45);}}
# .run-btn:disabled{{background:var(--border);color:var(--muted);cursor:not-allowed;transform:none;box-shadow:none;}}
# .secondary-btn{{padding:9px 16px;background:transparent;color:var(--accent2);border:1px solid rgba(14,165,233,0.3);border-radius:9px;font-family:var(--sans);font-size:13px;font-weight:600;cursor:pointer;}}
# .secondary-btn:hover{{background:rgba(14,165,233,0.08);}}
# .danger-btn{{padding:5px 10px;background:transparent;color:var(--rose);border:1px solid rgba(244,63,94,0.3);border-radius:6px;font-family:var(--mono);font-size:10px;cursor:pointer;}}
# .danger-btn:hover{{background:rgba(244,63,94,0.1);}}
# .pr-suggestions{{background:var(--surface);border:1px solid var(--border2);border-radius:9px;overflow:hidden;margin-bottom:14px;display:none;max-height:200px;overflow-y:auto;}}
# .pr-item{{padding:10px 14px;cursor:pointer;border-bottom:1px solid var(--border);font-family:var(--mono);font-size:12px;display:flex;align-items:center;gap:10px;transition:background 0.15s;}}
# .pr-item:last-child{{border-bottom:none;}}
# .pr-item:hover{{background:rgba(124,58,237,0.07);}}
# .pr-num{{color:var(--accent2);font-size:11px;flex-shrink:0;}}
# .pr-title-text{{color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
# .pr-loading{{padding:12px 14px;font-family:var(--mono);font-size:11px;color:var(--muted);}}
# .terminal{{background:#050609;border:1px solid var(--border2);border-radius:12px;overflow:hidden;}}
# .terminal-bar{{background:var(--surface);border-bottom:1px solid var(--border);padding:10px 16px;display:flex;align-items:center;gap:8px;}}
# .tdot{{width:10px;height:10px;border-radius:50%;}}
# .tdot.r{{background:#ff5f57;}}.tdot.y{{background:#ffbd2e;}}.tdot.g{{background:#28c941;}}
# .terminal-title{{font-family:var(--mono);font-size:11px;color:var(--muted);margin-left:8px;}}
# .terminal-body{{padding:18px;font-family:var(--mono);font-size:12px;line-height:2.1;min-height:140px;}}
# .t-muted{{color:var(--muted);}}.t-purple{{color:#a78bfa;}}.t-blue{{color:var(--accent2);}}.t-teal{{color:var(--teal);}}.t-warn{{color:#fb923c;}}.t-red{{color:var(--rose);}}.t-white{{color:var(--text);}}
# .step-boxes{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:20px;}}
# .step-box{{background:var(--surface);border:1px solid var(--border2);border-radius:11px;padding:15px;transition:border-color 0.3s;}}
# .step-box.done{{border-color:rgba(13,148,136,0.35);}}.step-box.error{{border-color:rgba(244,63,94,0.4);}}
# .step-box-label{{font-family:var(--mono);font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;}}
# .step-box-val{{font-size:13px;color:var(--text);line-height:1.5;word-break:break-all;}}
# .step-box-val a{{color:var(--accent2);text-decoration:none;}}.step-box-val a:hover{{text-decoration:underline;}}
# .badge{{display:inline-flex;align-items:center;gap:5px;padding:3px 9px;border-radius:5px;font-family:var(--mono);font-size:11px;font-weight:700;}}
# .badge.ok{{background:rgba(13,148,136,0.12);color:var(--teal);border:1px solid rgba(13,148,136,0.3);}}
# .badge.err{{background:rgba(244,63,94,0.1);color:var(--rose);border:1px solid rgba(244,63,94,0.3);}}
# .hint{{margin-top:16px;background:rgba(14,165,233,0.04);border:1px solid rgba(14,165,233,0.15);border-radius:9px;padding:12px 15px;font-family:var(--mono);font-size:11px;color:#7dd3fc;display:flex;align-items:center;gap:8px;}}
# .hint code{{background:rgba(0,0,0,0.4);padding:2px 7px;border-radius:4px;}}
# .member-row{{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border);}}
# .member-row:last-child{{border-bottom:none;}}
# .member-name{{font-family:var(--mono);font-size:13px;color:var(--text);}}
# .add-row{{display:flex;gap:10px;margin-top:16px;}}
# .add-row input[type="text"]{{flex:1;width:auto;}}
# .cal-status-row{{display:flex;align-items:center;gap:12px;flex-wrap:wrap;}}
# .spin{{display:inline-block;width:13px;height:13px;border:2px solid var(--border2);border-top-color:var(--accent);border-radius:50%;animation:spin 0.7s linear infinite;vertical-align:middle;margin-right:4px;}}
# .sec-modal{{position:fixed;inset:0;z-index:300;background:rgba(5,6,15,0.94);backdrop-filter:blur(14px);display:none;align-items:center;justify-content:center;}}
# .sec-modal.open{{display:flex;animation:fadeUp 0.3s ease;}}
# .sec-panel{{background:var(--card);border:2px solid rgba(220,38,38,0.6);border-radius:20px;padding:40px;max-width:520px;width:92%;text-align:center;box-shadow:0 0 80px rgba(220,38,38,0.1);}}
# .sec-icon{{font-size:48px;margin-bottom:16px;display:block;animation:pulse 1s infinite;}}
# .sec-title{{font-family:var(--mono);font-size:11px;font-weight:700;color:var(--rose);letter-spacing:0.15em;text-transform:uppercase;margin-bottom:12px;}}
# .sec-sub{{font-size:14px;color:var(--text);line-height:1.8;margin-bottom:14px;}}
# .sec-details{{font-family:var(--mono);font-size:11px;color:var(--muted2);background:rgba(220,38,38,0.06);border:1px solid rgba(220,38,38,0.2);border-radius:10px;padding:12px 14px;text-align:left;line-height:2.2;margin-bottom:4px;}}
# .sec-actions{{display:flex;gap:8px;justify-content:center;margin-top:20px;flex-wrap:wrap;}}
# .sec-dismiss{{padding:10px 16px;background:transparent;color:var(--muted2);border:1px solid var(--border2);border-radius:9px;font-family:var(--sans);font-size:13px;font-weight:700;cursor:pointer;}}
# .sec-view{{padding:10px 16px;background:linear-gradient(135deg,var(--red),var(--rose));color:#fff;border:none;border-radius:9px;font-family:var(--sans);font-size:13px;font-weight:700;cursor:pointer;}}
# .sec-approve{{padding:10px 16px;background:rgba(13,148,136,0.15);color:var(--teal);border:1px solid rgba(13,148,136,0.35);border-radius:9px;font-family:var(--sans);font-size:13px;font-weight:700;cursor:pointer;}}
# .sec-whitelist{{padding:10px 16px;background:rgba(124,58,237,0.1);color:#a78bfa;border:1px solid rgba(124,58,237,0.25);border-radius:9px;font-family:var(--sans);font-size:13px;font-weight:700;cursor:pointer;}}
# .detail-overlay{{position:fixed;inset:0;z-index:100;background:rgba(5,6,15,0.88);backdrop-filter:blur(10px);display:none;align-items:flex-start;justify-content:flex-end;}}
# .detail-overlay.open{{display:flex;}}
# .detail-panel{{width:min(660px,95vw);height:100vh;overflow-y:auto;background:var(--surface);border-left:1px solid var(--border2);padding:32px;animation:slideIn 0.3s ease;}}
# .detail-panel::-webkit-scrollbar{{width:3px;}}.detail-panel::-webkit-scrollbar-thumb{{background:var(--border2);border-radius:2px;}}
# .detail-close{{position:sticky;top:0;display:flex;justify-content:flex-end;margin-bottom:20px;}}
# .detail-close button{{background:var(--card);border:1px solid var(--border2);color:var(--text);font-size:16px;width:34px;height:34px;border-radius:8px;cursor:pointer;}}
# .detail-hero{{margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid var(--border);}}
# .detail-pr-num{{font-family:var(--mono);font-size:10px;color:var(--accent2);margin-bottom:6px;}}
# .detail-title{{font-size:19px;font-weight:800;line-height:1.3;margin-bottom:8px;}}
# .detail-author{{font-family:var(--mono);font-size:11px;color:var(--muted2);}}
# .detail-time{{font-family:var(--mono);font-size:10px;color:var(--muted);margin-top:4px;}}
# .detail-section{{margin-bottom:18px;}}
# .detail-section-title{{font-family:var(--mono);font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;display:flex;align-items:center;gap:8px;}}
# .detail-section-title::after{{content:'';flex:1;height:1px;background:var(--border);}}
# .detail-box{{background:var(--card);border:1px solid var(--border2);border-radius:11px;padding:16px;margin-bottom:8px;}}
# .detail-box.threat{{border-color:rgba(220,38,38,0.4);background:rgba(220,38,38,0.04);}}
# .detail-box.safe{{border-color:rgba(13,148,136,0.3);background:rgba(13,148,136,0.04);}}
# .detail-box-label{{font-family:var(--mono);font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;}}
# .detail-box p{{font-size:14px;color:var(--text);line-height:1.8;white-space:pre-wrap;}}
# .detail-box a{{color:var(--accent2);text-decoration:none;font-family:var(--mono);font-size:12px;word-break:break-all;}}
# .detail-actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px;}}
# .detail-approve-btn{{padding:9px 16px;background:rgba(13,148,136,0.15);color:var(--teal);border:1px solid rgba(13,148,136,0.35);border-radius:9px;font-family:var(--sans);font-size:13px;font-weight:700;cursor:pointer;}}
# .detail-whitelist-btn{{padding:9px 16px;background:rgba(124,58,237,0.1);color:#a78bfa;border:1px solid rgba(124,58,237,0.25);border-radius:9px;font-family:var(--sans);font-size:13px;font-weight:700;cursor:pointer;}}
# #toast-container{{position:fixed;top:20px;right:20px;z-index:200;display:flex;flex-direction:column;gap:8px;pointer-events:none;}}
# .toast{{padding:13px 16px;border-radius:10px;font-family:var(--mono);font-size:11px;display:flex;align-items:center;gap:10px;animation:fadeUp 0.3s ease;max-width:360px;pointer-events:all;line-height:1.5;}}
# .toast.threat{{background:#120608;border:1px solid rgba(220,38,38,0.5);color:#f87171;}}
# .toast.ok{{background:#06100d;border:1px solid rgba(13,148,136,0.4);color:var(--teal);}}
# .toast-close{{margin-left:auto;opacity:0.5;cursor:pointer;font-size:14px;flex-shrink:0;}}
# .feed-col{{background:rgba(10,11,19,0.97);display:flex;flex-direction:column;position:sticky;top:0;height:100vh;overflow:hidden;}}
# .feed-header{{padding:18px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-shrink:0;}}
# .feed-title{{font-family:var(--mono);font-size:10px;color:var(--accent2);text-transform:uppercase;letter-spacing:0.12em;display:flex;align-items:center;gap:8px;}}
# .live-dot{{width:6px;height:6px;background:var(--teal);border-radius:50%;animation:pulse 1.5s infinite;}}
# .clear-btn{{font-family:var(--mono);font-size:10px;color:var(--rose);background:transparent;border:1px solid rgba(244,63,94,0.25);border-radius:6px;padding:4px 10px;cursor:pointer;}}
# .feed-list{{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:8px;}}
# .feed-list::-webkit-scrollbar{{width:3px;}}.feed-list::-webkit-scrollbar-thumb{{background:var(--border2);border-radius:2px;}}
# .ncard{{background:var(--card2);border:1px solid var(--border);border-radius:11px;padding:13px;cursor:pointer;transition:border-color 0.2s,transform 0.2s;animation:fadeUp 0.35s ease both;}}
# .ncard:hover{{border-color:rgba(124,58,237,0.35);transform:translateX(-2px);}}
# .ncard.threat{{border-color:rgba(220,38,38,0.4);background:rgba(220,38,38,0.04);}}
# .ncard.verified{{border-color:rgba(13,148,136,0.25);}}
# .ncard.pending{{border-color:rgba(245,158,11,0.4);background:rgba(245,158,11,0.04);}}
# .ncard-top{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:7px;}}
# .ncard-meta{{display:flex;flex-direction:column;gap:2px;}}
# .ncard-time{{font-family:var(--mono);font-size:9px;color:var(--muted);}}
# .ncard-pr-num{{font-family:var(--mono);font-size:9px;color:var(--accent2);}}
# .ndel{{background:transparent;border:none;color:var(--muted);cursor:pointer;font-size:12px;padding:0 2px;line-height:1;flex-shrink:0;}}
# .ndel:hover{{color:var(--rose);}}
# .ncard-title{{font-size:12px;font-weight:700;color:var(--text);margin-bottom:3px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
# .ncard-author{{font-family:var(--mono);font-size:10px;color:var(--muted);margin-bottom:9px;}}
# .ncard-badges{{display:flex;gap:4px;flex-wrap:wrap;margin-bottom:9px;}}
# .nb{{font-family:var(--mono);font-size:8px;padding:2px 6px;border-radius:4px;font-weight:700;}}
# .nb.ok{{background:rgba(13,148,136,0.12);color:var(--teal);border:1px solid rgba(13,148,136,0.2);}}
# .nb.warn{{background:rgba(220,38,38,0.12);color:#f87171;border:1px solid rgba(220,38,38,0.25);}}
# .nb.blue{{background:rgba(14,165,233,0.1);color:var(--accent2);border:1px solid rgba(14,165,233,0.2);}}
# .nb.gray{{background:rgba(74,80,128,0.15);color:var(--muted2);border:1px solid rgba(74,80,128,0.2);}}
# .nb.purple{{background:rgba(124,58,237,0.12);color:#a78bfa;border:1px solid rgba(124,58,237,0.2);}}
# .nb.gold{{background:rgba(245,158,11,0.12);color:var(--gold);border:1px solid rgba(245,158,11,0.2);}}
# .more-btn{{width:100%;padding:6px;background:transparent;border:1px solid rgba(124,58,237,0.2);border-radius:7px;font-family:var(--mono);font-size:9px;color:#a78bfa;cursor:pointer;}}
# .ncard-actions{{display:flex;gap:5px;margin-top:7px;}}
# .approve-btn{{padding:5px 10px;background:rgba(13,148,136,0.15);color:var(--teal);border:1px solid rgba(13,148,136,0.3);border-radius:6px;font-family:var(--mono);font-size:9px;cursor:pointer;font-weight:700;}}
# .whitelist-btn{{padding:5px 10px;background:rgba(124,58,237,0.1);color:#a78bfa;border:1px solid rgba(124,58,237,0.2);border-radius:6px;font-family:var(--mono);font-size:9px;cursor:pointer;font-weight:700;}}
# .empty-feed{{font-family:var(--mono);font-size:10px;color:var(--muted);text-align:center;padding:40px 16px;line-height:2.2;}}
# .team-section{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px 22px;margin-top:24px;position:relative;overflow:hidden;}}
# .team-section::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(14,165,233,0.3),rgba(124,58,237,0.3),transparent);}}
# .team-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin:14px 0;}}
# .team-member{{background:var(--surface);border:1px solid var(--border2);border-radius:11px;padding:10px 14px;display:flex;align-items:center;gap:10px;}}
# .member-avatar{{width:28px;height:28px;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;color:#fff;flex-shrink:0;}}
# .member-full-name{{font-size:13px;font-weight:600;color:var(--text);}}
# .team-footer{{font-family:var(--mono);font-size:11px;color:var(--muted);text-align:center;padding-top:14px;border-top:1px solid var(--border);}}
# @keyframes fadeUp{{from{{opacity:0;transform:translateY(14px);}}to{{opacity:1;transform:translateY(0);}}}}
# @keyframes pulse{{0%,100%{{opacity:1;transform:scale(1);}}50%{{opacity:0.4;transform:scale(0.85);}}}}
# @keyframes spin{{to{{transform:rotate(360deg);}}}}
# @keyframes slideIn{{from{{transform:translateX(40px);opacity:0;}}to{{transform:translateX(0);opacity:1;}}}}
# @media(max-width:960px){{.layout{{grid-template-columns:1fr;}}.feed-col{{position:relative;height:auto;border:none;border-top:1px solid var(--border);}}.feed-list{{max-height:340px;}}}}
# @media(max-width:600px){{.step-boxes{{grid-template-columns:1fr;}}.team-grid{{grid-template-columns:1fr;}}}}
# </style>
# </head>
# <body>

# <div class="sec-modal" id="sec-modal">
#   <div class="sec-panel">
#     <span class="sec-icon">⚠️</span>
#     <div class="sec-title">Unauthorized Contributor</div>
#     <div class="sec-sub" id="sec-modal-msg"></div>
#     <div class="sec-details" id="sec-modal-details"></div>
#     <div class="sec-actions">
#       <button class="sec-dismiss" onclick="dismissAlert()">Dismiss</button>
#       <button class="sec-approve" id="sec-approve-btn">✓ Approve & Generate</button>
#       <button class="sec-whitelist" id="sec-whitelist-btn">+ Whitelist</button>
#       <button class="sec-view" id="sec-view-btn">View Details →</button>
#     </div>
#   </div>
# </div>

# <div id="toast-container"></div>

# <div class="detail-overlay" id="detail-overlay" onclick="closeDetail(event)">
#   <div class="detail-panel">
#     <div class="detail-close"><button onclick="closeDetailBtn()">✕</button></div>
#     <div id="detail-content"></div>
#   </div>
# </div>

# <div class="layout">
#   <div class="main-col">
#     <div class="wrap">
#       <header>
#         <div class="logo">
#           <div class="logo-row">
#             <div class="logo-icon">⚡</div>
#             <div class="logo-text"><span class="nex">Nex</span>Release</div>
#           </div>
#           <div class="logo-subtitle">by Schrodingers</div>
#         </div>
#         <div class="header-right">
#           <div class="user-pill">
#             {'<img src="' + avatar + '" alt=""/>' if avatar else '👤'}
#             {github_name}
#           </div>
#           <div class="status-pill"><div class="pulse-dot"></div>ONLINE</div>
#           <a href="/oauth/logout" class="logout-btn">Logout</a>
#         </div>
#       </header>

#       <div class="hero">
#         <div class="hero-eyebrow">MCP-Powered Automation</div>
#         <h1>Release coordination,<br><span class="grad-purple">fully automated.</span></h1>
#         <p>Merge a PR and the AI agent reads it, files the Jira ticket, pings Slack, and schedules the go/no-go — all in under 10 seconds.</p>
#       </div>

#       <div class="pipeline" id="pipeline">
#         <div class="pipe-step" id="ps0"><div class="pipe-icon">🔀</div><div class="pipe-label">PR Merge</div></div>
#         <div class="pipe-arrow" id="pa0"></div>
#         <div class="pipe-step" id="ps1"><div class="pipe-icon">🧠</div><div class="pipe-label">AI Read</div></div>
#         <div class="pipe-arrow" id="pa1"></div>
#         <div class="pipe-step" id="ps2"><div class="pipe-icon">🎫</div><div class="pipe-label">Jira</div></div>
#         <div class="pipe-arrow" id="pa2"></div>
#         <div class="pipe-step" id="ps3"><div class="pipe-icon">💬</div><div class="pipe-label">Slack</div></div>
#         <div class="pipe-arrow" id="pa3"></div>
#         <div class="pipe-step" id="ps4"><div class="pipe-icon">📅</div><div class="pipe-label">Meeting</div></div>
#       </div>

#       <div class="panel">
#         <div class="panel-title">Trigger Agent Manually</div>
#         <div class="repo-row">
#           <div class="repo-group">
#             <label>GitHub Repository</label>
#             <select id="repo-select" onchange="onRepoChange()">
#               <option value="">— select a repository —</option>
#               {''.join(f'<option value="{r}">{r}</option>' for r in repos)}
#             </select>
#           </div>
#           <div class="field">
#             <label>PR Number</label>
#             <input type="number" id="pr-number" value="" min="1" placeholder="auto" oninput="hideSuggestions()"/>
#           </div>
#           <button class="run-btn" id="run-btn" onclick="runAgent()">
#             <span id="btn-icon">▶</span> Run Agent
#           </button>
#         </div>
#         <div class="pr-suggestions" id="pr-suggestions"></div>
#         <div class="terminal">
#           <div class="terminal-bar">
#             <div class="tdot r"></div><div class="tdot y"></div><div class="tdot g"></div>
#             <span class="terminal-title">release-agent — bash</span>
#           </div>
#           <div class="terminal-body" id="log"><span class="t-muted">$ waiting for trigger...</span></div>
#         </div>
#         <div class="step-boxes" id="step-boxes" style="display:none;">
#           <div class="step-box" id="sb-pr"><div class="step-box-label">📦 PR Info</div><div class="step-box-val" id="sb-pr-val">—</div></div>
#           <div class="step-box" id="sb-security"><div class="step-box-label">🔐 Security</div><div class="step-box-val" id="sb-security-val">—</div></div>
#           <div class="step-box" id="sb-summary"><div class="step-box-label">🧠 AI Summary</div><div class="step-box-val" id="sb-summary-val">—</div></div>
#           <div class="step-box" id="sb-jira"><div class="step-box-label">🎫 Jira Ticket</div><div class="step-box-val" id="sb-jira-val">—</div></div>
#           <div class="step-box" id="sb-slack"><div class="step-box-label">💬 Slack</div><div class="step-box-val" id="sb-slack-val">—</div></div>
#           <div class="step-box" id="sb-meeting"><div class="step-box-label">📅 Meeting</div><div class="step-box-val" id="sb-meeting-val">—</div></div>
#         </div>
#         <div class="hint">🔗 Auto-trigger: point GitHub webhooks to <code>POST /webhook</code></div>
#       </div>

#       <div class="panel">
#         <div class="panel-title">🔐 Team Whitelist</div>
#         <p style="font-size:13px;color:var(--muted2);margin-bottom:18px;line-height:1.6;">Approved contributors. Unauthorized PRs trigger a security alert.</p>
#         <div id="member-list"></div>
#         <div class="add-row">
#           <input type="text" id="new-member" placeholder="github-username"/>
#           <button class="secondary-btn" onclick="addMember()">+ Add</button>
#         </div>
#       </div>

#       <div class="panel">
#         <div class="panel-title">📅 Google Calendar</div>
#         <p style="font-size:13px;color:var(--muted2);margin-bottom:18px;line-height:1.6;">Connect your Google Calendar for automatic meeting scheduling.</p>
#         <div class="cal-status-row">
#           <div id="cal-status" style="font-family:var(--mono);font-size:12px;color:var(--muted);"><span class="spin"></span> Checking...</div>
#           <button class="secondary-btn" id="cal-connect-btn" onclick="connectCalendar()" style="display:none;">Connect Google Calendar</button>
#         </div>
#       </div>

#       <div class="team-section">
#         <div style="font-family:var(--mono);font-size:10px;color:var(--muted2);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:12px;">Project Info</div>
#         <div style="font-size:18px;font-weight:900;letter-spacing:-0.5px;margin-bottom:4px;"><span style="background:linear-gradient(90deg,#a78bfa,#0ea5e9);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Nex</span>Release</div>
#         <div style="font-family:var(--mono);font-size:11px;color:var(--muted2);margin-bottom:14px;">MCP-Based AI Release Coordinator · Gen-AI Hackathon 2026</div>
#         <div class="team-grid">
#           <div class="team-member"><div class="member-avatar" style="background:linear-gradient(135deg,#7c3aed,#6d28d9);">PM</div><div class="member-full-name">Prateek Manocha</div></div>
#           <div class="team-member"><div class="member-avatar" style="background:linear-gradient(135deg,#0ea5e9,#0284c7);">KB</div><div class="member-full-name">Krish Bhandari</div></div>
#           <div class="team-member"><div class="member-avatar" style="background:linear-gradient(135deg,#0d9488,#0f766e);">NB</div><div class="member-full-name">Niraj Basel</div></div>
#           <div class="team-member"><div class="member-avatar" style="background:linear-gradient(135deg,#dc2626,#b91c1c);">DR</div><div class="member-full-name">Dhanush Rajakumar</div></div>
#         </div>
#         <div class="team-footer">Team Schrodingers · Built with Groq AI · GitHub · Jira · Slack</div>
#       </div>
#     </div>
#   </div>

#   <div class="feed-col">
#     <div class="feed-header">
#       <div class="feed-title"><div class="live-dot"></div>{username}'s Feed</div>
#       <button class="clear-btn" onclick="clearAll()">Clear</button>
#     </div>
#     <div class="feed-list" id="feed-list">
#       <div class="empty-feed">No PRs yet.<br><br>Select a repo above<br>and merge a PR.</div>
#     </div>
#   </div>
# </div>

# <script>
# const log = document.getElementById('log');
# let allNotifications = [];
# let lastSeenIds = new Set();

# function showToast(msg, type='ok', duration=6000) {{
#   const tc = document.getElementById('toast-container');
#   const t = document.createElement('div');
#   t.className = 'toast ' + type;
#   t.innerHTML = `<span>${{type==='threat'?'⚠':'✓'}}</span><span style="flex:1">${{msg}}</span><span class="toast-close" onclick="this.parentElement.remove()">✕</span>`;
#   tc.appendChild(t);
#   setTimeout(()=>{{if(t.parentElement)t.remove();}},duration);
# }}

# async function checkCalendarStatus() {{
#   try {{
#     const res = await fetch('/oauth/google/status');
#     const data = await res.json();
#     const status = document.getElementById('cal-status');
#     const btn = document.getElementById('cal-connect-btn');
#     btn.style.display = 'inline-flex';
#     if (data.connected) {{
#       status.innerHTML = '<span style="color:var(--teal);">✓ Google Calendar connected</span>';
#       btn.textContent = 'Reconnect';
#     }} else {{
#       status.innerHTML = '<span style="color:var(--muted);">Not connected — using fallback</span>';
#       btn.textContent = 'Connect Google Calendar';
#     }}
#   }} catch(e) {{
#     document.getElementById('cal-connect-btn').style.display = 'inline-flex';
#   }}
# }}

# async function connectCalendar() {{
#   const res = await fetch('/oauth/google');
#   const data = await res.json();
#   if (data.auth_url) {{
#     const popup = window.open(data.auth_url, '_blank', 'width=500,height=650');
#     showToast('Authorize in the popup window', 'ok', 8000);
#     const check = setInterval(async () => {{
#       if (popup && popup.closed) {{ clearInterval(check); checkCalendarStatus(); }}
#     }}, 1000);
#   }} else {{
#     showToast('Error: ' + (data.error || 'Unknown'), 'threat');
#   }}
# }}

# checkCalendarStatus();

# async function onRepoChange() {{
#   const repo = document.getElementById('repo-select').value;
#   const box = document.getElementById('pr-suggestions');
#   document.getElementById('pr-number').value = '';
#   if (!repo) {{ box.style.display='none'; return; }}
#   box.style.display='block';
#   box.innerHTML='<div class="pr-loading"><span class="spin"></span> Loading merged PRs...</div>';
#   try {{
#     const res = await fetch('/repo-prs?repo='+encodeURIComponent(repo));
#     const data = await res.json();
#     if (!data.prs || data.prs.length===0) {{
#       box.innerHTML='<div class="pr-loading" style="color:var(--muted2)">No merged PRs found.</div>';
#       return;
#     }}
#     box.innerHTML = data.prs.map(p=>
#       `<div class="pr-item" onclick="selectPr(${{p.number}})">
#         <span class="pr-num">#${{p.number}}</span>
#         <span class="pr-title-text">${{p.title}}</span>
#       </div>`
#     ).join('');
#   }} catch(e) {{
#     box.innerHTML='<div class="pr-loading" style="color:var(--rose)">Failed to load PRs.</div>';
#   }}
# }}

# function selectPr(num) {{
#   document.getElementById('pr-number').value = num;
#   document.getElementById('pr-suggestions').style.display='none';
# }}

# function hideSuggestions() {{
#   document.getElementById('pr-suggestions').style.display='none';
# }}

# function showSecurityAlert(n, idx) {{
#   document.getElementById('sec-modal-msg').textContent =
#     `PR #${{n.pr_number}} "${{n.pr_title}}" — @${{n.author}} is not on your whitelist.`;
#   document.getElementById('sec-modal-details').innerHTML =
#     `PR: #${{n.pr_number}}<br>Author: @${{n.author}}<br>Time: ${{n.time}}`;
#   document.getElementById('sec-approve-btn').onclick = async () => {{
#     dismissAlert();
#     showToast('Approving PR...','ok');
#     await fetch('/approve',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{index:idx}})}});
#     loadNotifications();
#   }};
#   document.getElementById('sec-whitelist-btn').onclick = async () => {{
#     await fetch('/whitelist/add',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{username:n.author}})}});
#     loadMembers();
#     showToast(`@${{n.author}} added`,'ok');
#     dismissAlert();
#   }};
#   document.getElementById('sec-view-btn').onclick = ()=>{{dismissAlert();openDetail(idx);}};
#   document.getElementById('sec-modal').classList.add('open');
# }}
# function dismissAlert() {{ document.getElementById('sec-modal').classList.remove('open'); }}

# function openDetail(index) {{
#   const n = allNotifications[index];
#   if(!n)return;
#   const isThreat  = n.security && n.security.status==='unauthorized';
#   const isVerified= n.security && n.security.status==='verified';
#   document.getElementById('detail-content').innerHTML=`
#     <div class="detail-hero">
#       <div class="detail-pr-num">PR #${{n.pr_number}}</div>
#       <div class="detail-title">${{n.pr_title}}</div>
#       <div class="detail-author">by @${{n.author}}</div>
#       <div class="detail-time">${{n.pending?'⏳ Pending':'Processed at '+n.time}}</div>
#     </div>
#     <div class="detail-section"><div class="detail-section-title">🔐 Security</div>
#       <div class="detail-box ${{isThreat?'threat':isVerified?'safe':''}}">
#         <div class="detail-box-label">Status</div>
#         <p>${{n.security?n.security.message:'—'}}</p>
#         ${{n.pending?`<div class="detail-actions">
#           <button class="detail-approve-btn" onclick="approveNotif(${{index}})">✓ Approve & Generate</button>
#           <button class="detail-whitelist-btn" onclick="whitelistAuthor('${{n.author}}')">+ Whitelist</button>
#         </div>`:''}}</div></div>
#     <div class="detail-section"><div class="detail-section-title">🧠 Summary</div>
#       <div class="detail-box"><p>${{n.summary||'—'}}</p></div></div>
#     <div class="detail-section"><div class="detail-section-title">✅ Checklist</div>
#       <div class="detail-box"><p>${{n.checklist||'—'}}</p></div></div>
#     <div class="detail-section"><div class="detail-section-title">⚠️ Risks</div>
#       <div class="detail-box"><p>${{n.risks||'—'}}</p></div></div>
#     <div class="detail-section"><div class="detail-section-title">🎫 Jira</div>
#       <div class="detail-box">
#         ${{n.jira_url?`<a href="${{n.jira_url}}" target="_blank">${{n.jira_url}}</a>`:'<p>—</p>'}}</div></div>
#     <div class="detail-section"><div class="detail-section-title">💬 Slack</div>
#       <div class="detail-box"><p>${{n.slack_message||'—'}}</p>
#         <div style="margin-top:8px">${{n.slack_posted?'<span class="badge ok">✓ Posted</span>':'<span class="badge err">✗ Not posted</span>'}}</div></div></div>
#     <div class="detail-section"><div class="detail-section-title">📅 Meeting</div>
#       <div class="detail-box"><p>${{n.meeting||'—'}}</p></div></div>
#     <div class="detail-section"><div class="detail-section-title">🔗 PR Link</div>
#       <div class="detail-box">
#         ${{n.pr_url?`<a href="${{n.pr_url}}" target="_blank">${{n.pr_url}}</a>`:'<p>—</p>'}}</div></div>`;
#   document.getElementById('detail-overlay').classList.add('open');
# }}

# async function approveNotif(index) {{
#   closeDetailBtn();
#   showToast('Approving...','ok');
#   await fetch('/approve',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{index}})}});
#   loadNotifications();
# }}
# async function whitelistAuthor(author) {{
#   await fetch('/whitelist/add',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{username:author}})}});
#   loadMembers();
#   showToast(`@${{author}} added`,'ok');
# }}
# function closeDetail(e){{if(e.target===document.getElementById('detail-overlay'))closeDetailBtn();}}
# function closeDetailBtn(){{document.getElementById('detail-overlay').classList.remove('open');}}

# async function loadNotifications() {{
#   const res = await fetch('/notifications');
#   const data = await res.json();
#   allNotifications = data.notifications;
#   renderFeed(allNotifications);
#   allNotifications.forEach((n,idx)=>{{
#     const uid=`${{n.pr_number}}-${{n.time}}`;
#     if(!lastSeenIds.has(uid)){{
#       lastSeenIds.add(uid);
#       if(n.security&&n.security.status==='unauthorized'){{
#         showSecurityAlert(n,idx);
#         showToast(`⚠ PR #${{n.pr_number}} by @${{n.author}} not whitelisted`,'threat',10000);
#       }} else if(lastSeenIds.size>1){{
#         showToast(`PR #${{n.pr_number}} processed`,'ok');
#       }}
#     }}
#   }});
# }}

# function renderFeed(notifications) {{
#   const feed = document.getElementById('feed-list');
#   if(notifications.length===0){{
#     feed.innerHTML='<div class="empty-feed">No PRs yet.<br><br>Select a repo above<br>and merge a PR.</div>';return;
#   }}
#   feed.innerHTML=notifications.map((n,i)=>{{
#     const isThreat  = n.security&&n.security.status==='unauthorized';
#     const isVerified= n.security&&n.security.status==='verified';
#     const isPending = n.pending;
#     const cls = isPending?'pending':isThreat?'threat':isVerified?'verified':'';
#     return `<div class="ncard ${{cls}}">
#       <div class="ncard-top">
#         <div class="ncard-meta">
#           <span class="ncard-time">${{n.time}}</span>
#           <span class="ncard-pr-num">PR #${{n.pr_number}}</span>
#         </div>
#         <button class="ndel" onclick="event.stopPropagation();deleteNotif(${{i}})">✕</button>
#       </div>
#       <div class="ncard-title">${{n.pr_title}}</div>
#       <div class="ncard-author">by @${{n.author}}</div>
#       <div class="ncard-badges">
#         <span class="nb blue">PR</span>
#         ${{n.jira_url?'<span class="nb ok">Jira ✓</span>':'<span class="nb gray">Jira —</span>'}}
#         ${{n.slack_posted?'<span class="nb ok">Slack ✓</span>':'<span class="nb gray">Slack —</span>'}}
#         ${{n.meeting?'<span class="nb ok">Meeting ✓</span>':'<span class="nb gray">Meeting —</span>'}}
#         ${{isThreat?`<span class="nb warn">⚠ @${{n.author}}</span>`:''}}
#         ${{isVerified?'<span class="nb purple">✓ Auth</span>':''}}
#         ${{isPending?'<span class="nb gold">⏳ Pending</span>':''}}
#       </div>
#       <button class="more-btn" onclick="openDetail(${{i}})">More Info →</button>
#       ${{isPending?`<div class="ncard-actions">
#         <button class="approve-btn" onclick="event.stopPropagation();approveNotif(${{i}})">✓ Approve</button>
#         <button class="whitelist-btn" onclick="event.stopPropagation();whitelistAuthor('${{n.author}}')">+ Whitelist</button>
#       </div>`:''}}</div>`;
#   }}).join('');
# }}

# async function deleteNotif(i){{
#   await fetch('/notifications/delete',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{index:i}})}});
#   loadNotifications();
# }}
# async function clearAll(){{
#   await fetch('/notifications/clear',{{method:'POST'}});
#   lastSeenIds.clear();loadNotifications();
# }}
# (async()=>{{
#   const res=await fetch('/notifications');
#   const data=await res.json();
#   allNotifications=data.notifications;
#   allNotifications.forEach(n=>lastSeenIds.add(`${{n.pr_number}}-${{n.time}}`));
#   renderFeed(allNotifications);
# }})();
# setInterval(loadNotifications,5000);

# async function loadMembers(){{
#   const res=await fetch('/whitelist');
#   const data=await res.json();
#   renderMembers(data.members);
# }}
# function renderMembers(members){{
#   const list=document.getElementById('member-list');
#   if(members.length===0){{list.innerHTML='<p style="font-family:var(--mono);font-size:12px;color:var(--muted);margin-bottom:8px;">No members yet.</p>';return;}}
#   list.innerHTML=members.map((m,i)=>`
#     <div class="member-row">
#       <span class="member-name">@${{m}}</span>
#       <button class="danger-btn" onclick="removeMember(${{i}})">Remove</button>
#     </div>`).join('');
# }}
# async function addMember(){{
#   const input=document.getElementById('new-member');
#   const name=input.value.trim();
#   if(!name)return;
#   await fetch('/whitelist/add',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{username:name}})}});
#   input.value='';loadMembers();
# }}
# async function removeMember(index){{
#   await fetch('/whitelist/remove',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{index}})}});
#   loadMembers();
# }}
# loadMembers();

# function addLine(html){{log.innerHTML+='<br>'+html;log.scrollTop=log.scrollHeight;}}
# function setStep(idx){{
#   for(let i=0;i<5;i++){{
#     const s=document.getElementById('ps'+i);
#     s.classList.remove('active','done');
#     if(i<idx)s.classList.add('done');
#     if(i===idx)s.classList.add('active');
#     if(i<4)document.getElementById('pa'+i).classList.toggle('lit',i<idx);
#   }}
# }}
# function setBox(id,val,done){{
#   const box=document.getElementById('sb-'+id);
#   const valEl=document.getElementById('sb-'+id+'-val');
#   if(box)box.classList.toggle('done',done);
#   if(valEl)valEl.innerHTML=val;
# }}
# function sleep(ms){{return new Promise(r=>setTimeout(r,ms));}}

# async function runAgent(){{
#   const repo=document.getElementById('repo-select').value;
#   const pr=document.getElementById('pr-number').value;
#   const btn=document.getElementById('run-btn');
#   if(!repo){{showToast('Select a repository first','threat');return;}}
#   if(!pr){{showToast('Select or enter a PR number','threat');return;}}
#   btn.disabled=true;
#   document.getElementById('btn-icon').innerHTML='<span class="spin"></span>';
#   document.getElementById('step-boxes').style.display='none';
#   document.getElementById('pr-suggestions').style.display='none';
#   log.innerHTML='<span class="t-muted">$ release-agent run --repo '+repo+' --pr '+pr+'</span>';
#   setStep(-1);await sleep(300);
#   addLine('<span class="t-purple">⟳  initializing agent...</span>');
#   await sleep(500);setStep(0);
#   addLine('<span class="t-white">[ 1/5 ]</span> <span class="t-muted">reading PR from GitHub...</span>');
#   try{{
#     const res=await fetch('/run?repo='+encodeURIComponent(repo)+'&pr='+pr);
#     const data=await res.json();
#     if(data.error){{addLine('<span class="t-red">✗  error: '+data.error+'</span>');btn.disabled=false;document.getElementById('btn-icon').textContent='▶';return;}}
#     await sleep(400);setStep(1);
#     addLine('<span class="t-teal">✓</span>  <span class="t-white">PR read:</span> <span class="t-blue">'+data.pr_title+'</span>');
#     if(data.security){{
#       const sc=data.security;
#       if(sc.status==='unauthorized'){{
#         addLine('<span class="t-red">⚠  SECURITY: '+sc.message+'</span>');
#         addLine('<span class="t-warn">⏳ Paused — approve in feed →</span>');
#         document.getElementById('step-boxes').style.display='grid';
#         setBox('pr',`<strong>${{data.pr_title}}</strong>`,true);
#         setBox('security',sc.message,false);
#         setBox('summary',data.summary||'—',true);
#         setBox('jira','⏳ Pending',false);setBox('slack','⏳ Pending',false);setBox('meeting','⏳ Pending',false);
#         loadNotifications();btn.disabled=false;document.getElementById('btn-icon').textContent='▶';return;
#       }} else if(sc.status==='verified'){{addLine('<span class="t-teal">🔐 '+sc.message+'</span>');}}
#     }}
#     await sleep(400);addLine('<span class="t-white">[ 2/5 ]</span> <span class="t-muted">summarizing with Groq AI...</span>');
#     await sleep(500);setStep(2);addLine('<span class="t-teal">✓</span>  summary generated');
#     await sleep(300);addLine('<span class="t-white">[ 3/5 ]</span> <span class="t-muted">creating Jira ticket...</span>');
#     await sleep(400);setStep(3);addLine('<span class="t-teal">✓</span>  ticket → <span class="t-blue">'+(data.jira_url||'N/A')+'</span>');
#     await sleep(300);addLine('<span class="t-white">[ 4/5 ]</span> <span class="t-muted">posting to Slack...</span>');
#     await sleep(400);setStep(4);addLine('<span class="t-teal">✓</span>  Slack posted');
#     await sleep(300);addLine('<span class="t-white">[ 5/5 ]</span> <span class="t-muted">scheduling meeting...</span>');
#     await sleep(400);addLine('<span class="t-teal">✓</span>  meeting → <span class="t-blue">'+(data.meeting||'N/A')+'</span>');
#     await sleep(300);addLine('');
#     addLine('<span class="t-purple">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>');
#     addLine('<span class="t-teal">  AGENT COMPLETE  </span>');
#     addLine('<span class="t-purple">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>');
#     document.getElementById('step-boxes').style.display='grid';
#     const sc=data.security||{{}};
#     setBox('pr',`<strong>${{data.pr_title}}</strong><br><span style="color:var(--muted2);font-size:11px;">by @${{data.author||'—'}}</span>`,true);
#     setBox('security',sc.message||'—',sc.status==='verified');
#     setBox('summary',data.summary||'—',true);
#     setBox('jira',data.jira_url?`<a href="${{data.jira_url}}" target="_blank">${{data.jira_url}}</a>`:'—',!!data.jira_url);
#     setBox('slack',data.slack_posted?'<span class="badge ok">✓ Posted</span>':'<span class="badge err">✗ Failed</span>',data.slack_posted);
#     setBox('meeting',data.meeting||'—',!!data.meeting);
#     loadNotifications();
#   }}catch(err){{addLine('<span class="t-red">✗  error: '+err+'</span>');}}
#   btn.disabled=false;document.getElementById('btn-icon').textContent='▶';
# }}
# </script>
# </body>
# </html>"""

# # ── API routes ─────────────────────────────────────────────────────────────────
# def current_user():
#     return session.get("github_username", "anonymous")

# @app.route("/repo-prs")
# def repo_prs():
#     repo         = request.args.get("repo", "")
#     access_token = session.get("github_token", "")
#     if not repo or not access_token:
#         return jsonify({"prs": []})
#     return jsonify({"prs": get_repo_prs_list(access_token, repo)})

# @app.route("/notifications")
# def get_notifications():
#     return jsonify({"notifications": load_notifications(current_user())})

# @app.route("/notifications/delete", methods=["POST"])
# def delete_notification():
#     data     = request.get_json()
#     index    = data.get("index")
#     username = current_user()
#     notifications = load_notifications(username)
#     if index is not None and 0 <= index < len(notifications):
#         notifications.pop(index)
#         save_notifications(username, notifications)
#     return jsonify({"notifications": notifications})

# @app.route("/notifications/clear", methods=["POST"])
# def clear_notifications():
#     username = current_user()
#     save_notifications(username, [])
#     return jsonify({"notifications": []})

# @app.route("/whitelist")
# def get_whitelist():
#     return jsonify({"members": load_whitelist()})

# @app.route("/whitelist/add", methods=["POST"])
# def add_to_whitelist():
#     data     = request.get_json()
#     username = data.get("username", "").strip()
#     if not username:
#         return jsonify({"error": "empty"})
#     members = load_whitelist()
#     if username.lower() not in [m.lower() for m in members]:
#         members.append(username)
#         save_whitelist(members)
#     return jsonify({"members": members})

# @app.route("/whitelist/remove", methods=["POST"])
# def remove_from_whitelist():
#     data  = request.get_json()
#     index = data.get("index")
#     members = load_whitelist()
#     if index is not None and 0 <= index < len(members):
#         members.pop(index)
#         save_whitelist(members)
#     return jsonify({"members": members})

# @app.route("/approve", methods=["POST"])
# def approve():
#     data     = request.get_json()
#     index    = data.get("index")
#     username = current_user()
#     jira_creds  = get_user_jira(username)
#     slack_creds = get_user_slack(username)
#     notifications = load_notifications(username)
#     if index is None or index >= len(notifications):
#         return jsonify({"error": "invalid index"})
#     n = notifications[index]
#     try:
#         repo      = n.get("pr_url", "").split("github.com/")[-1].split("/pull/")[0]
#         pr_number = n.get("pr_number", 1)
#         pr_data   = get_pr_info(repo, pr_number)
#         summary   = summarize_pr(pr_data)
#         ticket    = create_jira_ticket(
#             title=summary["jira_title"], description=summary["summary"],
#             checklist=summary["checklist"], risks=summary["risks"],
#             pr_id=pr_number, **jira_creds
#         )
#         slack_msg = f"""*PR Approved* — `{pr_data['title']}`
# *Author:* {pr_data['author']}
# {summary['slack_message']}
# *Jira:* {ticket.get('url', 'N/A')}
# *PR:* {pr_data['pr_url']}
# ⚠️ Author was not whitelisted but manually approved.""".strip()
#         slack_result = post_slack_message(
#             slack_msg,
#             slack_token=slack_creds["slack_token"],
#             channel=slack_creds["slack_channel"]
#         )
#         meeting = create_calendar_event(
#             meeting_title=summary["meeting_title"],
#             pr_url=pr_data["pr_url"], risks=summary["risks"]
#         )
#         notifications[index].update({
#             "jira_url": ticket.get("url", ""), "slack_posted": slack_result["success"],
#             "meeting": meeting["time"], "slack_message": slack_msg,
#             "summary": summary["summary"], "checklist": summary["checklist"],
#             "risks": summary["risks"], "pending": False
#         })
#         save_notifications(username, notifications)
#         return jsonify({"status": "approved"})
#     except Exception as e:
#         return jsonify({"error": str(e)})

# @app.route("/run")
# def run():
#     pr_number = request.args.get("pr", 1, type=int)
#     repo      = request.args.get("repo", "")
#     username  = current_user()
#     jira_creds  = get_user_jira(username)
#     slack_creds = get_user_slack(username)

#     if not repo:
#         return jsonify({"error": "No repository selected"})

#     ensure_owner_whitelisted(repo)
#     members = load_whitelist()
#     if username.lower() not in [m.lower() for m in members]:
#         members.append(username)
#         save_whitelist(members)

#     try:
#         pr_data  = get_pr_info(repo, pr_number)
#         security = check_contributor(pr_data["author"])

#         if security["status"] == "unauthorized":
#             add_notification(
#                 username=username, pr_number=pr_number,
#                 pr_title=pr_data["title"], author=pr_data["author"],
#                 jira_url="", slack_posted=False, meeting="",
#                 security=security, pr_url=pr_data["pr_url"],
#                 summary="⚠️ Security alert — awaiting approval.",
#                 checklist="", risks="Unauthorized contributor.",
#                 slack_message="", pending=True
#             )
#             return jsonify({
#                 "pr_title": pr_data["title"], "author": pr_data["author"],
#                 "summary": "⚠️ Security alert — awaiting approval.",
#                 "jira_url": "", "slack_posted": False, "meeting": "",
#                 "pr_url": pr_data["pr_url"], "security": security
#             })

#         summary = summarize_pr(pr_data)
#         ticket  = create_jira_ticket(
#             title=summary["jira_title"], description=summary["summary"],
#             checklist=summary["checklist"], risks=summary["risks"],
#             pr_id=pr_number, **jira_creds
#         )
#         slack_msg = f"""*New Release* — `{pr_data['title']}`
# *Author:* {pr_data['author']}
# *CI Status:* {pr_data['ci_status']}
# {summary['slack_message']}
# *Jira:* {ticket.get('url', 'N/A')}
# *PR:* {pr_data['pr_url']}""".strip()

#         slack_result = post_slack_message(
#             slack_msg,
#             slack_token=slack_creds["slack_token"],
#             channel=slack_creds["slack_channel"]
#         )
#         meeting = create_calendar_event(
#             meeting_title=summary["meeting_title"],
#             pr_url=pr_data["pr_url"], risks=summary["risks"]
#         )
#         add_notification(
#             username=username, pr_number=pr_number,
#             pr_title=pr_data["title"], author=pr_data["author"],
#             jira_url=ticket.get("url", ""), slack_posted=slack_result["success"],
#             meeting=meeting["time"], security=security,
#             pr_url=pr_data["pr_url"], summary=summary["summary"],
#             checklist=summary["checklist"], risks=summary["risks"],
#             slack_message=slack_msg, pending=False
#         )
#         return jsonify({
#             "pr_title": pr_data["title"], "author": pr_data["author"],
#             "summary": summary["summary"], "jira_url": ticket.get("url", ""),
#             "slack_posted": slack_result["success"], "meeting": meeting["time"],
#             "pr_url": pr_data["pr_url"], "security": security
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)})

# @app.route("/webhook", methods=["POST"])
# def webhook():
#     data      = request.get_json()
#     action    = data.get("action")
#     pr        = data.get("pull_request", {})
#     is_merged = pr.get("merged", False)
#     repo      = data.get("repository", {}).get("full_name", "")
#     owner     = repo.split("/")[0] if "/" in repo else "unknown"
#     ensure_owner_whitelisted(repo)

#     jira_creds  = get_user_jira(owner)
#     slack_creds = get_user_slack(owner)

#     if action in ["opened", "reopened"]:
#         pr_number = pr["number"]
#         try:
#             pr_data  = get_pr_info(repo, pr_number)
#             security = check_contributor(pr_data["author"])
#             if security["status"] == "unauthorized":
#                 add_notification(
#                     username=owner, pr_number=pr_number,
#                     pr_title=pr_data["title"], author=pr_data["author"],
#                     jira_url="", slack_posted=False, meeting="",
#                     security=security, pr_url=pr_data["pr_url"],
#                     summary="⚠️ Unauthorized contributor opened a PR.",
#                     checklist="", risks="Review before merging.",
#                     slack_message="", pending=True
#                 )
#             return jsonify({"status": "security checked", "pr": pr_number})
#         except Exception as e:
#             return jsonify({"status": "error", "message": str(e)})

#     if action == "closed" and is_merged:
#         pr_number = pr["number"]
#         try:
#             pr_data  = get_pr_info(repo, pr_number)
#             security = check_contributor(pr_data["author"])
#             if security["status"] == "unauthorized":
#                 add_notification(
#                     username=owner, pr_number=pr_number,
#                     pr_title=pr_data["title"], author=pr_data["author"],
#                     jira_url="", slack_posted=False, meeting="",
#                     security=security, pr_url=pr_data["pr_url"],
#                     summary="⚠️ Merged by unauthorized contributor.",
#                     checklist="", risks="Review immediately.",
#                     slack_message="", pending=True
#                 )
#                 return jsonify({"status": "security alert"})

#             summary = summarize_pr(pr_data)
#             ticket  = create_jira_ticket(
#                 title=summary["jira_title"], description=summary["summary"],
#                 checklist=summary["checklist"], risks=summary["risks"],
#                 pr_id=pr_number, **jira_creds
#             )
#             slack_msg = f"""*PR Auto-processed* — `{pr_data['title']}`
# *Author:* {pr_data['author']}
# {summary['slack_message']}
# *Jira:* {ticket.get('url', 'N/A')}""".strip()
#             post_slack_message(
#                 slack_msg,
#                 slack_token=slack_creds["slack_token"],
#                 channel=slack_creds["slack_channel"]
#             )
#             meeting = create_calendar_event(
#                 meeting_title=summary["meeting_title"],
#                 pr_url=pr_data["pr_url"], risks=summary["risks"]
#             )
#             add_notification(
#                 username=owner, pr_number=pr_number,
#                 pr_title=pr_data["title"], author=pr_data["author"],
#                 jira_url=ticket.get("url", ""), slack_posted=True,
#                 meeting=meeting["time"], security=security,
#                 pr_url=pr_data["pr_url"], summary=summary["summary"],
#                 checklist=summary["checklist"], risks=summary["risks"],
#                 slack_message=slack_msg, pending=False
#             )
#             return jsonify({"status": "agent triggered", "pr": pr_number})
#         except Exception as e:
#             return jsonify({"status": "error", "message": str(e)})

#     return jsonify({"status": "ignored"})


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))










#from flask import Flask, jsonify, request, redirect, session
from github_tool import get_pr_info
from claude_brain import summarize_pr, check_contributor, load_whitelist, save_whitelist
from jira_tool import create_jira_ticket
from slack_tool import post_slack_message
from calendar_tool import create_calendar_event, save_token
import json, os, requests as req
from datetime import datetime


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "nexrelease-secret-2026")

GITHUB_CLIENT_ID     = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_OAUTH_URL     = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL     = "https://github.com/login/oauth/access_token"
GITHUB_API_URL       = "https://api.github.com/user"
GITHUB_EMAILS_URL    = "https://api.github.com/user/emails"

NOTIFICATIONS_DIR = "user_notifications"
os.makedirs(NOTIFICATIONS_DIR, exist_ok=True)

def notif_file(username):
    return os.path.join(NOTIFICATIONS_DIR, f"{username.lower()}.json")

def load_notifications(username):
    f = notif_file(username)
    if not os.path.exists(f):
        return []
    with open(f) as fp:
        return json.load(fp)

def save_notifications(username, notifications):
    with open(notif_file(username), "w") as fp:
        json.dump(notifications, fp)

def add_notification(username, pr_number, pr_title, author, jira_url,
                     slack_posted, meeting, security, pr_url,
                     summary, checklist, risks, slack_message, pending=False):
    notifications = load_notifications(username)
    notifications.insert(0, {
        "id": len(notifications),
        "time": datetime.now().strftime("%H:%M"),
        "pr_number": pr_number, "pr_title": pr_title, "author": author,
        "jira_url": jira_url, "slack_posted": slack_posted, "meeting": meeting,
        "security": security, "pr_url": pr_url, "summary": summary,
        "checklist": checklist, "risks": risks, "slack_message": slack_message,
        "pending": pending
    })
    save_notifications(username, notifications)

PROFILES_FILE = "user_profiles.json"

def load_profiles():
    if not os.path.exists(PROFILES_FILE):
        return {}
    with open(PROFILES_FILE) as f:
        return json.load(f)

def save_profiles(profiles):
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f)

def get_profile(username):
    return load_profiles().get(username.lower(), {})

def save_profile(username, data):
    profiles = load_profiles()
    profiles[username.lower()] = data
    save_profiles(profiles)

def get_user_jira(username):
    profile = get_profile(username)
    return {
        "jira_domain":      profile.get("jira_domain", ""),
        "jira_email":       profile.get("jira_email", ""),
        "jira_api_token":   profile.get("jira_api_token", ""),
        "jira_project_key": profile.get("jira_project_key", "KAN"),
    }

def get_user_slack(username):
    profile = get_profile(username)
    return {
        "slack_token":   profile.get("slack_token", ""),
        "slack_channel": profile.get("slack_channel", "releases"),
    }

def ensure_owner_whitelisted(repo):
    if not repo or "/" not in repo:
        return
    owner = repo.split("/")[0]
    members = load_whitelist()
    if owner.lower() not in [m.lower() for m in members]:
        members.append(owner)
        save_whitelist(members)

def get_users_for_repo(repo):
    """Find ALL users who have this repo configured."""
    profiles = load_profiles()
    users = []
    for username, profile in profiles.items():
        if profile.get("repo", "").lower() == repo.lower():
            users.append(username)
    owner = repo.split("/")[0].lower() if "/" in repo else ""
    if owner and owner not in [u.lower() for u in users]:
        users.append(owner)
    return users if users else [owner]

def get_best_token_for_repo(repo):
    """Get the best available GitHub token for a repo."""
    owner = repo.split("/")[0] if "/" in repo else ""
    if owner:
        token = get_profile(owner).get("github_token", "")
        if token:
            return token
    profiles = load_profiles()
    for username, profile in profiles.items():
        if profile.get("github_token"):
            return profile["github_token"]
    return os.getenv("GITHUB_TOKEN", "")

def get_github_user(access_token):
    resp = req.get(GITHUB_API_URL, headers={
        "Authorization": f"token {access_token}", "Accept": "application/json"
    })
    return resp.json() if resp.status_code == 200 else None

def get_github_email(access_token):
    resp = req.get(GITHUB_EMAILS_URL, headers={
        "Authorization": f"token {access_token}", "Accept": "application/json"
    })
    if resp.status_code == 200:
        for e in resp.json():
            if e.get("primary") and e.get("verified"):
                return e.get("email", "")
        for e in resp.json():
            if e.get("verified"):
                return e.get("email", "")
    return ""

def get_github_repos(access_token):
    resp = req.get(
        "https://api.github.com/user/repos?per_page=100&sort=updated&type=all",
        headers={"Authorization": f"token {access_token}", "Accept": "application/json"}
    )
    return [r["full_name"] for r in resp.json()] if resp.status_code == 200 else []

def get_repo_prs_list(access_token, repo):
    resp = req.get(
        f"https://api.github.com/repos/{repo}/pulls?state=closed&per_page=20",
        headers={"Authorization": f"token {access_token}", "Accept": "application/json"}
    )
    if resp.status_code == 200:
        return [{"number": p["number"], "title": p["title"]}
                for p in resp.json() if p.get("merged_at")]
    return []

# ── GitHub OAuth ───────────────────────────────────────────────────────────────
@app.route("/oauth/login")
def oauth_login():
    if not GITHUB_CLIENT_ID:
        return redirect("/?error=no_oauth_config")
    return redirect(f"{GITHUB_OAUTH_URL}?client_id={GITHUB_CLIENT_ID}&scope=read:user user:email repo")

@app.route("/oauth/callback")
def oauth_callback():
    code = request.args.get("code")
    if not code:
        return redirect("/?error=oauth_cancelled")
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        return redirect("/?error=no_oauth_config")

    resp = req.post(GITHUB_TOKEN_URL, json={
        "client_id": GITHUB_CLIENT_ID, "client_secret": GITHUB_CLIENT_SECRET, "code": code
    }, headers={"Accept": "application/json"})
    access_token = resp.json().get("access_token", "")
    if not access_token:
        return redirect("/?error=oauth_failed")

    github_user = get_github_user(access_token)
    if not github_user:
        return redirect("/?error=user_fetch_failed")

    github_email = get_github_email(access_token) or github_user.get("email") or f"{github_user['login']}@github.local"

    session["github_username"] = github_user["login"]
    session["github_email"]    = github_email
    session["github_token"]    = access_token
    session["github_avatar"]   = github_user.get("avatar_url", "")
    session["github_name"]     = github_user.get("name") or github_user["login"]

    members = load_whitelist()
    if github_user["login"].lower() not in [m.lower() for m in members]:
        members.append(github_user["login"])
        save_whitelist(members)

    # ── Save github_token to profile so webhook + approve can use it ──
    profile = get_profile(github_user["login"])
    profile["github_token"] = access_token
    save_profile(github_user["login"], profile)

    if profile.get("jira_api_token") and profile.get("slack_token"):
        return redirect("/app")
    return redirect("/setup")

@app.route("/oauth/logout")
def oauth_logout():
    session.clear()
    return redirect("/")

# ── Google Calendar OAuth ──────────────────────────────────────────────────────
@app.route("/oauth/google")
def google_oauth():
    try:
        from google_auth_oauthlib.flow import Flow
        if not os.path.exists("credentials.json"):
            return jsonify({"error": "credentials.json not found."})
        flow = Flow.from_client_secrets_file(
            "credentials.json",
            scopes=["https://www.googleapis.com/auth/calendar"],
            redirect_uri="http://localhost:5000/oauth/google/callback"
        )
        auth_url, state = flow.authorization_url(access_type="offline", prompt="consent")
        with open("oauth_state.txt", "w") as f:
            f.write(state)
        return jsonify({"auth_url": auth_url})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/oauth/google/callback")
def google_oauth_callback():
    try:
        from google_auth_oauthlib.flow import Flow
        state = open("oauth_state.txt").read() if os.path.exists("oauth_state.txt") else None
        flow = Flow.from_client_secrets_file(
            "credentials.json",
            scopes=["https://www.googleapis.com/auth/calendar"],
            state=state,
            redirect_uri="http://localhost:5000/oauth/google/callback"
        )
        flow.fetch_token(authorization_response=request.url)
        save_token(flow.credentials)
        return "<html><body style='background:#07080f;color:#0d9488;font-family:monospace;display:flex;align-items:center;justify-content:center;height:100vh;'><div style='text-align:center'><div style='font-size:48px'>✅</div><div style='font-size:20px;margin-top:16px'>Google Calendar Connected!</div><script>setTimeout(()=>window.close(),2000)</script></div></body></html>"
    except Exception as e:
        return f"<html><body style='background:#07080f;color:#f43f5e;font-family:monospace;display:flex;align-items:center;justify-content:center;height:100vh;'><div>❌ {str(e)}</div></body></html>"

@app.route("/oauth/google/status")
def google_oauth_status():
    return jsonify({"connected": os.path.exists("token.pickle")})

# ── Landing ────────────────────────────────────────────────────────────────────
@app.route("/")
def landing():
    if session.get("github_username"):
        return redirect("/app")

    error = request.args.get("error", "")
    error_messages = {
        "oauth_failed":      "GitHub authentication failed. Please try again.",
        "oauth_cancelled":   "Login was cancelled. Please try again.",
        "user_fetch_failed": "Could not retrieve your GitHub profile. Please try again.",
        "no_oauth_config":   "OAuth is not configured on this server.",
    }
    error_text = error_messages.get(error, "")
    has_oauth  = bool(GITHUB_CLIENT_ID)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>NexRelease — Sign In</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Outfit:wght@400;600;700;800;900&display=swap" rel="stylesheet"/>
<style>
:root{{--bg:#07080f;--card:#121526;--border2:#252844;--accent:#7c3aed;--accent2:#0ea5e9;--teal:#0d9488;--rose:#f43f5e;--text:#e2e4f0;--muted:#4a5080;--muted2:#6b7199;--mono:'DM Mono',monospace;--sans:'Outfit',sans-serif;}}
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:var(--sans);background:var(--bg);color:var(--text);min-height:100vh;display:flex;align-items:center;justify-content:center;}}
body::before{{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 600px 400px at 20% 30%,rgba(124,58,237,0.08) 0%,transparent 70%),radial-gradient(ellipse 500px 300px at 80% 70%,rgba(14,165,233,0.06) 0%,transparent 70%);pointer-events:none;}}
body::after{{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(124,58,237,0.025) 1px,transparent 1px),linear-gradient(90deg,rgba(124,58,237,0.025) 1px,transparent 1px);background-size:48px 48px;pointer-events:none;}}
.card{{background:var(--card);border:1px solid var(--border2);border-radius:24px;padding:52px 48px;max-width:460px;width:92%;text-align:center;position:relative;overflow:hidden;animation:fadeUp 0.5s ease both;}}
.card::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(124,58,237,0.6),rgba(14,165,233,0.6),transparent);}}
.logo{{display:flex;align-items:center;justify-content:center;gap:14px;margin-bottom:8px;}}
.logo-icon{{width:52px;height:52px;border-radius:14px;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;font-size:26px;box-shadow:0 0 32px rgba(124,58,237,0.45);}}
.logo-text{{font-size:28px;font-weight:900;letter-spacing:-1px;}}
.logo-text .nex{{color:transparent;background:linear-gradient(90deg,#a78bfa,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.by-line{{font-family:var(--mono);font-size:11px;color:var(--muted2);margin-bottom:32px;}}
h2{{font-size:22px;font-weight:800;margin-bottom:10px;}}
.sub{{font-size:14px;color:var(--muted2);line-height:1.7;margin-bottom:28px;}}
.features{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:32px;text-align:left;}}
.feat{{background:rgba(124,58,237,0.06);border:1px solid rgba(124,58,237,0.15);border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:10px;color:var(--muted2);}}
.feat strong{{color:#a78bfa;display:block;margin-bottom:3px;}}
.oauth-btn{{display:flex;align-items:center;justify-content:center;gap:12px;width:100%;padding:15px;background:linear-gradient(135deg,#1a1a2e,#16213e);color:var(--text);border:1px solid rgba(255,255,255,0.12);border-radius:12px;font-family:var(--sans);font-size:15px;font-weight:700;cursor:pointer;text-decoration:none;transition:transform 0.15s,box-shadow 0.2s;margin-bottom:16px;}}
.oauth-btn:hover{{transform:translateY(-2px);box-shadow:0 8px 28px rgba(0,0,0,0.4);}}
.github-icon{{width:22px;height:22px;fill:var(--text);flex-shrink:0;}}
.error-box{{background:rgba(244,63,94,0.08);border:1px solid rgba(244,63,94,0.25);border-radius:8px;padding:12px 14px;font-family:var(--mono);font-size:11px;color:#f87171;margin-bottom:20px;text-align:left;display:{"block" if error_text else "none"};}}
.security-note{{font-family:var(--mono);font-size:10px;color:var(--muted);margin-top:18px;line-height:2;padding-top:18px;border-top:1px solid var(--border2);}}
.security-note .ok{{color:var(--teal);}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(16px);}}to{{opacity:1;transform:translateY(0);}}}}
</style>
</head>
<body>
<div class="card">
  <div class="logo">
    <div class="logo-icon">⚡</div>
    <div class="logo-text"><span class="nex">Nex</span>Release</div>
  </div>
  <div class="by-line">by Schrodingers</div>
  <h2>AI Release Coordinator</h2>
  <div class="sub">Automate PR coordination with Jira, Slack and go/no-go meetings — powered by MCP agents.</div>
  <div class="features">
    <div class="feat"><strong>🔀 PR Agent</strong>Reads & summarizes every PR</div>
    <div class="feat"><strong>🎫 Jira</strong>Auto-creates tickets</div>
    <div class="feat"><strong>💬 Slack</strong>Posts release notes</div>
    <div class="feat"><strong>🔐 Security</strong>Detects unauthorized contributors</div>
  </div>
  {'<div class="error-box">⚠ ' + error_text + '</div>' if error_text else ''}
  {'<a href="/oauth/login" class="oauth-btn"><svg class="github-icon" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>Continue with GitHub</a>' if has_oauth else '<div style="background:rgba(74,80,128,0.1);border:1px solid rgba(74,80,128,0.2);border-radius:10px;padding:16px;font-family:var(--mono);font-size:11px;color:var(--muted2);">⚠️ GitHub OAuth not configured.</div>'}
  <div class="security-note"><span class="ok">🔒 Secure authentication only.</span><br>Login requires a verified GitHub account.<br>We never see or store your GitHub password.</div>
</div>
</body>
</html>"""

# ── Setup ──────────────────────────────────────────────────────────────────────
@app.route("/setup", methods=["GET", "POST"])
def setup():
    username = session.get("github_username")
    if not username:
        return redirect("/")

    if request.method == "POST":
        jira_domain      = request.form.get("jira_domain", "").strip().replace("https://", "").replace("http://", "")
        jira_email       = request.form.get("jira_email", "").strip()
        jira_api_token   = request.form.get("jira_api_token", "").strip()
        jira_project_key = request.form.get("jira_project_key", "KAN").strip() or "KAN"
        slack_token      = request.form.get("slack_token", "").strip()
        slack_channel    = request.form.get("slack_channel", "releases").strip() or "releases"

        if not jira_domain or not jira_email or not jira_api_token or not slack_token:
            return redirect("/setup?error=missing")

        # ── Preserve github_token when saving setup profile ──
        existing = get_profile(username)
        save_profile(username, {
            **existing,
            "jira":              jira_email,
            "jira_domain":       jira_domain,
            "jira_email":        jira_email,
            "jira_api_token":    jira_api_token,
            "jira_project_key":  jira_project_key,
            "slack":             slack_token,
            "slack_token":       slack_token,
            "slack_channel":     slack_channel,
        })
        return redirect("/app")

    error        = request.args.get("error", "")
    github_email = session.get("github_email", "")
    github_name  = session.get("github_name", username)
    avatar       = session.get("github_avatar", "")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>NexRelease — Connect Tools</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Outfit:wght@400;600;700;800;900&display=swap" rel="stylesheet"/>
<style>
:root{{--bg:#07080f;--card:#121526;--surface:#0d0f1a;--border2:#252844;--accent:#7c3aed;--accent2:#0ea5e9;--teal:#0d9488;--rose:#f43f5e;--text:#e2e4f0;--muted:#4a5080;--muted2:#6b7199;--mono:'DM Mono',monospace;--sans:'Outfit',sans-serif;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:var(--sans);background:var(--bg);color:var(--text);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px;}}
.card{{background:var(--card);border:1px solid var(--border2);border-radius:24px;padding:44px 40px;max-width:540px;width:100%;position:relative;overflow:hidden;animation:fadeUp 0.4s ease both;}}
.card::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(124,58,237,0.5),rgba(14,165,233,0.5),transparent);}}
.user-bar{{display:flex;align-items:center;gap:12px;background:rgba(124,58,237,0.06);border:1px solid rgba(124,58,237,0.15);border-radius:10px;padding:12px 16px;margin-bottom:28px;}}
.avatar{{width:38px;height:38px;border-radius:50%;border:2px solid rgba(124,58,237,0.3);}}
.avatar-fallback{{width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;color:#fff;flex-shrink:0;}}
.user-info{{flex:1;}}
.user-name{{font-size:14px;font-weight:700;}}
.user-email{{font-family:var(--mono);font-size:11px;color:var(--teal);}}
h2{{font-size:22px;font-weight:800;margin-bottom:8px;}}
.sub{{font-size:13px;color:var(--muted2);line-height:1.6;margin-bottom:24px;}}
.section-label{{font-family:var(--mono);font-size:10px;color:var(--muted2);text-transform:uppercase;letter-spacing:0.1em;margin:20px 0 10px;display:flex;align-items:center;gap:8px;}}
.section-label::after{{content:'';flex:1;height:1px;background:var(--border2);}}
.form-group{{display:flex;flex-direction:column;gap:6px;margin-bottom:12px;}}
label{{font-family:var(--mono);font-size:10px;color:var(--muted2);text-transform:uppercase;letter-spacing:0.1em;}}
input{{background:var(--surface);border:1px solid var(--border2);color:var(--text);padding:11px 14px;border-radius:9px;font-family:var(--mono);font-size:13px;outline:none;width:100%;transition:border-color 0.2s;}}
input:focus{{border-color:var(--accent);box-shadow:0 0 0 3px rgba(124,58,237,0.1);}}
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:12px;}}
.hint{{background:rgba(14,165,233,0.05);border:1px solid rgba(14,165,233,0.15);border-radius:7px;padding:9px 12px;font-family:var(--mono);font-size:10px;color:#7dd3fc;margin-top:6px;line-height:1.8;}}
.btn{{width:100%;padding:14px;background:linear-gradient(135deg,var(--accent),#6d28d9);color:#fff;border:none;border-radius:11px;font-family:var(--sans);font-size:15px;font-weight:700;cursor:pointer;margin-top:16px;transition:transform 0.15s;}}
.btn:hover{{transform:translateY(-2px);}}
.error-box{{background:rgba(244,63,94,0.08);border:1px solid rgba(244,63,94,0.2);border-radius:8px;padding:10px 14px;font-family:var(--mono);font-size:11px;color:#f87171;margin-bottom:16px;display:{"block" if error else "none"};}}
.logout-link{{font-family:var(--mono);font-size:11px;color:var(--muted2);text-align:center;margin-top:20px;}}
.logout-link a{{color:var(--rose);text-decoration:none;}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(16px);}}to{{opacity:1;transform:translateY(0);}}}}
</style>
</head>
<body>
<div class="card">
  <div class="user-bar">
    {'<img class="avatar" src="' + avatar + '" alt=""/>' if avatar else '<div class="avatar-fallback">' + username[0].upper() + '</div>'}
    <div class="user-info">
      <div class="user-name">{github_name}</div>
      <div class="user-email">✓ {github_email}</div>
    </div>
  </div>
  <h2>Connect Your Tools</h2>
  <div class="sub">Your credentials are stored privately — Jira tickets go to <strong>your</strong> Jira, not anyone else's.</div>
  <div class="error-box">All required fields must be filled in.</div>
  <form method="POST">
    <div class="section-label">Jira</div>
    <div class="form-group">
      <label>Jira Domain *</label>
      <input type="text" name="jira_domain" placeholder="yourname.atlassian.net" required/>
      <div class="hint">Just the domain — e.g. prateekmanocha22.atlassian.net</div>
    </div>
    <div class="two-col">
      <div class="form-group">
        <label>Jira Email *</label>
        <input type="email" name="jira_email" placeholder="you@email.com" value="{github_email}" required/>
      </div>
      <div class="form-group">
        <label>Project Key</label>
        <input type="text" name="jira_project_key" placeholder="KAN" value="KAN"/>
      </div>
    </div>
    <div class="form-group">
      <label>Jira API Token *</label>
      <input type="password" name="jira_api_token" placeholder="your Jira API token" required/>
      <div class="hint">Get it at id.atlassian.com → Security → API tokens</div>
    </div>
    <div class="section-label">Slack</div>
    <div class="two-col">
      <div class="form-group">
        <label>Slack Bot Token *</label>
        <input type="password" name="slack_token" placeholder="xoxb-..." required/>
      </div>
      <div class="form-group">
        <label>Channel</label>
        <input type="text" name="slack_channel" placeholder="releases" value="releases"/>
      </div>
    </div>
    <div class="hint">Get Slack token at api.slack.com → Your App → OAuth & Permissions</div>
    <button type="submit" class="btn">🚀 Launch NexRelease Agent</button>
  </form>
  <div class="logout-link"><a href="/oauth/logout">← Use a different account</a></div>
</div>
</body>
</html>"""

# ── Main app ───────────────────────────────────────────────────────────────────
@app.route("/app")
def main_app():
    username = session.get("github_username")
    if not username:
        return redirect("/")
    profile = get_profile(username)
    if not profile.get("jira_api_token") or not profile.get("slack_token"):
        return redirect("/setup")

    github_name  = session.get("github_name", username)
    avatar       = session.get("github_avatar", "")
    access_token = session.get("github_token", "")
    repos        = get_github_repos(access_token) if access_token else []
    repos_json   = json.dumps(repos)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>NexRelease</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;600;700;800;900&display=swap" rel="stylesheet"/>
<style>
:root {{
  --bg:#07080f;--surface:#0d0f1a;--card:#121526;--card2:#161929;--border:#1e2240;--border2:#252844;--accent:#7c3aed;--accent2:#0ea5e9;--teal:#0d9488;--red:#dc2626;--rose:#f43f5e;--gold:#f59e0b;--text:#e2e4f0;--muted:#4a5080;--muted2:#6b7199;--mono:'DM Mono',monospace;--sans:'Outfit',sans-serif;
}}
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box;}}
html{{scroll-behavior:smooth;}}
body{{font-family:var(--sans);background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden;}}
body::before{{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 600px 400px at 10% 20%,rgba(124,58,237,0.06) 0%,transparent 70%),radial-gradient(ellipse 500px 300px at 90% 80%,rgba(14,165,233,0.05) 0%,transparent 70%);pointer-events:none;z-index:0;}}
body::after{{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(124,58,237,0.025) 1px,transparent 1px),linear-gradient(90deg,rgba(124,58,237,0.025) 1px,transparent 1px);background-size:48px 48px;pointer-events:none;z-index:0;}}
.layout{{position:relative;z-index:1;display:grid;grid-template-columns:1fr 300px;min-height:100vh;}}
.main-col{{overflow-y:auto;border-right:1px solid var(--border);}}
.wrap{{max-width:820px;margin:0 auto;padding:0 36px 100px;}}
header{{display:flex;align-items:center;justify-content:space-between;padding:28px 0 40px;border-bottom:1px solid var(--border);margin-bottom:48px;flex-wrap:wrap;gap:12px;}}
.logo{{display:flex;flex-direction:column;gap:4px;}}
.logo-row{{display:flex;align-items:center;gap:14px;}}
.logo-icon{{width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;font-size:20px;box-shadow:0 0 24px rgba(124,58,237,0.4);}}
.logo-text{{font-size:22px;font-weight:900;letter-spacing:-0.8px;}}
.logo-text .nex{{color:transparent;background:linear-gradient(90deg,#a78bfa,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.logo-subtitle{{font-family:var(--mono);font-size:10px;color:var(--muted2);padding-left:54px;}}
.header-right{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;}}
.user-pill{{font-family:var(--mono);font-size:11px;padding:6px 12px;border-radius:20px;border:1px solid rgba(124,58,237,0.3);color:#a78bfa;display:flex;align-items:center;gap:8px;background:rgba(124,58,237,0.06);}}
.user-pill img{{width:18px;height:18px;border-radius:50%;}}
.status-pill{{font-family:var(--mono);font-size:11px;padding:6px 12px;border-radius:20px;border:1px solid rgba(13,148,136,0.4);color:var(--teal);display:flex;align-items:center;gap:7px;background:rgba(13,148,136,0.06);}}
.pulse-dot{{width:7px;height:7px;background:var(--teal);border-radius:50%;animation:pulse 2s infinite;}}
.logout-btn{{font-family:var(--mono);font-size:10px;color:var(--rose);background:transparent;border:1px solid rgba(244,63,94,0.25);border-radius:6px;padding:5px 10px;cursor:pointer;text-decoration:none;}}
.logout-btn:hover{{background:rgba(244,63,94,0.08);}}
.hero{{margin-bottom:44px;}}
.hero-eyebrow{{font-family:var(--mono);font-size:11px;color:var(--accent2);letter-spacing:0.15em;text-transform:uppercase;margin-bottom:16px;display:flex;align-items:center;gap:10px;}}
.hero-eyebrow::before{{content:'';width:20px;height:1px;background:var(--accent2);}}
.hero h1{{font-size:clamp(28px,4vw,46px);font-weight:900;line-height:1.08;letter-spacing:-2px;margin-bottom:14px;}}
.grad-purple{{background:linear-gradient(90deg,#a78bfa,#7c3aed,#0ea5e9);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.hero p{{font-size:15px;color:var(--muted2);line-height:1.75;max-width:520px;}}
.pipeline{{display:flex;align-items:center;margin-bottom:40px;overflow-x:auto;padding:4px 0 8px;}}
.pipe-step{{display:flex;flex-direction:column;align-items:center;gap:7px;flex-shrink:0;}}
.pipe-icon{{width:48px;height:48px;background:var(--card);border:1px solid var(--border2);border-radius:13px;display:flex;align-items:center;justify-content:center;font-size:20px;transition:all 0.35s;}}
.pipe-step.active .pipe-icon{{border-color:var(--accent);box-shadow:0 0 0 3px rgba(124,58,237,0.15);transform:translateY(-4px);}}
.pipe-step.done .pipe-icon{{border-color:var(--teal);background:rgba(13,148,136,0.08);}}
.pipe-label{{font-family:var(--mono);font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;}}
.pipe-step.active .pipe-label,.pipe-step.done .pipe-label{{color:var(--teal);}}
.pipe-arrow{{width:28px;height:2px;background:var(--border2);flex-shrink:0;margin-bottom:22px;position:relative;transition:background 0.4s;}}
.pipe-arrow.lit{{background:linear-gradient(90deg,var(--teal),var(--accent2));}}
.pipe-arrow::after{{content:'';position:absolute;right:-5px;top:-3px;border:4px solid transparent;border-left-color:inherit;}}
.pipe-arrow.lit::after{{border-left-color:var(--accent2);}}
.panel{{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:28px;margin-bottom:20px;position:relative;overflow:hidden;}}
.panel::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(124,58,237,0.3),transparent);}}
.panel-title{{font-size:11px;font-weight:700;color:var(--muted2);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:20px;display:flex;align-items:center;gap:10px;}}
.panel-title::before{{content:'';width:3px;height:14px;background:var(--accent);border-radius:2px;}}
.repo-row{{display:flex;gap:12px;align-items:flex-end;flex-wrap:wrap;margin-bottom:14px;}}
.repo-group{{display:flex;flex-direction:column;gap:6px;flex:1;min-width:180px;}}
.repo-group label,.field label{{font-family:var(--mono);font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;}}
select{{background:var(--surface);border:1px solid var(--border2);color:var(--text);padding:10px 14px;border-radius:9px;font-family:var(--mono);font-size:13px;outline:none;width:100%;}}
select:focus{{border-color:var(--accent);box-shadow:0 0 0 3px rgba(124,58,237,0.12);}}
select option{{background:var(--surface);}}
.field{{display:flex;flex-direction:column;gap:6px;}}
input[type="number"],input[type="text"]{{background:var(--surface);border:1px solid var(--border2);color:var(--text);padding:10px 14px;border-radius:9px;font-family:var(--mono);font-size:13px;outline:none;transition:border-color 0.2s,box-shadow 0.2s;}}
input[type="number"]{{width:100px;}}
input[type="text"]{{width:200px;}}
input:focus{{border-color:var(--accent);box-shadow:0 0 0 3px rgba(124,58,237,0.12);}}
.run-btn{{padding:11px 24px;background:linear-gradient(135deg,var(--accent),#6d28d9);color:#fff;border:none;border-radius:9px;font-family:var(--sans);font-size:14px;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:8px;transition:transform 0.15s,box-shadow 0.2s;box-shadow:0 4px 20px rgba(124,58,237,0.3);}}
.run-btn:hover{{transform:translateY(-2px);box-shadow:0 8px 28px rgba(124,58,237,0.45);}}
.run-btn:disabled{{background:var(--border);color:var(--muted);cursor:not-allowed;transform:none;box-shadow:none;}}
.secondary-btn{{padding:9px 16px;background:transparent;color:var(--accent2);border:1px solid rgba(14,165,233,0.3);border-radius:9px;font-family:var(--sans);font-size:13px;font-weight:600;cursor:pointer;}}
.secondary-btn:hover{{background:rgba(14,165,233,0.08);}}
.danger-btn{{padding:5px 10px;background:transparent;color:var(--rose);border:1px solid rgba(244,63,94,0.3);border-radius:6px;font-family:var(--mono);font-size:10px;cursor:pointer;}}
.danger-btn:hover{{background:rgba(244,63,94,0.1);}}
.pr-suggestions{{background:var(--surface);border:1px solid var(--border2);border-radius:9px;overflow:hidden;margin-bottom:14px;display:none;max-height:200px;overflow-y:auto;}}
.pr-item{{padding:10px 14px;cursor:pointer;border-bottom:1px solid var(--border);font-family:var(--mono);font-size:12px;display:flex;align-items:center;gap:10px;transition:background 0.15s;}}
.pr-item:last-child{{border-bottom:none;}}
.pr-item:hover{{background:rgba(124,58,237,0.07);}}
.pr-num{{color:var(--accent2);font-size:11px;flex-shrink:0;}}
.pr-title-text{{color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
.pr-loading{{padding:12px 14px;font-family:var(--mono);font-size:11px;color:var(--muted);}}
.terminal{{background:#050609;border:1px solid var(--border2);border-radius:12px;overflow:hidden;}}
.terminal-bar{{background:var(--surface);border-bottom:1px solid var(--border);padding:10px 16px;display:flex;align-items:center;gap:8px;}}
.tdot{{width:10px;height:10px;border-radius:50%;}}
.tdot.r{{background:#ff5f57;}}.tdot.y{{background:#ffbd2e;}}.tdot.g{{background:#28c941;}}
.terminal-title{{font-family:var(--mono);font-size:11px;color:var(--muted);margin-left:8px;}}
.terminal-body{{padding:18px;font-family:var(--mono);font-size:12px;line-height:2.1;min-height:140px;}}
.t-muted{{color:var(--muted);}}.t-purple{{color:#a78bfa;}}.t-blue{{color:var(--accent2);}}.t-teal{{color:var(--teal);}}.t-warn{{color:#fb923c;}}.t-red{{color:var(--rose);}}.t-white{{color:var(--text);}}
.step-boxes{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:20px;}}
.step-box{{background:var(--surface);border:1px solid var(--border2);border-radius:11px;padding:15px;transition:border-color 0.3s;}}
.step-box.done{{border-color:rgba(13,148,136,0.35);}}.step-box.error{{border-color:rgba(244,63,94,0.4);}}
.step-box-label{{font-family:var(--mono);font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;}}
.step-box-val{{font-size:13px;color:var(--text);line-height:1.5;word-break:break-all;}}
.step-box-val a{{color:var(--accent2);text-decoration:none;}}.step-box-val a:hover{{text-decoration:underline;}}
.badge{{display:inline-flex;align-items:center;gap:5px;padding:3px 9px;border-radius:5px;font-family:var(--mono);font-size:11px;font-weight:700;}}
.badge.ok{{background:rgba(13,148,136,0.12);color:var(--teal);border:1px solid rgba(13,148,136,0.3);}}
.badge.err{{background:rgba(244,63,94,0.1);color:var(--rose);border:1px solid rgba(244,63,94,0.3);}}
.hint{{margin-top:16px;background:rgba(14,165,233,0.04);border:1px solid rgba(14,165,233,0.15);border-radius:9px;padding:12px 15px;font-family:var(--mono);font-size:11px;color:#7dd3fc;display:flex;align-items:center;gap:8px;}}
.hint code{{background:rgba(0,0,0,0.4);padding:2px 7px;border-radius:4px;}}
.member-row{{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border);}}
.member-row:last-child{{border-bottom:none;}}
.member-name{{font-family:var(--mono);font-size:13px;color:var(--text);}}
.add-row{{display:flex;gap:10px;margin-top:16px;}}
.add-row input[type="text"]{{flex:1;width:auto;}}
.cal-status-row{{display:flex;align-items:center;gap:12px;flex-wrap:wrap;}}
.spin{{display:inline-block;width:13px;height:13px;border:2px solid var(--border2);border-top-color:var(--accent);border-radius:50%;animation:spin 0.7s linear infinite;vertical-align:middle;margin-right:4px;}}
.sec-modal{{position:fixed;inset:0;z-index:300;background:rgba(5,6,15,0.94);backdrop-filter:blur(14px);display:none;align-items:center;justify-content:center;}}
.sec-modal.open{{display:flex;animation:fadeUp 0.3s ease;}}
.sec-panel{{background:var(--card);border:2px solid rgba(220,38,38,0.6);border-radius:20px;padding:40px;max-width:520px;width:92%;text-align:center;box-shadow:0 0 80px rgba(220,38,38,0.1);}}
.sec-icon{{font-size:48px;margin-bottom:16px;display:block;animation:pulse 1s infinite;}}
.sec-title{{font-family:var(--mono);font-size:11px;font-weight:700;color:var(--rose);letter-spacing:0.15em;text-transform:uppercase;margin-bottom:12px;}}
.sec-sub{{font-size:14px;color:var(--text);line-height:1.8;margin-bottom:14px;}}
.sec-details{{font-family:var(--mono);font-size:11px;color:var(--muted2);background:rgba(220,38,38,0.06);border:1px solid rgba(220,38,38,0.2);border-radius:10px;padding:12px 14px;text-align:left;line-height:2.2;margin-bottom:4px;}}
.sec-actions{{display:flex;gap:8px;justify-content:center;margin-top:20px;flex-wrap:wrap;}}
.sec-dismiss{{padding:10px 16px;background:transparent;color:var(--muted2);border:1px solid var(--border2);border-radius:9px;font-family:var(--sans);font-size:13px;font-weight:700;cursor:pointer;}}
.sec-view{{padding:10px 16px;background:linear-gradient(135deg,var(--red),var(--rose));color:#fff;border:none;border-radius:9px;font-family:var(--sans);font-size:13px;font-weight:700;cursor:pointer;}}
.sec-approve{{padding:10px 16px;background:rgba(13,148,136,0.15);color:var(--teal);border:1px solid rgba(13,148,136,0.35);border-radius:9px;font-family:var(--sans);font-size:13px;font-weight:700;cursor:pointer;}}
.sec-whitelist{{padding:10px 16px;background:rgba(124,58,237,0.1);color:#a78bfa;border:1px solid rgba(124,58,237,0.25);border-radius:9px;font-family:var(--sans);font-size:13px;font-weight:700;cursor:pointer;}}
.detail-overlay{{position:fixed;inset:0;z-index:100;background:rgba(5,6,15,0.88);backdrop-filter:blur(10px);display:none;align-items:flex-start;justify-content:flex-end;}}
.detail-overlay.open{{display:flex;}}
.detail-panel{{width:min(660px,95vw);height:100vh;overflow-y:auto;background:var(--surface);border-left:1px solid var(--border2);padding:32px;animation:slideIn 0.3s ease;}}
.detail-panel::-webkit-scrollbar{{width:3px;}}.detail-panel::-webkit-scrollbar-thumb{{background:var(--border2);border-radius:2px;}}
.detail-close{{position:sticky;top:0;display:flex;justify-content:flex-end;margin-bottom:20px;}}
.detail-close button{{background:var(--card);border:1px solid var(--border2);color:var(--text);font-size:16px;width:34px;height:34px;border-radius:8px;cursor:pointer;}}
.detail-hero{{margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid var(--border);}}
.detail-pr-num{{font-family:var(--mono);font-size:10px;color:var(--accent2);margin-bottom:6px;}}
.detail-title{{font-size:19px;font-weight:800;line-height:1.3;margin-bottom:8px;}}
.detail-author{{font-family:var(--mono);font-size:11px;color:var(--muted2);}}
.detail-time{{font-family:var(--mono);font-size:10px;color:var(--muted);margin-top:4px;}}
.detail-section{{margin-bottom:18px;}}
.detail-section-title{{font-family:var(--mono);font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;display:flex;align-items:center;gap:8px;}}
.detail-section-title::after{{content:'';flex:1;height:1px;background:var(--border);}}
.detail-box{{background:var(--card);border:1px solid var(--border2);border-radius:11px;padding:16px;margin-bottom:8px;}}
.detail-box.threat{{border-color:rgba(220,38,38,0.4);background:rgba(220,38,38,0.04);}}
.detail-box.safe{{border-color:rgba(13,148,136,0.3);background:rgba(13,148,136,0.04);}}
.detail-box-label{{font-family:var(--mono);font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;}}
.detail-box p{{font-size:14px;color:var(--text);line-height:1.8;white-space:pre-wrap;}}
.detail-box a{{color:var(--accent2);text-decoration:none;font-family:var(--mono);font-size:12px;word-break:break-all;}}
.detail-actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px;}}
.detail-approve-btn{{padding:9px 16px;background:rgba(13,148,136,0.15);color:var(--teal);border:1px solid rgba(13,148,136,0.35);border-radius:9px;font-family:var(--sans);font-size:13px;font-weight:700;cursor:pointer;}}
.detail-whitelist-btn{{padding:9px 16px;background:rgba(124,58,237,0.1);color:#a78bfa;border:1px solid rgba(124,58,237,0.25);border-radius:9px;font-family:var(--sans);font-size:13px;font-weight:700;cursor:pointer;}}
#toast-container{{position:fixed;top:20px;right:20px;z-index:200;display:flex;flex-direction:column;gap:8px;pointer-events:none;}}
.toast{{padding:13px 16px;border-radius:10px;font-family:var(--mono);font-size:11px;display:flex;align-items:center;gap:10px;animation:fadeUp 0.3s ease;max-width:360px;pointer-events:all;line-height:1.5;}}
.toast.threat{{background:#120608;border:1px solid rgba(220,38,38,0.5);color:#f87171;}}
.toast.ok{{background:#06100d;border:1px solid rgba(13,148,136,0.4);color:var(--teal);}}
.toast-close{{margin-left:auto;opacity:0.5;cursor:pointer;font-size:14px;flex-shrink:0;}}
.feed-col{{background:rgba(10,11,19,0.97);display:flex;flex-direction:column;position:sticky;top:0;height:100vh;overflow:hidden;}}
.feed-header{{padding:18px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-shrink:0;}}
.feed-title{{font-family:var(--mono);font-size:10px;color:var(--accent2);text-transform:uppercase;letter-spacing:0.12em;display:flex;align-items:center;gap:8px;}}
.live-dot{{width:6px;height:6px;background:var(--teal);border-radius:50%;animation:pulse 1.5s infinite;}}
.clear-btn{{font-family:var(--mono);font-size:10px;color:var(--rose);background:transparent;border:1px solid rgba(244,63,94,0.25);border-radius:6px;padding:4px 10px;cursor:pointer;}}
.feed-list{{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:8px;}}
.feed-list::-webkit-scrollbar{{width:3px;}}.feed-list::-webkit-scrollbar-thumb{{background:var(--border2);border-radius:2px;}}
.ncard{{background:var(--card2);border:1px solid var(--border);border-radius:11px;padding:13px;cursor:pointer;transition:border-color 0.2s,transform 0.2s;animation:fadeUp 0.35s ease both;}}
.ncard:hover{{border-color:rgba(124,58,237,0.35);transform:translateX(-2px);}}
.ncard.threat{{border-color:rgba(220,38,38,0.4);background:rgba(220,38,38,0.04);}}
.ncard.verified{{border-color:rgba(13,148,136,0.25);}}
.ncard.pending{{border-color:rgba(245,158,11,0.4);background:rgba(245,158,11,0.04);}}
.ncard-top{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:7px;}}
.ncard-meta{{display:flex;flex-direction:column;gap:2px;}}
.ncard-time{{font-family:var(--mono);font-size:9px;color:var(--muted);}}
.ncard-pr-num{{font-family:var(--mono);font-size:9px;color:var(--accent2);}}
.ndel{{background:transparent;border:none;color:var(--muted);cursor:pointer;font-size:12px;padding:0 2px;line-height:1;flex-shrink:0;}}
.ndel:hover{{color:var(--rose);}}
.ncard-title{{font-size:12px;font-weight:700;color:var(--text);margin-bottom:3px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
.ncard-author{{font-family:var(--mono);font-size:10px;color:var(--muted);margin-bottom:9px;}}
.ncard-badges{{display:flex;gap:4px;flex-wrap:wrap;margin-bottom:9px;}}
.nb{{font-family:var(--mono);font-size:8px;padding:2px 6px;border-radius:4px;font-weight:700;}}
.nb.ok{{background:rgba(13,148,136,0.12);color:var(--teal);border:1px solid rgba(13,148,136,0.2);}}
.nb.warn{{background:rgba(220,38,38,0.12);color:#f87171;border:1px solid rgba(220,38,38,0.25);}}
.nb.blue{{background:rgba(14,165,233,0.1);color:var(--accent2);border:1px solid rgba(14,165,233,0.2);}}
.nb.gray{{background:rgba(74,80,128,0.15);color:var(--muted2);border:1px solid rgba(74,80,128,0.2);}}
.nb.purple{{background:rgba(124,58,237,0.12);color:#a78bfa;border:1px solid rgba(124,58,237,0.2);}}
.nb.gold{{background:rgba(245,158,11,0.12);color:var(--gold);border:1px solid rgba(245,158,11,0.2);}}
.more-btn{{width:100%;padding:6px;background:transparent;border:1px solid rgba(124,58,237,0.2);border-radius:7px;font-family:var(--mono);font-size:9px;color:#a78bfa;cursor:pointer;}}
.ncard-actions{{display:flex;gap:5px;margin-top:7px;}}
.approve-btn{{padding:5px 10px;background:rgba(13,148,136,0.15);color:var(--teal);border:1px solid rgba(13,148,136,0.3);border-radius:6px;font-family:var(--mono);font-size:9px;cursor:pointer;font-weight:700;}}
.whitelist-btn{{padding:5px 10px;background:rgba(124,58,237,0.1);color:#a78bfa;border:1px solid rgba(124,58,237,0.2);border-radius:6px;font-family:var(--mono);font-size:9px;cursor:pointer;font-weight:700;}}
.empty-feed{{font-family:var(--mono);font-size:10px;color:var(--muted);text-align:center;padding:40px 16px;line-height:2.2;}}
.team-section{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px 22px;margin-top:24px;position:relative;overflow:hidden;}}
.team-section::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(14,165,233,0.3),rgba(124,58,237,0.3),transparent);}}
.team-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin:14px 0;}}
.team-member{{background:var(--surface);border:1px solid var(--border2);border-radius:11px;padding:10px 14px;display:flex;align-items:center;gap:10px;}}
.member-avatar{{width:28px;height:28px;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;color:#fff;flex-shrink:0;}}
.member-full-name{{font-size:13px;font-weight:600;color:var(--text);}}
.team-footer{{font-family:var(--mono);font-size:11px;color:var(--muted);text-align:center;padding-top:14px;border-top:1px solid var(--border);}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(14px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes pulse{{0%,100%{{opacity:1;transform:scale(1);}}50%{{opacity:0.4;transform:scale(0.85);}}}}
@keyframes spin{{to{{transform:rotate(360deg);}}}}
@keyframes slideIn{{from{{transform:translateX(40px);opacity:0;}}to{{transform:translateX(0);opacity:1;}}}}
@media(max-width:960px){{.layout{{grid-template-columns:1fr;}}.feed-col{{position:relative;height:auto;border:none;border-top:1px solid var(--border);}}.feed-list{{max-height:340px;}}}}
@media(max-width:600px){{.step-boxes{{grid-template-columns:1fr;}}.team-grid{{grid-template-columns:1fr;}}}}
</style>
</head>
<body>

<div class="sec-modal" id="sec-modal">
  <div class="sec-panel">
    <span class="sec-icon">⚠️</span>
    <div class="sec-title">Unauthorized Contributor</div>
    <div class="sec-sub" id="sec-modal-msg"></div>
    <div class="sec-details" id="sec-modal-details"></div>
    <div class="sec-actions">
      <button class="sec-dismiss" onclick="dismissAlert()">Dismiss</button>
      <button class="sec-approve" id="sec-approve-btn">✓ Approve & Generate</button>
      <button class="sec-whitelist" id="sec-whitelist-btn">+ Whitelist</button>
      <button class="sec-view" id="sec-view-btn">View Details →</button>
    </div>
  </div>
</div>

<div id="toast-container"></div>

<div class="detail-overlay" id="detail-overlay" onclick="closeDetail(event)">
  <div class="detail-panel">
    <div class="detail-close"><button onclick="closeDetailBtn()">✕</button></div>
    <div id="detail-content"></div>
  </div>
</div>

<div class="layout">
  <div class="main-col">
    <div class="wrap">
      <header>
        <div class="logo">
          <div class="logo-row">
            <div class="logo-icon">⚡</div>
            <div class="logo-text"><span class="nex">Nex</span>Release</div>
          </div>
          <div class="logo-subtitle">by Schrodingers</div>
        </div>
        <div class="header-right">
          <div class="user-pill">
            {'<img src="' + avatar + '" alt=""/>' if avatar else '👤'}
            {github_name}
          </div>
          <div class="status-pill"><div class="pulse-dot"></div>ONLINE</div>
          <a href="/oauth/logout" class="logout-btn">Logout</a>
        </div>
      </header>

      <div class="hero">
        <div class="hero-eyebrow">MCP-Powered Automation</div>
        <h1>Release coordination,<br><span class="grad-purple">fully automated.</span></h1>
        <p>Merge a PR and the AI agent reads it, files the Jira ticket, pings Slack, and schedules the go/no-go — all in under 10 seconds.</p>
      </div>

      <div class="pipeline" id="pipeline">
        <div class="pipe-step" id="ps0"><div class="pipe-icon">🔀</div><div class="pipe-label">PR Merge</div></div>
        <div class="pipe-arrow" id="pa0"></div>
        <div class="pipe-step" id="ps1"><div class="pipe-icon">🧠</div><div class="pipe-label">AI Read</div></div>
        <div class="pipe-arrow" id="pa1"></div>
        <div class="pipe-step" id="ps2"><div class="pipe-icon">🎫</div><div class="pipe-label">Jira</div></div>
        <div class="pipe-arrow" id="pa2"></div>
        <div class="pipe-step" id="ps3"><div class="pipe-icon">💬</div><div class="pipe-label">Slack</div></div>
        <div class="pipe-arrow" id="pa3"></div>
        <div class="pipe-step" id="ps4"><div class="pipe-icon">📅</div><div class="pipe-label">Meeting</div></div>
      </div>

      <div class="panel">
        <div class="panel-title">Trigger Agent Manually</div>
        <div class="repo-row">
          <div class="repo-group">
            <label>GitHub Repository</label>
            <select id="repo-select" onchange="onRepoChange()">
              <option value="">— select a repository —</option>
              {''.join(f'<option value="{r}">{r}</option>' for r in repos)}
            </select>
          </div>
          <div class="field">
            <label>PR Number</label>
            <input type="number" id="pr-number" value="" min="1" placeholder="auto" oninput="hideSuggestions()"/>
          </div>
          <button class="run-btn" id="run-btn" onclick="runAgent()">
            <span id="btn-icon">▶</span> Run Agent
          </button>
        </div>
        <div class="pr-suggestions" id="pr-suggestions"></div>
        <div class="terminal">
          <div class="terminal-bar">
            <div class="tdot r"></div><div class="tdot y"></div><div class="tdot g"></div>
            <span class="terminal-title">release-agent — bash</span>
          </div>
          <div class="terminal-body" id="log"><span class="t-muted">$ waiting for trigger...</span></div>
        </div>
        <div class="step-boxes" id="step-boxes" style="display:none;">
          <div class="step-box" id="sb-pr"><div class="step-box-label">📦 PR Info</div><div class="step-box-val" id="sb-pr-val">—</div></div>
          <div class="step-box" id="sb-security"><div class="step-box-label">🔐 Security</div><div class="step-box-val" id="sb-security-val">—</div></div>
          <div class="step-box" id="sb-summary"><div class="step-box-label">🧠 AI Summary</div><div class="step-box-val" id="sb-summary-val">—</div></div>
          <div class="step-box" id="sb-jira"><div class="step-box-label">🎫 Jira Ticket</div><div class="step-box-val" id="sb-jira-val">—</div></div>
          <div class="step-box" id="sb-slack"><div class="step-box-label">💬 Slack</div><div class="step-box-val" id="sb-slack-val">—</div></div>
          <div class="step-box" id="sb-meeting"><div class="step-box-label">📅 Meeting</div><div class="step-box-val" id="sb-meeting-val">—</div></div>
        </div>
        <div class="hint">🔗 Auto-trigger: point GitHub webhooks to <code>POST /webhook</code></div>
      </div>

      <div class="panel">
        <div class="panel-title">🔐 Team Whitelist</div>
        <p style="font-size:13px;color:var(--muted2);margin-bottom:18px;line-height:1.6;">Approved contributors. Unauthorized PRs trigger a security alert.</p>
        <div id="member-list"></div>
        <div class="add-row">
          <input type="text" id="new-member" placeholder="github-username"/>
          <button class="secondary-btn" onclick="addMember()">+ Add</button>
        </div>
      </div>

      <div class="panel">
        <div class="panel-title">📅 Google Calendar</div>
        <p style="font-size:13px;color:var(--muted2);margin-bottom:18px;line-height:1.6;">Connect your Google Calendar for automatic meeting scheduling.</p>
        <div class="cal-status-row">
          <div id="cal-status" style="font-family:var(--mono);font-size:12px;color:var(--muted);"><span class="spin"></span> Checking...</div>
          <button class="secondary-btn" id="cal-connect-btn" onclick="connectCalendar()" style="display:none;">Connect Google Calendar</button>
        </div>
      </div>

      <div class="team-section">
        <div style="font-family:var(--mono);font-size:10px;color:var(--muted2);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:12px;">Project Info</div>
        <div style="font-size:18px;font-weight:900;letter-spacing:-0.5px;margin-bottom:4px;"><span style="background:linear-gradient(90deg,#a78bfa,#0ea5e9);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Nex</span>Release</div>
        <div style="font-family:var(--mono);font-size:11px;color:var(--muted2);margin-bottom:14px;">MCP-Based AI Release Coordinator · Gen-AI Hackathon 2026</div>
        <div class="team-grid">
          <div class="team-member"><div class="member-avatar" style="background:linear-gradient(135deg,#7c3aed,#6d28d9);">PM</div><div class="member-full-name">Prateek Manocha</div></div>
          <div class="team-member"><div class="member-avatar" style="background:linear-gradient(135deg,#0ea5e9,#0284c7);">KB</div><div class="member-full-name">Krish Bhandari</div></div>
          <div class="team-member"><div class="member-avatar" style="background:linear-gradient(135deg,#0d9488,#0f766e);">NB</div><div class="member-full-name">Niraj Basel</div></div>
          <div class="team-member"><div class="member-avatar" style="background:linear-gradient(135deg,#dc2626,#b91c1c);">DR</div><div class="member-full-name">Dhanush Rajakumar</div></div>
        </div>
        <div class="team-footer">Team Schrodingers · Built with Groq AI · GitHub · Jira · Slack</div>
      </div>
    </div>
  </div>

  <div class="feed-col">
    <div class="feed-header">
      <div class="feed-title"><div class="live-dot"></div>{username}'s Feed</div>
      <button class="clear-btn" onclick="clearAll()">Clear</button>
    </div>
    <div class="feed-list" id="feed-list">
      <div class="empty-feed">No PRs yet.<br><br>Select a repo above<br>and merge a PR.</div>
    </div>
  </div>
</div>

<script>
const log = document.getElementById('log');
let allNotifications = [];
let lastSeenIds = new Set();

function showToast(msg, type='ok', duration=6000) {{
  const tc = document.getElementById('toast-container');
  const t = document.createElement('div');
  t.className = 'toast ' + type;
  t.innerHTML = `<span>${{type==='threat'?'⚠':'✓'}}</span><span style="flex:1">${{msg}}</span><span class="toast-close" onclick="this.parentElement.remove()">✕</span>`;
  tc.appendChild(t);
  setTimeout(()=>{{if(t.parentElement)t.remove();}},duration);
}}

async function checkCalendarStatus() {{
  try {{
    const res = await fetch('/oauth/google/status');
    const data = await res.json();
    const status = document.getElementById('cal-status');
    const btn = document.getElementById('cal-connect-btn');
    btn.style.display = 'inline-flex';
    if (data.connected) {{
      status.innerHTML = '<span style="color:var(--teal);">✓ Google Calendar connected</span>';
      btn.textContent = 'Reconnect';
    }} else {{
      status.innerHTML = '<span style="color:var(--muted);">Not connected — using fallback</span>';
      btn.textContent = 'Connect Google Calendar';
    }}
  }} catch(e) {{
    document.getElementById('cal-connect-btn').style.display = 'inline-flex';
  }}
}}

async function connectCalendar() {{
  const res = await fetch('/oauth/google');
  const data = await res.json();
  if (data.auth_url) {{
    const popup = window.open(data.auth_url, '_blank', 'width=500,height=650');
    showToast('Authorize in the popup window', 'ok', 8000);
    const check = setInterval(async () => {{
      if (popup && popup.closed) {{ clearInterval(check); checkCalendarStatus(); }}
    }}, 1000);
  }} else {{
    showToast('Error: ' + (data.error || 'Unknown'), 'threat');
  }}
}}

checkCalendarStatus();

async function onRepoChange() {{
  const repo = document.getElementById('repo-select').value;
  const box = document.getElementById('pr-suggestions');
  document.getElementById('pr-number').value = '';
  if (!repo) {{ box.style.display='none'; return; }}
  box.style.display='block';
  box.innerHTML='<div class="pr-loading"><span class="spin"></span> Loading merged PRs...</div>';
  try {{
    const res = await fetch('/repo-prs?repo='+encodeURIComponent(repo));
    const data = await res.json();
    if (!data.prs || data.prs.length===0) {{
      box.innerHTML='<div class="pr-loading" style="color:var(--muted2)">No merged PRs found.</div>';
      return;
    }}
    box.innerHTML = data.prs.map(p=>
      `<div class="pr-item" onclick="selectPr(${{p.number}})">
        <span class="pr-num">#${{p.number}}</span>
        <span class="pr-title-text">${{p.title}}</span>
      </div>`
    ).join('');
  }} catch(e) {{
    box.innerHTML='<div class="pr-loading" style="color:var(--rose)">Failed to load PRs.</div>';
  }}
}}

function selectPr(num) {{
  document.getElementById('pr-number').value = num;
  document.getElementById('pr-suggestions').style.display='none';
}}

function hideSuggestions() {{
  document.getElementById('pr-suggestions').style.display='none';
}}

function showSecurityAlert(n, idx) {{
  document.getElementById('sec-modal-msg').textContent =
    `PR #${{n.pr_number}} "${{n.pr_title}}" — @${{n.author}} is not on your whitelist.`;
  document.getElementById('sec-modal-details').innerHTML =
    `PR: #${{n.pr_number}}<br>Author: @${{n.author}}<br>Time: ${{n.time}}`;
  document.getElementById('sec-approve-btn').onclick = async () => {{
    dismissAlert();
    showToast('Approving PR...','ok');
    await fetch('/approve',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{index:idx}})}});
    loadNotifications();
  }};
  document.getElementById('sec-whitelist-btn').onclick = async () => {{
    await fetch('/whitelist/add',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{username:n.author}})}});
    loadMembers();
    showToast(`@${{n.author}} added`,'ok');
    dismissAlert();
  }};
  document.getElementById('sec-view-btn').onclick = ()=>{{dismissAlert();openDetail(idx);}};
  document.getElementById('sec-modal').classList.add('open');
}}
function dismissAlert() {{ document.getElementById('sec-modal').classList.remove('open'); }}

function openDetail(index) {{
  const n = allNotifications[index];
  if(!n)return;
  const isThreat  = n.security && n.security.status==='unauthorized';
  const isVerified= n.security && n.security.status==='verified';
  document.getElementById('detail-content').innerHTML=`
    <div class="detail-hero">
      <div class="detail-pr-num">PR #${{n.pr_number}}</div>
      <div class="detail-title">${{n.pr_title}}</div>
      <div class="detail-author">by @${{n.author}}</div>
      <div class="detail-time">${{n.pending?'⏳ Pending':'Processed at '+n.time}}</div>
    </div>
    <div class="detail-section"><div class="detail-section-title">🔐 Security</div>
      <div class="detail-box ${{isThreat?'threat':isVerified?'safe':''}}">
        <div class="detail-box-label">Status</div>
        <p>${{n.security?n.security.message:'—'}}</p>
        ${{n.pending?`<div class="detail-actions">
          <button class="detail-approve-btn" onclick="approveNotif(${{index}})">✓ Approve & Generate</button>
          <button class="detail-whitelist-btn" onclick="whitelistAuthor('${{n.author}}')">+ Whitelist</button>
        </div>`:''}}</div></div>
    <div class="detail-section"><div class="detail-section-title">🧠 Summary</div>
      <div class="detail-box"><p>${{n.summary||'—'}}</p></div></div>
    <div class="detail-section"><div class="detail-section-title">✅ Checklist</div>
      <div class="detail-box"><p>${{n.checklist||'—'}}</p></div></div>
    <div class="detail-section"><div class="detail-section-title">⚠️ Risks</div>
      <div class="detail-box"><p>${{n.risks||'—'}}</p></div></div>
    <div class="detail-section"><div class="detail-section-title">🎫 Jira</div>
      <div class="detail-box">
        ${{n.jira_url?`<a href="${{n.jira_url}}" target="_blank">${{n.jira_url}}</a>`:'<p>—</p>'}}</div></div>
    <div class="detail-section"><div class="detail-section-title">💬 Slack</div>
      <div class="detail-box"><p>${{n.slack_message||'—'}}</p>
        <div style="margin-top:8px">${{n.slack_posted?'<span class="badge ok">✓ Posted</span>':'<span class="badge err">✗ Not posted</span>'}}</div></div></div>
    <div class="detail-section"><div class="detail-section-title">📅 Meeting</div>
      <div class="detail-box"><p>${{n.meeting||'—'}}</p></div></div>
    <div class="detail-section"><div class="detail-section-title">🔗 PR Link</div>
      <div class="detail-box">
        ${{n.pr_url?`<a href="${{n.pr_url}}" target="_blank">${{n.pr_url}}</a>`:'<p>—</p>'}}</div></div>`;
  document.getElementById('detail-overlay').classList.add('open');
}}

async function approveNotif(index) {{
  closeDetailBtn();
  showToast('Approving...','ok');
  await fetch('/approve',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{index}})}});
  loadNotifications();
}}
async function whitelistAuthor(author) {{
  await fetch('/whitelist/add',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{username:author}})}});
  loadMembers();
  showToast(`@${{author}} added`,'ok');
}}
function closeDetail(e){{if(e.target===document.getElementById('detail-overlay'))closeDetailBtn();}}
function closeDetailBtn(){{document.getElementById('detail-overlay').classList.remove('open');}}

async function loadNotifications() {{
  const res = await fetch('/notifications');
  const data = await res.json();
  allNotifications = data.notifications;
  renderFeed(allNotifications);
  allNotifications.forEach((n,idx)=>{{
    const uid=`${{n.pr_number}}-${{n.time}}`;
    if(!lastSeenIds.has(uid)){{
      lastSeenIds.add(uid);
      if(n.security&&n.security.status==='unauthorized'){{
        showSecurityAlert(n,idx);
        showToast(`⚠ PR #${{n.pr_number}} by @${{n.author}} not whitelisted`,'threat',10000);
      }} else if(lastSeenIds.size>1){{
        showToast(`PR #${{n.pr_number}} processed`,'ok');
      }}
    }}
  }});
}}

function renderFeed(notifications) {{
  const feed = document.getElementById('feed-list');
  if(notifications.length===0){{
    feed.innerHTML='<div class="empty-feed">No PRs yet.<br><br>Select a repo above<br>and merge a PR.</div>';return;
  }}
  feed.innerHTML=notifications.map((n,i)=>{{
    const isThreat  = n.security&&n.security.status==='unauthorized';
    const isVerified= n.security&&n.security.status==='verified';
    const isPending = n.pending;
    const cls = isPending?'pending':isThreat?'threat':isVerified?'verified':'';
    return `<div class="ncard ${{cls}}">
      <div class="ncard-top">
        <div class="ncard-meta">
          <span class="ncard-time">${{n.time}}</span>
          <span class="ncard-pr-num">PR #${{n.pr_number}}</span>
        </div>
        <button class="ndel" onclick="event.stopPropagation();deleteNotif(${{i}})">✕</button>
      </div>
      <div class="ncard-title">${{n.pr_title}}</div>
      <div class="ncard-author">by @${{n.author}}</div>
      <div class="ncard-badges">
        <span class="nb blue">PR</span>
        ${{n.jira_url?'<span class="nb ok">Jira ✓</span>':'<span class="nb gray">Jira —</span>'}}
        ${{n.slack_posted?'<span class="nb ok">Slack ✓</span>':'<span class="nb gray">Slack —</span>'}}
        ${{n.meeting?'<span class="nb ok">Meeting ✓</span>':'<span class="nb gray">Meeting —</span>'}}
        ${{isThreat?`<span class="nb warn">⚠ @${{n.author}}</span>`:''}}
        ${{isVerified?'<span class="nb purple">✓ Auth</span>':''}}
        ${{isPending?'<span class="nb gold">⏳ Pending</span>':''}}
      </div>
      <button class="more-btn" onclick="openDetail(${{i}})">More Info →</button>
      ${{isPending?`<div class="ncard-actions">
        <button class="approve-btn" onclick="event.stopPropagation();approveNotif(${{i}})">✓ Approve</button>
        <button class="whitelist-btn" onclick="event.stopPropagation();whitelistAuthor('${{n.author}}')">+ Whitelist</button>
      </div>`:''}}</div>`;
  }}).join('');
}}

async function deleteNotif(i){{
  await fetch('/notifications/delete',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{index:i}})}});
  loadNotifications();
}}
async function clearAll(){{
  await fetch('/notifications/clear',{{method:'POST'}});
  lastSeenIds.clear();loadNotifications();
}}
(async()=>{{
  const res=await fetch('/notifications');
  const data=await res.json();
  allNotifications=data.notifications;
  allNotifications.forEach(n=>lastSeenIds.add(`${{n.pr_number}}-${{n.time}}`));
  renderFeed(allNotifications);
}})();
setInterval(loadNotifications,5000);

async function loadMembers(){{
  const res=await fetch('/whitelist');
  const data=await res.json();
  renderMembers(data.members);
}}
function renderMembers(members){{
  const list=document.getElementById('member-list');
  if(members.length===0){{list.innerHTML='<p style="font-family:var(--mono);font-size:12px;color:var(--muted);margin-bottom:8px;">No members yet.</p>';return;}}
  list.innerHTML=members.map((m,i)=>`
    <div class="member-row">
      <span class="member-name">@${{m}}</span>
      <button class="danger-btn" onclick="removeMember(${{i}})">Remove</button>
    </div>`).join('');
}}
async function addMember(){{
  const input=document.getElementById('new-member');
  const name=input.value.trim();
  if(!name)return;
  await fetch('/whitelist/add',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{username:name}})}});
  input.value='';loadMembers();
}}
async function removeMember(index){{
  await fetch('/whitelist/remove',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{index}})}});
  loadMembers();
}}
loadMembers();

function addLine(html){{log.innerHTML+='<br>'+html;log.scrollTop=log.scrollHeight;}}
function setStep(idx){{
  for(let i=0;i<5;i++){{
    const s=document.getElementById('ps'+i);
    s.classList.remove('active','done');
    if(i<idx)s.classList.add('done');
    if(i===idx)s.classList.add('active');
    if(i<4)document.getElementById('pa'+i).classList.toggle('lit',i<idx);
  }}
}}
function setBox(id,val,done){{
  const box=document.getElementById('sb-'+id);
  const valEl=document.getElementById('sb-'+id+'-val');
  if(box)box.classList.toggle('done',done);
  if(valEl)valEl.innerHTML=val;
}}
function sleep(ms){{return new Promise(r=>setTimeout(r,ms));}}

async function runAgent(){{
  const repo=document.getElementById('repo-select').value;
  const pr=document.getElementById('pr-number').value;
  const btn=document.getElementById('run-btn');
  if(!repo){{showToast('Select a repository first','threat');return;}}
  if(!pr){{showToast('Select or enter a PR number','threat');return;}}
  btn.disabled=true;
  document.getElementById('btn-icon').innerHTML='<span class="spin"></span>';
  document.getElementById('step-boxes').style.display='none';
  document.getElementById('pr-suggestions').style.display='none';
  log.innerHTML='<span class="t-muted">$ release-agent run --repo '+repo+' --pr '+pr+'</span>';
  setStep(-1);await sleep(300);
  addLine('<span class="t-purple">⟳  initializing agent...</span>');
  await sleep(500);setStep(0);
  addLine('<span class="t-white">[ 1/5 ]</span> <span class="t-muted">reading PR from GitHub...</span>');
  try{{
    const res=await fetch('/run?repo='+encodeURIComponent(repo)+'&pr='+pr);
    const data=await res.json();
    if(data.error){{addLine('<span class="t-red">✗  error: '+data.error+'</span>');btn.disabled=false;document.getElementById('btn-icon').textContent='▶';return;}}
    await sleep(400);setStep(1);
    addLine('<span class="t-teal">✓</span>  <span class="t-white">PR read:</span> <span class="t-blue">'+data.pr_title+'</span>');
    if(data.security){{
      const sc=data.security;
      if(sc.status==='unauthorized'){{
        addLine('<span class="t-red">⚠  SECURITY: '+sc.message+'</span>');
        addLine('<span class="t-warn">⏳ Paused — approve in feed →</span>');
        document.getElementById('step-boxes').style.display='grid';
        setBox('pr',`<strong>${{data.pr_title}}</strong>`,true);
        setBox('security',sc.message,false);
        setBox('summary',data.summary||'—',true);
        setBox('jira','⏳ Pending',false);setBox('slack','⏳ Pending',false);setBox('meeting','⏳ Pending',false);
        loadNotifications();btn.disabled=false;document.getElementById('btn-icon').textContent='▶';return;
      }} else if(sc.status==='verified'){{addLine('<span class="t-teal">🔐 '+sc.message+'</span>');}}
    }}
    await sleep(400);addLine('<span class="t-white">[ 2/5 ]</span> <span class="t-muted">summarizing with Groq AI...</span>');
    await sleep(500);setStep(2);addLine('<span class="t-teal">✓</span>  summary generated');
    await sleep(300);addLine('<span class="t-white">[ 3/5 ]</span> <span class="t-muted">creating Jira ticket...</span>');
    await sleep(400);setStep(3);addLine('<span class="t-teal">✓</span>  ticket → <span class="t-blue">'+(data.jira_url||'N/A')+'</span>');
    await sleep(300);addLine('<span class="t-white">[ 4/5 ]</span> <span class="t-muted">posting to Slack...</span>');
    await sleep(400);setStep(4);addLine('<span class="t-teal">✓</span>  Slack posted');
    await sleep(300);addLine('<span class="t-white">[ 5/5 ]</span> <span class="t-muted">scheduling meeting...</span>');
    await sleep(400);addLine('<span class="t-teal">✓</span>  meeting → <span class="t-blue">'+(data.meeting||'N/A')+'</span>');
    await sleep(300);addLine('');
    addLine('<span class="t-purple">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>');
    addLine('<span class="t-teal">  AGENT COMPLETE  </span>');
    addLine('<span class="t-purple">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>');
    document.getElementById('step-boxes').style.display='grid';
    const sc=data.security||{{}};
    setBox('pr',`<strong>${{data.pr_title}}</strong><br><span style="color:var(--muted2);font-size:11px;">by @${{data.author||'—'}}</span>`,true);
    setBox('security',sc.message||'—',sc.status==='verified');
    setBox('summary',data.summary||'—',true);
    setBox('jira',data.jira_url?`<a href="${{data.jira_url}}" target="_blank">${{data.jira_url}}</a>`:'—',!!data.jira_url);
    setBox('slack',data.slack_posted?'<span class="badge ok">✓ Posted</span>':'<span class="badge err">✗ Failed</span>',data.slack_posted);
    setBox('meeting',data.meeting||'—',!!data.meeting);
    loadNotifications();
  }}catch(err){{addLine('<span class="t-red">✗  error: '+err+'</span>');}}
  btn.disabled=false;document.getElementById('btn-icon').textContent='▶';
}}
</script>
</body>
</html>"""

# ── API routes ─────────────────────────────────────────────────────────────────
def current_user():
    return session.get("github_username", "anonymous")

def get_token_for_user(username):
    """Get GitHub token — session first, fall back to saved profile."""
    return session.get("github_token") or get_profile(username).get("github_token", "")

@app.route("/repo-prs")
def repo_prs():
    repo         = request.args.get("repo", "")
    access_token = session.get("github_token", "")
    if not repo or not access_token:
        return jsonify({"prs": []})
    return jsonify({"prs": get_repo_prs_list(access_token, repo)})

@app.route("/notifications")
def get_notifications():
    return jsonify({"notifications": load_notifications(current_user())})

@app.route("/notifications/delete", methods=["POST"])
def delete_notification():
    data     = request.get_json()
    index    = data.get("index")
    username = current_user()
    notifications = load_notifications(username)
    if index is not None and 0 <= index < len(notifications):
        notifications.pop(index)
        save_notifications(username, notifications)
    return jsonify({"notifications": notifications})

@app.route("/notifications/clear", methods=["POST"])
def clear_notifications():
    username = current_user()
    save_notifications(username, [])
    return jsonify({"notifications": []})

@app.route("/whitelist")
def get_whitelist():
    return jsonify({"members": load_whitelist()})

@app.route("/whitelist/add", methods=["POST"])
def add_to_whitelist():
    data     = request.get_json()
    username = data.get("username", "").strip()
    if not username:
        return jsonify({"error": "empty"})
    members = load_whitelist()
    if username.lower() not in [m.lower() for m in members]:
        members.append(username)
        save_whitelist(members)
    return jsonify({"members": members})

@app.route("/whitelist/remove", methods=["POST"])
def remove_from_whitelist():
    data  = request.get_json()
    index = data.get("index")
    members = load_whitelist()
    if index is not None and 0 <= index < len(members):
        members.pop(index)
        save_whitelist(members)
    return jsonify({"members": members})

@app.route("/approve", methods=["POST"])
def approve():
    data     = request.get_json()
    index    = data.get("index")
    username = current_user()
    jira_creds   = get_user_jira(username)
    slack_creds  = get_user_slack(username)
    access_token = get_token_for_user(username)  # ← fixed
    notifications = load_notifications(username)
    if index is None or index >= len(notifications):
        return jsonify({"error": "invalid index"})
    n = notifications[index]
    try:
        repo      = n.get("pr_url", "").split("github.com/")[-1].split("/pull/")[0]
        pr_number = n.get("pr_number", 1)
        pr_data   = get_pr_info(repo, pr_number, access_token)  # ← fixed
        summary   = summarize_pr(pr_data)
        ticket    = create_jira_ticket(
            title=summary["jira_title"], description=summary["summary"],
            checklist=summary["checklist"], risks=summary["risks"],
            pr_id=pr_number, **jira_creds
        )
        slack_msg = f"""*PR Approved* — `{pr_data['title']}`
*Author:* {pr_data['author']}
{summary['slack_message']}
*Jira:* {ticket.get('url', 'N/A')}
*PR:* {pr_data['pr_url']}
⚠️ Author was not whitelisted but manually approved.""".strip()
        slack_result = post_slack_message(
            slack_msg,
            slack_token=slack_creds["slack_token"],
            channel=slack_creds["slack_channel"]
        )
        meeting = create_calendar_event(
            meeting_title=summary["meeting_title"],
            pr_url=pr_data["pr_url"], risks=summary["risks"]
        )
        notifications[index].update({
            "jira_url": ticket.get("url", ""), "slack_posted": slack_result["success"],
            "meeting": meeting["time"], "slack_message": slack_msg,
            "summary": summary["summary"], "checklist": summary["checklist"],
            "risks": summary["risks"], "pending": False
        })
        save_notifications(username, notifications)
        return jsonify({"status": "approved"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/run")
def run():
    pr_number    = request.args.get("pr", 1, type=int)
    repo         = request.args.get("repo", "")
    username     = current_user()
    access_token = get_token_for_user(username)  # ← fixed
    jira_creds   = get_user_jira(username)
    slack_creds  = get_user_slack(username)

    if not repo:
        return jsonify({"error": "No repository selected"})

    ensure_owner_whitelisted(repo)
    members = load_whitelist()
    if username.lower() not in [m.lower() for m in members]:
        members.append(username)
        save_whitelist(members)

    try:
        pr_data  = get_pr_info(repo, pr_number, access_token)  # ← fixed
        security = check_contributor(pr_data["author"])

        if security["status"] == "unauthorized":
            add_notification(
                username=username, pr_number=pr_number,
                pr_title=pr_data["title"], author=pr_data["author"],
                jira_url="", slack_posted=False, meeting="",
                security=security, pr_url=pr_data["pr_url"],
                summary="⚠️ Security alert — awaiting approval.",
                checklist="", risks="Unauthorized contributor.",
                slack_message="", pending=True
            )
            return jsonify({
                "pr_title": pr_data["title"], "author": pr_data["author"],
                "summary": "⚠️ Security alert — awaiting approval.",
                "jira_url": "", "slack_posted": False, "meeting": "",
                "pr_url": pr_data["pr_url"], "security": security
            })

        summary = summarize_pr(pr_data)
        ticket  = create_jira_ticket(
            title=summary["jira_title"], description=summary["summary"],
            checklist=summary["checklist"], risks=summary["risks"],
            pr_id=pr_number, **jira_creds
        )
        slack_msg = f"""*New Release* — `{pr_data['title']}`
*Author:* {pr_data['author']}
*CI Status:* {pr_data['ci_status']}
{summary['slack_message']}
*Jira:* {ticket.get('url', 'N/A')}
*PR:* {pr_data['pr_url']}""".strip()

        slack_result = post_slack_message(
            slack_msg,
            slack_token=slack_creds["slack_token"],
            channel=slack_creds["slack_channel"]
        )
        meeting = create_calendar_event(
            meeting_title=summary["meeting_title"],
            pr_url=pr_data["pr_url"], risks=summary["risks"]
        )
        add_notification(
            username=username, pr_number=pr_number,
            pr_title=pr_data["title"], author=pr_data["author"],
            jira_url=ticket.get("url", ""), slack_posted=slack_result["success"],
            meeting=meeting["time"], security=security,
            pr_url=pr_data["pr_url"], summary=summary["summary"],
            checklist=summary["checklist"], risks=summary["risks"],
            slack_message=slack_msg, pending=False
        )
        return jsonify({
            "pr_title": pr_data["title"], "author": pr_data["author"],
            "summary": summary["summary"], "jira_url": ticket.get("url", ""),
            "slack_posted": slack_result["success"], "meeting": meeting["time"],
            "pr_url": pr_data["pr_url"], "security": security
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/webhook", methods=["POST"])
def webhook():
    data      = request.get_json()
    action    = data.get("action")
    pr        = data.get("pull_request", {})
    is_merged = pr.get("merged", False)
    repo      = data.get("repository", {}).get("full_name", "")
    owner     = repo.split("/")[0].lower() if "/" in repo else "unknown"
    ensure_owner_whitelisted(repo)

    access_token    = get_best_token_for_repo(repo)
    users_to_notify = get_users_for_repo(repo)
    jira_creds      = get_user_jira(owner)
    slack_creds     = get_user_slack(owner)

    if action in ["opened", "reopened"]:
        pr_number = pr["number"]
        try:
            pr_data  = get_pr_info(repo, pr_number, access_token)  # ← fixed
            security = check_contributor(pr_data["author"])
            if security["status"] == "unauthorized":
                for notify_user in users_to_notify:
                  add_notification(
                    username=notify_user, pr_number=pr_number,
                    pr_title=pr_data["title"], author=pr_data["author"],
                    jira_url="", slack_posted=False, meeting="",
                    security=security, pr_url=pr_data["pr_url"],
                    summary="⚠️ Unauthorized contributor opened a PR.",
                    checklist="", risks="Review before merging.",
                    slack_message="", pending=True
                )
            return jsonify({"status": "security checked", "pr": pr_number})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    if action == "closed" and is_merged:
        pr_number = pr["number"]
        try:
            pr_data  = get_pr_info(repo, pr_number, access_token)  # ← fixed
            security = check_contributor(pr_data["author"])
            if security["status"] == "unauthorized":
                for notify_user in users_to_notify:
                    add_notification(
                      username=notify_user, pr_number=pr_number,
                      pr_title=pr_data["title"], author=pr_data["author"],
                      jira_url="", slack_posted=False, meeting="",
                      security=security, pr_url=pr_data["pr_url"],
                      summary="⚠️ Merged by unauthorized contributor.",
                      checklist="", risks="Review immediately.",
                      slack_message="", pending=True
                )
                return jsonify({"status": "security alert"})

            summary = summarize_pr(pr_data)
            ticket  = create_jira_ticket(
                title=summary["jira_title"], description=summary["summary"],
                checklist=summary["checklist"], risks=summary["risks"],
                pr_id=pr_number, **jira_creds
            )
            slack_msg = f"""*PR Auto-processed* — `{pr_data['title']}`
*Author:* {pr_data['author']}
{summary['slack_message']}
*Jira:* {ticket.get('url', 'N/A')}""".strip()
            post_slack_message(
                slack_msg,
                slack_token=slack_creds["slack_token"],
                channel=slack_creds["slack_channel"]
            )
            meeting = create_calendar_event(
                meeting_title=summary["meeting_title"],
                pr_url=pr_data["pr_url"], risks=summary["risks"]
            )
            for notify_user in users_to_notify:
                add_notification(
                  username=notify_user, pr_number=pr_number,
                  pr_title=pr_data["title"], author=pr_data["author"],
                  jira_url=ticket.get("url", ""), slack_posted=True,
                  meeting=meeting["time"], security=security,
                  pr_url=pr_data["pr_url"], summary=summary["summary"],
                  checklist=summary["checklist"], risks=summary["risks"],
                  slack_message=slack_msg, pending=False
            )
            return jsonify({"status": "agent triggered", "pr": pr_number})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    return jsonify({"status": "ignored"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))