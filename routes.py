# # app/routes.py
# import os
# import requests
# from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
# from flask_login import login_user, logout_user, current_user, login_required
# from dotenv import load_dotenv
# from collections import Counter
# from datetime import datetime, timedelta
# from werkzeug.utils import secure_filename

# from . import db
# from .models import User, Report
# from .nlp_utils import analyze_text

# load_dotenv()
# bp = Blueprint("main", __name__)
# API_KEY = os.getenv("API_KEY")

# # ================== Home ==================
# @bp.route("/")
# def home():
#     return render_template("index.html")


# # ================== Register ==================
# @bp.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form.get("username")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         interested_area = request.form.get("interested_area")

#         if User.query.filter((User.username == username) | (User.email == email)).first():
#             flash("Username or email already exists!", "danger")
#             return redirect(url_for("main.register"))

#         new_user = User(
#             username=username,
#             email=email,
#             interested_area=interested_area
#         )
#         new_user.set_password(password)

#         db.session.add(new_user)
#         db.session.commit()

#         flash("Account created successfully! Please log in.", "success")
#         return redirect(url_for("main.login"))

#     return render_template("register.html")


# # ================== Trending News ==================
# @bp.route("/trending", methods=["GET", "POST"])
# def trending():
#     selected_area = request.form.get("interested_area", "")
#     selected_country = request.form.get("country", "")
#     selected_date = request.form.get("date_filter", "")
#     keyword = request.form.get("keyword", "")

#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {
#         "token": API_KEY,
#         "lang": "en",
#         "max": 30
#     }

#     category_map = {
#         "Technology": "technology",
#         "Sports": "sports",
#         "Health": "health",
#         "Business": "business",
#         "Politics": "politics",
#         "Science": "science",
#         "World": "world"
#     }

#     if selected_area in category_map:
#         params["topic"] = category_map[selected_area]

#     if selected_country:
#         params["country"] = selected_country

#     if keyword:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = keyword

#     today = datetime.utcnow().date()
#     if selected_date == "today":
#         params["from"] = today.strftime("%Y-%m-%d")
#     elif selected_date == "yesterday":
#         params["from"] = (today - timedelta(days=1)).strftime("%Y-%m-%d")
#         params["to"] = today.strftime("%Y-%m-%d")
#     elif selected_date == "past_week":
#         params["from"] = (today - timedelta(days=7)).strftime("%Y-%m-%d")

#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         data = response.json()
#     except Exception:
#         flash("⚠️ Failed to fetch news. Please try again later.", "danger")
#         return render_template("trending.html", articles=[], sentiment_counts={}, entity_counts={}, 
#                                selected_area=selected_area, selected_country=selected_country,
#                                selected_date=selected_date, keyword=keyword)

#     articles = data.get("articles", [])
#     if not articles:
#         flash("No news found for the selected filters.", "warning")

#     enriched_articles = []
#     sentiment_list = []
#     entity_list = []

#     for art in articles:
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description

#         nlp_result = analyze_text(content)
#         sentiment = nlp_result.get("sentiment", "NEUTRAL")
#         entities = nlp_result.get("entities", [])

#         sentiment_list.append(sentiment)
#         entity_list.extend([ent for ent, _ in entities])

#         published_at = art.get("publishedAt")
#         if published_at:
#             try:
#                 published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
#                 published_at = published_at.strftime("%d %b %Y, %H:%M UTC")
#             except Exception:
#                 published_at = None

#         enriched_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url"),
#             "image": art.get("image"),
#             "sentiment": sentiment,
#             "entities": entities,
#             "published_at": published_at
#         })

#     sentiment_counts = Counter(sentiment_list)
#     entity_counts = dict(Counter(entity_list).most_common(10))

#     return render_template(
#         "trending.html",
#         articles=enriched_articles,
#         sentiment_counts=sentiment_counts,
#         entity_counts=entity_counts,
#         selected_area=selected_area,
#         selected_country=selected_country,
#         selected_date=selected_date,
#         keyword=keyword
#     )


# # ================== Login ==================
# @bp.route("/login", methods=["GET", "POST"])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for("main.dashboard"))

#     if request.method == "POST":
#         login_id = request.form.get("login_id")
#         password = request.form.get("password")

#         user = User.query.filter((User.email == login_id) | (User.username == login_id)).first()

#         if user and user.check_password(password):
#             login_user(user)
#             flash(f"Welcome back, {user.username}!", "success")
#             return redirect(url_for("main.dashboard"))
#         else:
#             flash("Login failed. Check username/email and password.", "danger")
#             return redirect(url_for("main.login"))

#     return render_template("login.html")


# # ================== Logout ==================
# @bp.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     flash("You have been logged out.", "info")
#     return redirect(url_for("main.home"))


# # ================== Dashboard ==================
# @bp.route("/dashboard")
# @login_required
# def dashboard():
#     interested_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 5}

#     category_map = {
#         "Technology": "technology",
#         "Sports": "sports",
#         "Health": "health",
#         "Business": "business",
#         "Politics": "politics",
#         "Science": "science",
#         "World": "world"
#     }

#     if interested_area in category_map:
#         params["topic"] = category_map[interested_area]
#     elif interested_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = interested_area

#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         articles = response.json().get("articles", [])
#     except Exception:
#         articles = []

#     analyzed_articles = []
#     for art in articles:
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description
#         nlp_result = analyze_text(content)

#         analyzed_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url"),
#             "image": art.get("image"),
#             "publishedAt": art.get("publishedAt"),
#             "sentiment": nlp_result.get("sentiment", "NEUTRAL"),
#             "sentiment_score": nlp_result.get("sentiment_score"),
#             "entities": nlp_result.get("entities", [])
#         })

#     user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.date_created.desc()).all()
#     return render_template("dashboard.html", username=current_user.username, reports=user_reports, articles=analyzed_articles)


# # ================== Reports ==================
# @bp.route("/reports")
# @login_required
# def reports():
#     reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.date_created.desc()).all()
#     return render_template("reports.html", reports=reports)


# # ================== Generate Report ==================
# @bp.route("/generate_report", methods=["POST"])
# @login_required
# def generate_report():
#     """Generate a detailed report with trending news + NLP analysis using GNews."""
#     selected_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 10}

#     category_map = {
#         "Technology": "technology",
#         "Sports": "sports",
#         "Health": "health",
#         "Business": "business",
#         "Politics": "politics",
#         "Science": "science",
#         "World": "world"
#     }

#     if selected_area in category_map:
#         params["topic"] = category_map[selected_area]
#     elif selected_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = selected_area

#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         articles = response.json().get("articles", [])
#     except Exception:
#         flash("⚠️ Failed to fetch news. Report not generated.", "danger")
#         return redirect(url_for("main.dashboard"))

#     if not articles:
#         flash("No news found for your area. Report not generated.", "warning")
#         return redirect(url_for("main.dashboard"))

#     report_lines = [
#         f"NewsPulse Report for {current_user.username}",
#         f"Generated at: {datetime.utcnow()} UTC",
#         f"Interested Area: {selected_area}",
#         "",
#         "Trending News and Analysis:\n"
#     ]

#     for idx, art in enumerate(articles, start=1):
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description

#         published_at = art.get("publishedAt")
#         if published_at:
#             try:
#                 published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
#                 published_at = published_at.strftime("%d %b %Y, %H:%M UTC")
#             except:
#                 published_at = None

#         nlp_result = analyze_text(content)
#         sentiment = nlp_result.get("sentiment", "NEUTRAL")
#         sentiment_score = nlp_result.get("sentiment_score", None)
#         entities = [ent for ent, _ in nlp_result.get("entities", [])]

#         report_lines.append(f"{idx}. Title: {title}")
#         report_lines.append(f"   Description: {description}")
#         report_lines.append(f"   URL: {art.get('url')}")
#         report_lines.append(f"   Published: {published_at}")
#         report_lines.append(f"   Sentiment: {sentiment} ({sentiment_score})")
#         report_lines.append(f"   Entities: {', '.join(entities) if entities else 'None'}\n")

#     report_text = "\n".join(report_lines)

#     reports_dir = os.path.join(os.getcwd(), "generated_reports")
#     os.makedirs(reports_dir, exist_ok=True)
#     filename = f"report_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.txt"
#     file_path = os.path.join(reports_dir, secure_filename(filename))
#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(report_text)

#     report = Report(
#         user_id=current_user.id,
#         file_path=file_path,
#         text=report_text,
#         sentiment=None,
#         sentiment_score=None,
#         entities=None
#     )
#     db.session.add(report)
#     db.session.commit()

#     flash(f"✅ Detailed report '{filename}' generated successfully!", "success")
#     return redirect(url_for("main.reports"))


# # ================== Download Report ==================
# @bp.route("/download_report/<int:report_id>")
# @login_required
# def download_report(report_id):
#     report = Report.query.get_or_404(report_id)
#     if report.user_id != current_user.id:
#         flash("❌ Unauthorized access!", "danger")
#         return redirect(url_for("main.reports"))
#     return send_file(report.file_path, as_attachment=True)


# # ================== Profile ==================
# @bp.route("/profile", methods=["GET", "POST"])
# @login_required
# def profile():
#     if request.method == "POST":
#         current_user.username = request.form.get("username")
#         current_user.email = request.form.get("email")
#         current_user.interested_area = request.form.get("interested_area")

#         db.session.commit()
#         flash("Profile updated successfully!", "success")
#         return redirect(url_for("main.profile"))

#     return render_template("profile.html")



# import os
# import requests
# from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
# from flask_login import login_user, logout_user, current_user, login_required
# from dotenv import load_dotenv
# from collections import Counter
# from datetime import datetime, timedelta
# from werkzeug.utils import secure_filename

# from . import db
# from .models import User, Report
# from .nlp_utils import analyze_text

# load_dotenv()
# bp = Blueprint("main", __name__)
# API_KEY = os.getenv("API_KEY")

# # ================== Home ==================
# @bp.route("/")
# def home():
#     return render_template("index.html")


# # ================== Register ==================
# @bp.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form.get("username")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         interested_area = request.form.get("interested_area")

#         if User.query.filter((User.username == username) | (User.email == email)).first():
#             flash("Username or email already exists!", "danger")
#             return redirect(url_for("main.register"))

#         new_user = User(
#             username=username,
#             email=email,
#             interested_area=interested_area
#         )
#         new_user.set_password(password)

#         db.session.add(new_user)
#         db.session.commit()

#         flash("Account created successfully! Please log in.", "success")
#         return redirect(url_for("main.login"))

#     return render_template("register.html")


# # ================== Trending News ==================
# @bp.route("/trending", methods=["GET", "POST"])
# def trending():
#     selected_area = request.form.get("interested_area", "")
#     selected_country = request.form.get("country", "")
#     selected_date = request.form.get("date_filter", "")
#     keyword = request.form.get("keyword", "")

#     # Default GNews endpoint
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {
#         "token": API_KEY,
#         "lang": "en",
#         "max": 30
#     }

#     # Category mapping to GNews topics
#     category_map = {
#         "Technology": "technology",
#         "Sports": "sports",
#         "Health": "health",
#         "Business": "business",
#         "Politics": "politics",
#         "Science": "science",
#         "World": "world"
#     }

#     if selected_area in category_map:
#         params["topic"] = category_map[selected_area]

#     if selected_country:
#         params["country"] = selected_country

#     # If keyword given → switch to search endpoint
#     if keyword:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = keyword

#     # Date filter handling
#     today = datetime.utcnow().date()
#     if selected_date == "today":
#         params["from"] = today.strftime("%Y-%m-%d")
#     elif selected_date == "yesterday":
#         params["from"] = (today - timedelta(days=1)).strftime("%Y-%m-%d")
#         params["to"] = today.strftime("%Y-%m-%d")
#     elif selected_date == "past_week":
#         params["from"] = (today - timedelta(days=7)).strftime("%Y-%m-%d")

#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         data = response.json()
#     except Exception:
#         flash("⚠️ Failed to fetch news. Please try again later.", "danger")
#         return render_template("trending.html", articles=[], sentiment_counts={}, entity_counts={}, 
#                                selected_area=selected_area, selected_country=selected_country,
#                                selected_date=selected_date, keyword=keyword)

#     articles = data.get("articles", [])
#     if not articles:
#         flash("No news found for the selected filters.", "warning")

#     enriched_articles = []
#     sentiment_list = []
#     entity_list = []

#     for art in articles:
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description

#         # Run NLP
#         nlp_result = analyze_text(content)
#         sentiment = nlp_result.get("sentiment", "NEUTRAL")
#         entities = nlp_result.get("entities", [])

#         sentiment_list.append(sentiment)
#         entity_list.extend([ent for ent, _ in entities])

#         published_at = art.get("publishedAt")
#         if published_at:
#             try:
#                 published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
#                 published_at = published_at.strftime("%d %b %Y, %H:%M UTC")
#             except Exception:
#                 published_at = None

#         enriched_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url"),
#             "image": art.get("image"),
#             "sentiment": sentiment,
#             "entities": entities,
#             "published_at": published_at,
#             "source": art.get("source", {}).get("name")
#         })

#     sentiment_counts = Counter(sentiment_list)
#     entity_counts = dict(Counter(entity_list).most_common(10))

#     return render_template(
#         "trending.html",
#         articles=enriched_articles,
#         sentiment_counts=sentiment_counts,
#         entity_counts=entity_counts,
#         selected_area=selected_area,
#         selected_country=selected_country,
#         selected_date=selected_date,
#         keyword=keyword
#     )


# # ================== Login ==================
# @bp.route("/login", methods=["GET", "POST"])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for("main.dashboard"))

#     if request.method == "POST":
#         login_id = request.form.get("login_id")
#         password = request.form.get("password")

#         user = User.query.filter((User.email == login_id) | (User.username == login_id)).first()

#         if user and user.check_password(password):
#             login_user(user)
#             flash(f"Welcome back, {user.username}!", "success")
#             return redirect(url_for("main.dashboard"))
#         else:
#             flash("Login failed. Check username/email and password.", "danger")
#             return redirect(url_for("main.login"))

#     return render_template("login.html")


# # ================== Logout ==================
# @bp.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     flash("You have been logged out.", "info")
#     return redirect(url_for("main.home"))


# # ================== Dashboard ==================
# @bp.route("/dashboard")
# @login_required
# def dashboard():
#     interested_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 5}

#     category_map = {
#         "Technology": "technology",
#         "Sports": "sports",
#         "Health": "health",
#         "Business": "business",
#         "Politics": "politics",
#         "Science": "science",
#         "World": "world"
#     }

#     if interested_area in category_map:
#         params["topic"] = category_map[interested_area]
#     elif interested_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = interested_area

#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         articles = response.json().get("articles", [])
#     except Exception:
#         articles = []

#     analyzed_articles = []
#     for art in articles:
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description
#         nlp_result = analyze_text(content)

#         analyzed_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url"),
#             "image": art.get("image"),
#             "publishedAt": art.get("publishedAt"),
#             "sentiment": nlp_result.get("sentiment", "NEUTRAL"),
#             "sentiment_score": nlp_result.get("sentiment_score"),
#             "entities": nlp_result.get("entities", [])
#         })

#     user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.date_created.desc()).all()
#     return render_template("dashboard.html", username=current_user.username, reports=user_reports, articles=analyzed_articles)


# # ================== Reports ==================
# @bp.route("/reports")
# @login_required
# def reports():
#     reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.date_created.desc()).all()
#     return render_template("reports.html", reports=reports)


# # ================== Generate Report ==================
# @bp.route("/generate_report", methods=["POST"])
# @login_required
# def generate_report():
#     """Generate a detailed report with trending news + NLP analysis using GNews."""
#     selected_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 10}

#     category_map = {
#         "Technology": "technology",
#         "Sports": "sports",
#         "Health": "health",
#         "Business": "business",
#         "Politics": "politics",
#         "Science": "science",
#         "World": "world"
#     }

#     if selected_area in category_map:
#         params["topic"] = category_map[selected_area]
#     elif selected_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = selected_area

#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         articles = response.json().get("articles", [])
#     except Exception:
#         flash("⚠️ Failed to fetch news. Report not generated.", "danger")
#         return redirect(url_for("main.dashboard"))

#     if not articles:
#         flash("No news found for your area. Report not generated.", "warning")
#         return redirect(url_for("main.dashboard"))

#     report_lines = [
#         f"NewsPulse Report for {current_user.username}",
#         f"Generated at: {datetime.utcnow()} UTC",
#         f"Interested Area: {selected_area}",
#         "",
#         "Trending News and Analysis:\n"
#     ]

#     for idx, art in enumerate(articles, start=1):
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description

#         published_at = art.get("publishedAt")
#         if published_at:
#             try:
#                 published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
#                 published_at = published_at.strftime("%d %b %Y, %H:%M UTC")
#             except:
#                 published_at = None

#         nlp_result = analyze_text(content)
#         sentiment = nlp_result.get("sentiment", "NEUTRAL")
#         sentiment_score = nlp_result.get("sentiment_score", None)
#         entities = [ent for ent, _ in nlp_result.get("entities", [])]

#         report_lines.append(f"{idx}. Title: {title}")
#         report_lines.append(f"   Description: {description}")
#         report_lines.append(f"   URL: {art.get('url')}")
#         report_lines.append(f"   Published: {published_at}")
#         report_lines.append(f"   Sentiment: {sentiment} ({sentiment_score})")
#         report_lines.append(f"   Entities: {', '.join(entities) if entities else 'None'}\n")

#     report_text = "\n".join(report_lines)

#     reports_dir = os.path.join(os.getcwd(), "generated_reports")
#     os.makedirs(reports_dir, exist_ok=True)
#     filename = f"report_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.txt"
#     file_path = os.path.join(reports_dir, secure_filename(filename))
#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(report_text)

#     report = Report(
#         user_id=current_user.id,
#         file_path=file_path,
#         text=report_text,
#         sentiment=None,
#         sentiment_score=None,
#         entities=None
#     )
#     db.session.add(report)
#     db.session.commit()

#     flash(f"✅ Detailed report '{filename}' generated successfully!", "success")
#     return redirect(url_for("main.reports"))


# # ================== Download Report ==================
# @bp.route("/download_report/<int:report_id>")
# @login_required
# def download_report(report_id):
#     report = Report.query.get_or_404(report_id)
#     if report.user_id != current_user.id:
#         flash("❌ Unauthorized access!", "danger")
#         return redirect(url_for("main.reports"))
#     return send_file(report.file_path, as_attachment=True)


# # ================== Profile ==================
# @bp.route("/profile", methods=["GET", "POST"])
# @login_required
# def profile():
#     if request.method == "POST":
#         current_user.username = request.form.get("username")
#         current_user.email = request.form.get("email")
#         current_user.interested_area = request.form.get("interested_area")

#         db.session.commit()
#         flash("Profile updated successfully!", "success")
#         return redirect(url_for("main.profile"))

#     return render_template("profile.html")


# import os
# import requests
# from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
# from flask_login import login_user, logout_user, current_user, login_required
# from dotenv import load_dotenv
# from collections import Counter
# from datetime import datetime, timedelta
# from werkzeug.utils import secure_filename

# from . import db
# from .models import User, Report
# from .nlp_utils import analyze_text

# load_dotenv()
# bp = Blueprint("main", __name__)
# API_KEY = os.getenv("API_KEY")

# # ================== Home ==================
# @bp.route("/")
# def home():
#     return render_template("index.html")


# # ================== Register ==================
# @bp.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form.get("username")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         interested_area = request.form.get("interested_area")

#         if User.query.filter((User.username == username) | (User.email == email)).first():
#             flash("Username or email already exists!", "danger")
#             return redirect(url_for("main.register"))

#         new_user = User(
#             username=username,
#             email=email,
#             interested_area=interested_area
#         )
#         new_user.set_password(password)

#         db.session.add(new_user)
#         db.session.commit()

#         flash("Account created successfully! Please log in.", "success")
#         return redirect(url_for("main.login"))

#     return render_template("register.html")


# # ================== Trending News ==================
# @bp.route("/trending", methods=["GET", "POST"])
# def trending():
#     selected_area = request.form.get("interested_area", "")
#     selected_country = request.form.get("country", "")
#     selected_date = request.form.get("date_filter", "")
#     keyword = request.form.get("keyword", "")

#     # Default GNews endpoint
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {
#         "token": API_KEY,
#         "lang": "en",
#         "max": 30
#     }

#     # Category mapping to GNews topics
#     category_map = {
#         "Technology": "technology",
#         "Sports": "sports",
#         "Health": "health",
#         "Business": "business",
#         "Politics": "politics",
#         "Science": "science",
#         "World": "world"
#     }

#     if selected_area in category_map:
#         params["topic"] = category_map[selected_area]

#     if selected_country:
#         params["country"] = selected_country

#     # If keyword given → switch to search endpoint
#     if keyword:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = keyword

#     # ⚠️ NOTE: GNews free plan does NOT support "from" and "to" → remove them
#     today = datetime.utcnow().date()
#     if selected_date in ["today", "yesterday", "past_week"]:
#         flash("⚠️ Date filtering is not supported in the free GNews API. Showing latest news only.", "warning")

#     try:
#         response = requests.get(url, params=params)

#         if response.status_code != 200:
#             try:
#                 error_msg = response.json().get("errors", response.text)
#             except:
#                 error_msg = response.text
#             flash(f"⚠️ GNews Error: {error_msg}", "danger")
#             return render_template("trending.html", articles=[], sentiment_counts={}, entity_counts={},
#                                    selected_area=selected_area, selected_country=selected_country,
#                                    selected_date=selected_date, keyword=keyword)

#         data = response.json()
#     except Exception as e:
#         flash(f"⚠️ Exception: {str(e)}", "danger")
#         return render_template("trending.html", articles=[], sentiment_counts={}, entity_counts={}, 
#                                selected_area=selected_area, selected_country=selected_country,
#                                selected_date=selected_date, keyword=keyword)

#     articles = data.get("articles", [])
#     if not articles:
#         flash("No news found for the selected filters.", "warning")

#     enriched_articles = []
#     sentiment_list = []
#     entity_list = []

#     for art in articles:
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description

#         # Run NLP
#         nlp_result = analyze_text(content)
#         sentiment = nlp_result.get("sentiment", "NEUTRAL")
#         entities = nlp_result.get("entities", [])

#         sentiment_list.append(sentiment)
#         entity_list.extend([ent for ent, _ in entities])

#         published_at = art.get("publishedAt")
#         if published_at:
#             try:
#                 published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
#                 published_at = published_at.strftime("%d %b %Y, %H:%M UTC")
#             except Exception:
#                 published_at = None

#         enriched_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url"),
#             "image": art.get("image"),
#             "sentiment": sentiment,
#             "entities": entities,
#             "published_at": published_at,
#             "source": art.get("source", {}).get("name")
#         })

#     sentiment_counts = Counter(sentiment_list)
#     entity_counts = dict(Counter(entity_list).most_common(10))

#     return render_template(
#         "trending.html",
#         articles=enriched_articles,
#         sentiment_counts=sentiment_counts,
#         entity_counts=entity_counts,
#         selected_area=selected_area,
#         selected_country=selected_country,
#         selected_date=selected_date,
#         keyword=keyword
#     )


# # ================== Login ==================
# @bp.route("/login", methods=["GET", "POST"])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for("main.dashboard"))

#     if request.method == "POST":
#         login_id = request.form.get("login_id")
#         password = request.form.get("password")

#         user = User.query.filter((User.email == login_id) | (User.username == login_id)).first()

#         if user and user.check_password(password):
#             login_user(user)
#             flash(f"Welcome back, {user.username}!", "success")
#             return redirect(url_for("main.dashboard"))
#         else:
#             flash("Login failed. Check username/email and password.", "danger")
#             return redirect(url_for("main.login"))

#     return render_template("login.html")


# # ================== Logout ==================
# @bp.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     flash("You have been logged out.", "info")
#     return redirect(url_for("main.home"))


# # ================== Dashboard ==================
# @bp.route("/dashboard")
# @login_required
# def dashboard():
#     interested_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 5}

#     category_map = {
#         "Technology": "technology",
#         "Sports": "sports",
#         "Health": "health",
#         "Business": "business",
#         "Politics": "politics",
#         "Science": "science",
#         "World": "world"
#     }

#     if interested_area in category_map:
#         params["topic"] = category_map[interested_area]
#     elif interested_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = interested_area

#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         articles = response.json().get("articles", [])
#     except Exception:
#         articles = []

#     analyzed_articles = []
#     for art in articles:
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description
#         nlp_result = analyze_text(content)

#         analyzed_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url"),
#             "image": art.get("image"),
#             "publishedAt": art.get("publishedAt"),
#             "sentiment": nlp_result.get("sentiment", "NEUTRAL"),
#             "sentiment_score": nlp_result.get("sentiment_score"),
#             "entities": nlp_result.get("entities", [])
#         })

#     user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.date_created.desc()).all()
#     return render_template("dashboard.html", username=current_user.username, reports=user_reports, articles=analyzed_articles)


# # ================== Reports ==================
# @bp.route("/reports")
# @login_required
# def reports():
#     reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.date_created.desc()).all()
#     return render_template("reports.html", reports=reports)


# # ================== Generate Report ==================
# @bp.route("/generate_report", methods=["POST"])
# @login_required
# def generate_report():
#     """Generate a detailed report with trending news + NLP analysis using GNews."""
#     selected_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 10}

#     category_map = {
#         "Technology": "technology",
#         "Sports": "sports",
#         "Health": "health",
#         "Business": "business",
#         "Politics": "politics",
#         "Science": "science",
#         "World": "world"
#     }

#     if selected_area in category_map:
#         params["topic"] = category_map[selected_area]
#     elif selected_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = selected_area

#     try:
#         response = requests.get(url, params=params)
#         if response.status_code != 200:
#             try:
#                 error_msg = response.json().get("errors", response.text)
#             except:
#                 error_msg = response.text
#             flash(f"⚠️ GNews Error: {error_msg}", "danger")
#             return redirect(url_for("main.dashboard"))
#         articles = response.json().get("articles", [])
#     except Exception as e:
#         flash(f"⚠️ Exception: {str(e)}", "danger")
#         return redirect(url_for("main.dashboard"))

#     if not articles:
#         flash("No news found for your area. Report not generated.", "warning")
#         return redirect(url_for("main.dashboard"))

#     report_lines = [
#         f"NewsPulse Report for {current_user.username}",
#         f"Generated at: {datetime.utcnow()} UTC",
#         f"Interested Area: {selected_area}",
#         "",
#         "Trending News and Analysis:\n"
#     ]

#     for idx, art in enumerate(articles, start=1):
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description

#         published_at = art.get("publishedAt")
#         if published_at:
#             try:
#                 published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
#                 published_at = published_at.strftime("%d %b %Y, %H:%M UTC")
#             except:
#                 published_at = None

#         nlp_result = analyze_text(content)
#         sentiment = nlp_result.get("sentiment", "NEUTRAL")
#         sentiment_score = nlp_result.get("sentiment_score", None)
#         entities = [ent for ent, _ in nlp_result.get("entities", [])]

#         report_lines.append(f"{idx}. Title: {title}")
#         report_lines.append(f"   Description: {description}")
#         report_lines.append(f"   URL: {art.get('url')}")
#         report_lines.append(f"   Published: {published_at}")
#         report_lines.append(f"   Sentiment: {sentiment} ({sentiment_score})")
#         report_lines.append(f"   Entities: {', '.join(entities) if entities else 'None'}\n")

#     report_text = "\n".join(report_lines)

#     reports_dir = os.path.join(os.getcwd(), "generated_reports")
#     os.makedirs(reports_dir, exist_ok=True)
#     filename = f"report_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.txt"
#     file_path = os.path.join(reports_dir, secure_filename(filename))
#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(report_text)

#     report = Report(
#         user_id=current_user.id,
#         file_path=file_path,
#         text=report_text,
#         sentiment=None,
#         sentiment_score=None,
#         entities=None
#     )
#     db.session.add(report)
#     db.session.commit()

#     flash(f"✅ Detailed report '{filename}' generated successfully!", "success")
#     return redirect(url_for("main.reports"))


# # ================== Download Report ==================
# @bp.route("/download_report/<int:report_id>")
# @login_required
# def download_report(report_id):
#     report = Report.query.get_or_404(report_id)
#     if report.user_id != current_user.id:
#         flash("❌ Unauthorized access!", "danger")
#         return redirect(url_for("main.reports"))
#     return send_file(report.file_path, as_attachment=True)


# # ================== Profile ==================
# @bp.route("/profile", methods=["GET", "POST"])
# @login_required
# def profile():
#     if request.method == "POST":
#         current_user.username = request.form.get("username")
#         current_user.email = request.form.get("email")
#         current_user.interested_area = request.form.get("interested_area")

#         db.session.commit()
#         flash("Profile updated successfully!", "success")
#         return redirect(url_for("main.profile"))

#     return render_template("profile.html")


# import os
# import requests
# from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
# from flask_login import login_user, logout_user, current_user, login_required
# from dotenv import load_dotenv
# from collections import Counter
# from datetime import datetime, timedelta
# from werkzeug.utils import secure_filename

# from . import db
# from .models import User, Report
# from .nlp_utils import analyze_text

# load_dotenv()
# bp = Blueprint("main", __name__)

# # ================== API KEY ==================
# API_KEY = os.getenv("NEWS_API_KEY") or os.getenv("API_KEY")
# if not API_KEY:
#     raise ValueError("❌ Missing API key! Set NEWS_API_KEY or API_KEY in .env")

# # ================== Unified category map ==================
# category_map = {
#     "Technology": "technology",
#     "Sports": "sports",
#     "Health": "health",
#     "Business": "business",
#     "Politics": "politics",
#     "Science": "science",
#     "World": "world"
# }

# # ================== Home ==================
# @bp.route("/")
# def home():
#     return render_template("index.html")

# # ================== Register ==================
# @bp.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form.get("username")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         interested_area = request.form.get("interested_area")

#         if User.query.filter((User.username == username) | (User.email == email)).first():
#             flash("Username or email already exists!", "danger")
#             return redirect(url_for("main.register"))

#         new_user = User(
#             username=username,
#             email=email,
#             interested_area=interested_area
#         )
#         new_user.set_password(password)

#         db.session.add(new_user)
#         db.session.commit()

#         flash("Account created successfully! Please log in.", "success")
#         return redirect(url_for("main.login"))

#     return render_template("register.html")

# # ================== Trending News ==================
# @bp.route("/trending", methods=["GET", "POST"])
# def trending():
#     selected_area = request.form.get("interested_area", "")
#     selected_country = request.form.get("country", "")
#     selected_date = request.form.get("date_filter", "")
#     keyword = request.form.get("keyword", "")

#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 30}

#     # Map category to API
#     if selected_area in category_map:
#         params["topic"] = category_map[selected_area]

#     if selected_country:
#         params["country"] = selected_country

#     # If keyword given → switch to search endpoint
#     if keyword:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = keyword

#     # Date filter warning (free GNews)
#     if selected_date in ["today", "yesterday", "past_week"]:
#         flash("⚠️ Date filtering is not supported in the free GNews API. Showing latest news only.", "warning")

#     try:
#         response = requests.get(url, params=params)
#         if response.status_code != 200:
#             try:
#                 error_msg = response.json().get("errors", response.text)
#             except:
#                 error_msg = response.text
#             flash(f"⚠️ GNews Error: {error_msg}", "danger")
#             return render_template(
#                 "trending.html", articles=[], sentiment_counts={}, entity_counts={},
#                 selected_area=selected_area, selected_country=selected_country,
#                 selected_date=selected_date, keyword=keyword, category_map=category_map
#             )
#         data = response.json()
#     except Exception as e:
#         flash(f"⚠️ Exception: {str(e)}", "danger")
#         return render_template(
#             "trending.html", articles=[], sentiment_counts={}, entity_counts={},
#             selected_area=selected_area, selected_country=selected_country,
#             selected_date=selected_date, keyword=keyword, category_map=category_map
#         )

#     articles = data.get("articles", [])
#     if not articles:
#         flash("No news found for the selected filters.", "warning")

#     enriched_articles = []
#     sentiment_list = []
#     entity_list = []

#     for art in articles:
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description

#         # NLP analysis
#         nlp_result = analyze_text(content)
#         sentiment = nlp_result.get("sentiment", "NEUTRAL")
#         entities = nlp_result.get("entities", [])

#         sentiment_list.append(sentiment)
#         entity_list.extend([ent for ent, _ in entities])

#         published_at = art.get("publishedAt")
#         if published_at:
#             try:
#                 published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
#                 published_at = published_at.strftime("%d %b %Y, %H:%M UTC")
#             except Exception:
#                 published_at = None

#         enriched_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url"),
#             "image": art.get("image"),
#             "sentiment": sentiment,
#             "entities": entities,
#             "published_at": published_at,
#             "source": art.get("source", {}).get("name")
#         })

#     sentiment_counts = Counter(sentiment_list)
#     entity_counts = dict(Counter(entity_list).most_common(10))

#     return render_template(
#         "trending.html",
#         articles=enriched_articles,
#         sentiment_counts=sentiment_counts,
#         entity_counts=entity_counts,
#         selected_area=selected_area,
#         selected_country=selected_country,
#         selected_date=selected_date,
#         keyword=keyword,
#         category_map=category_map
#     )

# # ================== Login ==================
# @bp.route("/login", methods=["GET", "POST"])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for("main.dashboard"))

#     if request.method == "POST":
#         login_id = request.form.get("login_id")
#         password = request.form.get("password")

#         user = User.query.filter((User.email == login_id) | (User.username == login_id)).first()

#         if user and user.check_password(password):
#             login_user(user)
#             flash(f"Welcome back, {user.username}!", "success")
#             return redirect(url_for("main.dashboard"))
#         else:
#             flash("Login failed. Check username/email and password.", "danger")
#             return redirect(url_for("main.login"))

#     return render_template("login.html")

# # ================== Logout ==================
# @bp.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     flash("You have been logged out.", "info")
#     return redirect(url_for("main.home"))

# # ================== Dashboard ==================
# @bp.route("/dashboard")
# @login_required
# def dashboard():
#     interested_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 5}

#     if interested_area in category_map:
#         params["topic"] = category_map[interested_area]
#     elif interested_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = interested_area

#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         articles = response.json().get("articles", [])
#     except Exception:
#         articles = []

#     analyzed_articles = []
#     for art in articles:
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description
#         nlp_result = analyze_text(content)

#         analyzed_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url"),
#             "image": art.get("image"),
#             "publishedAt": art.get("publishedAt"),
#             "sentiment": nlp_result.get("sentiment", "NEUTRAL"),
#             "sentiment_score": nlp_result.get("sentiment_score"),
#             "entities": nlp_result.get("entities", [])
#         })

#     user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.date_created.desc()).all()
#     return render_template("dashboard.html", username=current_user.username, reports=user_reports, articles=analyzed_articles, category_map=category_map)

# # ================== Reports ==================
# @bp.route("/reports")
# @login_required
# def reports():
#     reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.date_created.desc()).all()
#     return render_template("reports.html", reports=reports)

# # ================== Generate Report ==================
# @bp.route("/generate_report", methods=["POST"])
# @login_required
# def generate_report():
#     selected_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 10}

#     if selected_area in category_map:
#         params["topic"] = category_map[selected_area]
#     elif selected_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = selected_area

#     try:
#         response = requests.get(url, params=params)
#         if response.status_code != 200:
#             try:
#                 error_msg = response.json().get("errors", response.text)
#             except:
#                 error_msg = response.text
#             flash(f"⚠️ GNews Error: {error_msg}", "danger")
#             return redirect(url_for("main.dashboard"))
#         articles = response.json().get("articles", [])
#     except Exception as e:
#         flash(f"⚠️ Exception: {str(e)}", "danger")
#         return redirect(url_for("main.dashboard"))

#     if not articles:
#         flash("No news found for your area. Report not generated.", "warning")
#         return redirect(url_for("main.dashboard"))

#     report_lines = [
#         f"NewsPulse Report for {current_user.username}",
#         f"Generated at: {datetime.utcnow()} UTC",
#         f"Interested Area: {selected_area}",
#         "",
#         "Trending News and Analysis:\n"
#     ]

#     for idx, art in enumerate(articles, start=1):
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description

#         published_at = art.get("publishedAt")
#         if published_at:
#             try:
#                 published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
#                 published_at = published_at.strftime("%d %b %Y, %H:%M UTC")
#             except:
#                 published_at = None

#         nlp_result = analyze_text(content)
#         sentiment = nlp_result.get("sentiment", "NEUTRAL")
#         sentiment_score = nlp_result.get("sentiment_score", None)
#         entities = [ent for ent, _ in nlp_result.get("entities", [])]

#         report_lines.append(f"{idx}. Title: {title}")
#         report_lines.append(f"   Description: {description}")
#         report_lines.append(f"   URL: {art.get('url')}")
#         report_lines.append(f"   Published: {published_at}")
#         report_lines.append(f"   Sentiment: {sentiment} ({sentiment_score})")
#         report_lines.append(f"   Entities: {', '.join(entities) if entities else 'None'}\n")

#     report_text = "\n".join(report_lines)

#     reports_dir = os.path.join(os.getcwd(), "generated_reports")
#     os.makedirs(reports_dir, exist_ok=True)
#     filename = f"report_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.txt"
#     file_path = os.path.join(reports_dir, secure_filename(filename))
#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(report_text)

#     report = Report(
#         user_id=current_user.id,
#         file_path=file_path,
#         text=report_text,
#         sentiment=None,
#         sentiment_score=None,
#         entities=None
#     )
#     db.session.add(report)
#     db.session.commit()

#     flash(f"✅ Detailed report '{filename}' generated successfully!", "success")
#     return redirect(url_for("main.reports"))

# # ================== Download Report ==================
# @bp.route("/download_report/<int:report_id>")
# @login_required
# def download_report(report_id):
#     report = Report.query.get_or_404(report_id)
#     if report.user_id != current_user.id:
#         flash("❌ Unauthorized access!", "danger")
#         return redirect(url_for("main.reports"))
#     return send_file(report.file_path, as_attachment=True)

# # ================== Profile ==================
# @bp.route("/profile", methods=["GET", "POST"])
# @login_required
# def profile():
#     if request.method == "POST":
#         current_user.username = request.form.get("username")
#         current_user.email = request.form.get("email")
#         current_user.interested_area = request.form.get("interested_area")
#         db.session.commit()
#         flash("Profile updated successfully!", "success")
#         return redirect(url_for("main.profile"))

#     return render_template("profile.html", category_map=category_map)




# import os
# import requests
# from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
# from flask_login import login_user, logout_user, current_user, login_required
# from dotenv import load_dotenv
# from collections import Counter
# from datetime import datetime
# from werkzeug.utils import secure_filename

# from . import db
# from .models import User, Report
# from .nlp_utils import analyze_text

# load_dotenv()
# bp = Blueprint("main", __name__)

# # ================== API KEY ==================
# API_KEY = os.getenv("NEWS_API_KEY") or os.getenv("API_KEY")
# if not API_KEY:
#     raise ValueError("❌ Missing API key! Set NEWS_API_KEY or API_KEY in .env")

# # ================== Unified category map ==================
# category_map = {
#     "Technology": "technology",
#     "Sports": "sports",
#     "Health": "health",
#     "Business": "business",
#     "Politics": "politics",
#     "Science": "science",
#     "World": "world"
# }

# # ================== GNews helper ==================
# def fetch_gnews(url, params):
#     """Fetch news from GNews API with error handling."""
#     try:
#         response = requests.get(url, params=params)
#         if response.status_code != 200:
#             try:
#                 error_msg = response.json().get("errors", response.text)
#             except:
#                 error_msg = response.text
#             flash(f"⚠️ GNews Error: {error_msg}", "danger")
#             return []
#         return response.json().get("articles", [])
#     except Exception as e:
#         flash(f"⚠️ GNews Exception: {str(e)}", "danger")
#         return []

# # ================== Home ==================
# @bp.route("/")
# def home():
#     return render_template("index.html")

# # ================== Register ==================
# @bp.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form.get("username")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         interested_area = request.form.get("interested_area")

#         if User.query.filter((User.username == username) | (User.email == email)).first():
#             flash("Username or email already exists!", "danger")
#             return redirect(url_for("main.register"))

#         new_user = User(
#             username=username,
#             email=email,
#             interested_area=interested_area
#         )
#         new_user.set_password(password)

#         db.session.add(new_user)
#         db.session.commit()

#         flash("Account created successfully! Please log in.", "success")
#         return redirect(url_for("main.login"))

#     return render_template("register.html", category_map=category_map)

# # ================== Trending News ==================
# @bp.route("/trending", methods=["GET", "POST"])
# def trending():
#     selected_area = request.form.get("interested_area", "")
#     selected_country = request.form.get("country", "")
#     selected_date = request.form.get("date_filter", "")
#     keyword = request.form.get("keyword", "")

#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 30}

#     if selected_area in category_map:
#         params["topic"] = category_map[selected_area]
#     if selected_country:
#         params["country"] = selected_country
#     if keyword:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = keyword
#     if selected_date in ["today", "yesterday", "past_week"]:
#         flash("⚠️ Date filtering is not supported in the free GNews API. Showing latest news only.", "warning")

#     articles = fetch_gnews(url, params)

#     if not articles:
#         flash("No news found for the selected filters.", "warning")

#     enriched_articles = []
#     sentiment_list = []
#     entity_list = []

#     for art in articles:
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description

#         nlp_result = analyze_text(content)
#         sentiment = nlp_result.get("sentiment", "NEUTRAL")
#         entities = nlp_result.get("entities", [])

#         sentiment_list.append(sentiment)
#         entity_list.extend([ent for ent, _ in entities])

#         published_at = art.get("publishedAt")
#         if published_at:
#             try:
#                 published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
#                 published_at = published_at.strftime("%d %b %Y, %H:%M UTC")
#             except:
#                 published_at = None

#         enriched_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url"),
#             "image": art.get("image"),
#             "sentiment": sentiment,
#             "entities": entities,
#             "published_at": published_at,
#             "source": art.get("source", {}).get("name")
#         })

#     sentiment_counts = Counter(sentiment_list)
#     entity_counts = dict(Counter(entity_list).most_common(10))

#     return render_template(
#         "trending.html",
#         articles=enriched_articles,
#         sentiment_counts=sentiment_counts,
#         entity_counts=entity_counts,
#         selected_area=selected_area,
#         selected_country=selected_country,
#         selected_date=selected_date,
#         keyword=keyword,
#         category_map=category_map
#     )

# # ================== Login ==================
# @bp.route("/login", methods=["GET", "POST"])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for("main.dashboard"))

#     if request.method == "POST":
#         login_id = request.form.get("login_id")
#         password = request.form.get("password")

#         user = User.query.filter((User.email == login_id) | (User.username == login_id)).first()

#         if user and user.check_password(password):
#             login_user(user)
#             flash(f"Welcome back, {user.username}!", "success")
#             return redirect(url_for("main.dashboard"))
#         else:
#             flash("Login failed. Check username/email and password.", "danger")
#             return redirect(url_for("main.login"))

#     return render_template("login.html")

# # ================== Logout ==================
# @bp.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     flash("You have been logged out.", "info")
#     return redirect(url_for("main.home"))

# # ================== Dashboard ==================
# @bp.route("/dashboard")
# @login_required
# def dashboard():
#     interested_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 5}

#     if interested_area in category_map:
#         params["topic"] = category_map[interested_area]
#     elif interested_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = interested_area

#     articles = fetch_gnews(url, params)

#     analyzed_articles = []
#     for art in articles:
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description
#         nlp_result = analyze_text(content)

#         analyzed_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url"),
#             "image": art.get("image"),
#             "publishedAt": art.get("publishedAt"),
#             "sentiment": nlp_result.get("sentiment", "NEUTRAL"),
#             "sentiment_score": nlp_result.get("sentiment_score"),
#             "entities": nlp_result.get("entities", [])
#         })

#     user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.date_created.desc()).all()
#     return render_template(
#         "dashboard.html",
#         username=current_user.username,
#         reports=user_reports,
#         articles=analyzed_articles,
#         category_map=category_map
#     )

# # ================== Reports ==================
# @bp.route("/reports")
# @login_required
# def reports():
#     reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.date_created.desc()).all()
#     return render_template("reports.html", reports=reports)

# # ================== Generate Report ==================
# @bp.route("/generate_report", methods=["POST"])
# @login_required
# def generate_report():
#     selected_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 10}

#     if selected_area in category_map:
#         params["topic"] = category_map[selected_area]
#     elif selected_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = selected_area

#     articles = fetch_gnews(url, params)

#     if not articles:
#         flash("No news found for your area. Report not generated.", "warning")
#         return redirect(url_for("main.dashboard"))

#     report_lines = [
#         f"NewsPulse Report for {current_user.username}",
#         f"Generated at: {datetime.utcnow()} UTC",
#         f"Interested Area: {selected_area}",
#         "",
#         "Trending News and Analysis:\n"
#     ]

#     for idx, art in enumerate(articles, start=1):
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description

#         published_at = art.get("publishedAt")
#         if published_at:
#             try:
#                 published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
#                 published_at = published_at.strftime("%d %b %Y, %H:%M UTC")
#             except:
#                 published_at = None

#         nlp_result = analyze_text(content)
#         sentiment = nlp_result.get("sentiment", "NEUTRAL")
#         sentiment_score = nlp_result.get("sentiment_score", None)
#         entities = [ent for ent, _ in nlp_result.get("entities", [])]

#         report_lines.append(f"{idx}. Title: {title}")
#         report_lines.append(f"   Description: {description}")
#         report_lines.append(f"   URL: {art.get('url')}")
#         report_lines.append(f"   Published: {published_at}")
#         report_lines.append(f"   Sentiment: {sentiment} ({sentiment_score})")
#         report_lines.append(f"   Entities: {', '.join(entities) if entities else 'None'}\n")

#     report_text = "\n".join(report_lines)

#     reports_dir = os.path.join(os.getcwd(), "generated_reports")
#     os.makedirs(reports_dir, exist_ok=True)
#     filename = f"report_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.txt"
#     file_path = os.path.join(reports_dir, secure_filename(filename))
#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(report_text)

#     report = Report(
#         user_id=current_user.id,
#         file_path=file_path,
#         text=report_text
#     )
#     db.session.add(report)
#     db.session.commit()

#     flash(f"✅ Detailed report '{filename}' generated successfully!", "success")
#     return redirect(url_for("main.reports"))

# # ================== Download Report ==================
# @bp.route("/download_report/<int:report_id>")
# @login_required
# def download_report(report_id):
#     report = Report.query.get_or_404(report_id)
#     if report.user_id != current_user.id:
#         flash("❌ Unauthorized access!", "danger")
#         return redirect(url_for("main.reports"))
#     return send_file(report.file_path, as_attachment=True)

# # ================== Profile ==================
# @bp.route("/profile", methods=["GET", "POST"])
# @login_required
# def profile():
#     if request.method == "POST":
#         current_user.username = request.form.get("username")
#         current_user.email = request.form.get("email")
#         current_user.interested_area = request.form.get("interested_area")
#         db.session.commit()
#         flash("Profile updated successfully!", "success")
#         return redirect(url_for("main.profile"))

#     return render_template("profile.html", category_map=category_map)


# import os
# import requests
# from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
# from flask_login import login_user, logout_user, current_user, login_required
# from dotenv import load_dotenv
# from collections import Counter
# from datetime import datetime, timedelta
# from werkzeug.utils import secure_filename

# from . import db
# from .models import User, Report
# from .nlp_utils import analyze_text

# load_dotenv()
# bp = Blueprint("main", __name__)

# # ================== API KEY ==================
# API_KEY = os.getenv("NEWS_API_KEY") or os.getenv("API_KEY")
# if not API_KEY:
#     raise ValueError("❌ Missing API key! Set NEWS_API_KEY or API_KEY in .env")

# # ================== Category map ==================
# category_map = {
#     "Technology": "technology",
#     "Sports": "sports",
#     "Health": "health",
#     "Business": "business",
#     "Politics": "politics",
#     "Science": "science",
#     "World": "world",
#     "Entertainment": "entertainment"  # New category
# }

# # ================== GNews helper ==================
# def fetch_gnews(url, params):
#     try:
#         response = requests.get(url, params=params)
#         if response.status_code != 200:
#             try:
#                 error_msg = response.json().get("errors", response.text)
#             except:
#                 error_msg = response.text
#             flash(f"⚠️ GNews Error: {error_msg}", "danger")
#             return []
#         return response.json().get("articles", [])
#     except Exception as e:
#         flash(f"⚠️ GNews Exception: {str(e)}", "danger")
#         return []

# # ================== Home ==================
# @bp.route("/")
# def home():
#     return render_template("index.html", category_map=category_map)

# # ================== Register ==================
# @bp.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form.get("username")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         interested_area = request.form.get("interested_area")

#         if User.query.filter((User.username == username) | (User.email == email)).first():
#             flash("Username or email already exists!", "danger")
#             return redirect(url_for("main.register"))

#         new_user = User(
#             username=username,
#             email=email,
#             interested_area=interested_area
#         )
#         new_user.set_password(password)
#         db.session.add(new_user)
#         db.session.commit()

#         flash("Account created successfully! Please log in.", "success")
#         return redirect(url_for("main.login"))

#     return render_template("register.html", category_map=category_map)

# # ================== Trending News ==================
# @bp.route("/trending", methods=["GET", "POST"])
# def trending():
#     selected_area = request.form.get("interested_area", "")
#     selected_country = request.form.get("country", "")
#     selected_date = request.form.get("date_filter", "")
#     keyword = request.form.get("keyword", "")

#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 30}

#     if selected_area in category_map:
#         params["topic"] = category_map[selected_area]
#     if selected_country:
#         params["country"] = selected_country
#     if keyword:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = keyword

#     articles = fetch_gnews(url, params)
#     if not articles:
#         flash("No news found for the selected filters.", "warning")

#     # ================== Date filtering ==================
#     now = datetime.utcnow()
#     if selected_date == "last_few_hours":
#         threshold = now - timedelta(hours=6)
#     elif selected_date == "today":
#         threshold = datetime(now.year, now.month, now.day)
#     elif selected_date == "yesterday":
#         threshold = datetime(now.year, now.month, now.day) - timedelta(days=1)
#     elif selected_date == "past_week":
#         threshold = now - timedelta(days=7)
#     else:
#         threshold = None

#     enriched_articles = []
#     sentiment_list = []
#     entity_list = []

#     for art in articles:
#         published_at_raw = art.get("publishedAt")
#         if published_at_raw:
#             try:
#                 published_at_dt = datetime.strptime(published_at_raw, "%Y-%m-%dT%H:%M:%SZ")
#                 if threshold and published_at_dt < threshold:
#                     continue
#                 published_at = published_at_dt.strftime("%d %b %Y, %H:%M UTC")
#             except:
#                 published_at = None
#         else:
#             published_at = None

#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description

#         nlp_result = analyze_text(content)
#         sentiment = nlp_result.get("sentiment", "NEUTRAL")
#         entities = nlp_result.get("entities", [])

#         sentiment_list.append(sentiment)
#         entity_list.extend([ent for ent, _ in entities])

#         enriched_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url"),
#             "image": art.get("image"),
#             "sentiment": sentiment,
#             "entities": entities,
#             "published_at": published_at,
#             "source": art.get("source", {}).get("name")
#         })

#     # ================== Sentiment counts ==================
#     sentiment_counts_raw = Counter(sentiment_list)
#     total = sum(sentiment_counts_raw.values()) or 1
#     sentiment_counts = {k: v / total for k, v in sentiment_counts_raw.items()}  # normalized for charts
#     entity_counts = dict(Counter(entity_list).most_common(10))

#     return render_template(
#         "trending.html",
#         articles=enriched_articles,
#         sentiment_counts=sentiment_counts,
#         entity_counts=entity_counts,
#         selected_area=selected_area,
#         selected_country=selected_country,
#         selected_date=selected_date,
#         keyword=keyword,
#         category_map=category_map
#     )

# # ================== Login ==================
# @bp.route("/login", methods=["GET", "POST"])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for("main.dashboard"))

#     if request.method == "POST":
#         login_id = request.form.get("login_id")
#         password = request.form.get("password")
#         user = User.query.filter((User.email == login_id) | (User.username == login_id)).first()

#         if user and user.check_password(password):
#             login_user(user)
#             flash(f"Welcome back, {user.username}!", "success")
#             return redirect(url_for("main.dashboard"))
#         else:
#             flash("Login failed. Check username/email and password.", "danger")
#             return redirect(url_for("main.login"))

#     return render_template("login.html")

# # ================== Logout ==================
# @bp.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     flash("You have been logged out.", "info")
#     return redirect(url_for("main.home"))

# # ================== Dashboard ==================
# @bp.route("/dashboard")
# @login_required
# def dashboard():
#     interested_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 5}

#     if interested_area in category_map:
#         params["topic"] = category_map[interested_area]
#     elif interested_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = interested_area

#     articles = fetch_gnews(url, params)
#     analyzed_articles = []

#     for art in articles:
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description
#         nlp_result = analyze_text(content)
#         analyzed_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url"),
#             "image": art.get("image"),
#             "publishedAt": art.get("publishedAt"),
#             "sentiment": nlp_result.get("sentiment", "NEUTRAL"),
#             "sentiment_score": nlp_result.get("sentiment_score"),
#             "entities": nlp_result.get("entities", [])
#         })

#     user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.date_created.desc()).all()
#     return render_template(
#         "dashboard.html",
#         username=current_user.username,
#         reports=user_reports,
#         articles=analyzed_articles,
#         category_map=category_map
#     )

# # ================== Reports ==================
# @bp.route("/reports")
# @login_required
# def reports():
#     reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.date_created.desc()).all()
#     return render_template("reports.html", reports=reports)

# # ================== Generate Report ==================
# @bp.route("/generate_report", methods=["POST"])
# @login_required
# def generate_report():
#     selected_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 10}

#     if selected_area in category_map:
#         params["topic"] = category_map[selected_area]
#     elif selected_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = selected_area

#     articles = fetch_gnews(url, params)
#     if not articles:
#         flash("No news found for your area. Report not generated.", "warning")
#         return redirect(url_for("main.dashboard"))

#     report_lines = [
#         f"NewsPulse Report for {current_user.username}",
#         f"Generated at: {datetime.utcnow()} UTC",
#         f"Interested Area: {selected_area}",
#         "",
#         "Trending News and Analysis:\n"
#     ]

#     for idx, art in enumerate(articles, start=1):
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = title + " " + description

#         published_at = art.get("publishedAt")
#         if published_at:
#             try:
#                 published_at_dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
#                 published_at = published_at_dt.strftime("%d %b %Y, %H:%M UTC")
#             except:
#                 published_at = None

#         nlp_result = analyze_text(content)
#         sentiment = nlp_result.get("sentiment", "NEUTRAL")
#         sentiment_score = nlp_result.get("sentiment_score", None)
#         entities = [ent for ent, _ in nlp_result.get("entities", [])]

#         report_lines.append(f"{idx}. Title: {title}")
#         report_lines.append(f"   Description: {description}")
#         report_lines.append(f"   URL: {art.get('url')}")
#         report_lines.append(f"   Published: {published_at}")
#         report_lines.append(f"   Sentiment: {sentiment} ({sentiment_score})")
#         report_lines.append(f"   Entities: {', '.join(entities) if entities else 'None'}\n")

#     report_text = "\n".join(report_lines)
#     reports_dir = os.path.join(os.getcwd(), "generated_reports")
#     os.makedirs(reports_dir, exist_ok=True)
#     filename = f"report_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.txt"
#     file_path = os.path.join(reports_dir, secure_filename(filename))
#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(report_text)

#     report = Report(user_id=current_user.id, file_path=file_path, text=report_text)
#     db.session.add(report)
#     db.session.commit()
#     flash(f"✅ Detailed report '{filename}' generated successfully!", "success")
#     return redirect(url_for("main.reports"))

# # ================== Download Report ==================
# @bp.route("/download_report/<int:report_id>")
# @login_required
# def download_report(report_id):
#     report = Report.query.get_or_404(report_id)
#     if report.user_id != current_user.id:
#         flash("❌ Unauthorized access!", "danger")
#         return redirect(url_for("main.reports"))
#     return send_file(report.file_path, as_attachment=True)

# # ================== Profile ==================
# @bp.route("/profile", methods=["GET", "POST"])
# @login_required
# def profile():
#     if request.method == "POST":
#         current_user.username = request.form.get("username")
#         current_user.email = request.form.get("email")
#         current_user.interested_area = request.form.get("interested_area")
#         db.session.commit()
#         flash("Profile updated successfully!", "success")
#         return redirect(url_for("main.profile"))

#     return render_template("profile.html", category_map=category_map)









# import os
# import requests
# from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
# from flask_login import login_user, logout_user, current_user, login_required
# from dotenv import load_dotenv
# from collections import Counter
# from datetime import datetime, timedelta
# from werkzeug.utils import secure_filename

# from . import db
# from .models import User, Report
# from .nlp_utils import analyze_text

# load_dotenv()
# bp = Blueprint("main", __name__)

# # ================== API KEY ==================
# API_KEY = os.getenv("NEWS_API_KEY") or os.getenv("API_KEY")
# if not API_KEY:
#     raise ValueError("❌ Missing API key! Set NEWS_API_KEY or API_KEY in .env")

# # ================== Category map ==================
# category_map = {
#     "Technology": "technology",
#     "Sports": "sports",
#     "Health": "health",
#     "Business": "business",
#     "Politics": "politics",
#     "Science": "science",
#     "World": "world",
#     "Entertainment": "entertainment"
# }

# # ================== GNews helper ==================
# def fetch_gnews(url, params):
#     try:
#         response = requests.get(url, params=params)
#         if response.status_code != 200:
#             try:
#                 error_msg = response.json().get("errors", response.text)
#             except:
#                 error_msg = response.text
#             flash(f"⚠️ GNews Error: {error_msg}", "danger")
#             return []
#         return response.json().get("articles", [])
#     except Exception as e:
#         flash(f"⚠️ GNews Exception: {str(e)}", "danger")
#         return []

# # ================== Home ==================
# @bp.route("/")
# def home():
#     return render_template("index.html", category_map=category_map)

# # ================== Register ==================
# @bp.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form.get("username")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         interested_area = request.form.get("interested_area")

#         if User.query.filter((User.username == username) | (User.email == email)).first():
#             flash("Username or email already exists!", "danger")
#             return redirect(url_for("main.register"))

#         new_user = User(
#             username=username,
#             email=email,
#             interested_area=interested_area
#         )
#         new_user.set_password(password)
#         db.session.add(new_user)
#         db.session.commit()

#         flash("Account created successfully! Please log in.", "success")
#         return redirect(url_for("main.login"))

#     return render_template("register.html", category_map=category_map)

# # ================== Trending News ==================
# # @bp.route("/trending", methods=["GET", "POST"])
# # def trending():
# #     selected_area = request.form.get("interested_area", "")
# #     selected_country = request.form.get("country", "")
# #     selected_date = request.form.get("date_filter", "")
# #     keyword = request.form.get("keyword", "")

# #     url = "https://gnews.io/api/v4/top-headlines"
# #     params = {"token": API_KEY, "lang": "en", "max": 30}

# #     if selected_area in category_map:
# #         params["topic"] = category_map[selected_area]
# #     if selected_country:
# #         params["country"] = selected_country
# #     if keyword:
# #         url = "https://gnews.io/api/v4/search"
# #         params["q"] = keyword

# #     articles = fetch_gnews(url, params)
# #     if not articles:
# #         flash("No news found for the selected filters.", "warning")

# # @bp.route("/trending", methods=["GET", "POST"])
# # def trending():
# #     selected_area = request.form.get("interested_area", "None")
# #     selected_country = request.form.get("country", "None")
# #     selected_date = request.form.get("date_filter", "None")
# #     keyword = request.form.get("keyword", "")

# #     url = "https://gnews.io/api/v4/top-headlines"
# #     params = {"token": API_KEY, "lang": "en", "max": 30}

# #     if selected_area != "None" and selected_area in category_map:
# #         params["topic"] = category_map[selected_area]
# #     if selected_country != "None" and selected_country:
# #         params["country"] = selected_country
# #     if keyword:
# #         url = "https://gnews.io/api/v4/search"
# #         params["q"] = keyword

# #     articles = fetch_gnews(url, params)
# #     if not articles:
# #         flash("No news found for the selected filters.", "warning")

# #     # Date filtering
# #     now = datetime.utcnow()
# #     threshold = None
# #     if selected_date == "last_few_hours":
# #         threshold = now - timedelta(hours=6)
# #     elif selected_date == "today":
# #         threshold = datetime(now.year, now.month, now.day)
# #     elif selected_date == "yesterday":
# #         threshold = datetime(now.year, now.month, now.day) - timedelta(days=1)
# #     elif selected_date == "past_week":
# #         threshold = now - timedelta(days=7)

# #     enriched_articles = []
# #     sentiment_list = []
# #     entity_list = []

# #     for art in articles:
# #         published_at_raw = art.get("publishedAt")
# #         if published_at_raw:
# #             try:
# #                 published_at_dt = datetime.strptime(published_at_raw, "%Y-%m-%dT%H:%M:%SZ")
# #                 # Skip if older than threshold
# #                 if threshold and published_at_dt < threshold:
# #                     continue
# #                 # Convert to India time
# #                 published_at_dt += timedelta(hours=5, minutes=30)
# #                 published_at = published_at_dt.strftime("%d %b %Y, %H:%M IST")
# #             except:
# #                 published_at = "None"
# #         else:
# #             published_at = "None"

# #         title = art.get("title") or "None"
# #         description = art.get("description") or "None"
# #         content = title + " " + description

# #         nlp_result = analyze_text(content)
# #         sentiment = nlp_result.get("sentiment", "Neutral")
# #         entities = nlp_result.get("entities", [])
# #         if not entities:
# #             entities = [("None", "None")]

# #         sentiment_list.append(sentiment)
# #         entity_list.extend([ent for ent, _ in entities])

# #         enriched_articles.append({
# #             "title": title,
# #             "description": description,
# #             "url": art.get("url"),
# #             "image": art.get("image"),
# #             "sentiment": sentiment,
# #             "entities": entities,
# #             "published_at": published_at,
# #             "source": art.get("source", {}).get("name", "None")
# #         })

# #     # Sentiment chart (normalized)
# #     sentiment_counts_raw = Counter(sentiment_list)
# #     total = sum(sentiment_counts_raw.values()) or 1
# #     sentiment_counts = {k: v for k, v in sentiment_counts_raw.items()}

# #     # Entity chart
# #     entity_counts = dict(Counter(entity_list).most_common(10))
# #     if not entity_counts:
# #         entity_counts = {"None": 1}

# #     return render_template(
# #         "trending.html",
# #         articles=enriched_articles,
# #         sentiment_counts=sentiment_counts,
# #         entity_counts=entity_counts,
# #         selected_area=selected_area,
# #         selected_country=selected_country,
# #         selected_date=selected_date,
# #         keyword=keyword,
# #         category_map=category_map
# #     )

# #     # ================== Date filtering ==================
# #     now = datetime.utcnow()
# #     if selected_date == "last_few_hours":
# #         threshold = now - timedelta(hours=6)
# #     elif selected_date == "today":
# #         threshold = datetime(now.year, now.month, now.day)
# #     elif selected_date == "yesterday":
# #         threshold = datetime(now.year, now.month, now.day) - timedelta(days=1)
# #     elif selected_date == "past_week":
# #         threshold = now - timedelta(days=7)
# #     else:
# #         threshold = None

# #     enriched_articles = []
# #     sentiment_list = []
# #     entity_list = []

# #     for art in articles:
# #         published_at_raw = art.get("publishedAt")
# #         if published_at_raw:
# #             try:
# #                 published_at_dt = datetime.strptime(published_at_raw, "%Y-%m-%dT%H:%M:%SZ")
# #                 if threshold and published_at_dt < threshold:
# #                     continue
# #                 # Convert to IST
# #                 published_at_dt += timedelta(hours=5, minutes=30)
# #                 published_at = published_at_dt.strftime("%d %b %Y, %H:%M IST")
# #             except:
# #                 published_at = "None"
# #         else:
# #             published_at = "None"

# #         title = art.get("title") or "None"
# #         description = art.get("description") or "None"
# #         url_link = art.get("url") or "#"
# #         image = art.get("image") or ""
# #         source = art.get("source", {}).get("name") or "None"

# #         content = title + " " + description
# #         nlp_result = analyze_text(content)
# #         sentiment = nlp_result.get("sentiment", "None")
# #         entities = nlp_result.get("entities", [])
# #         sentiment_list.append(sentiment if sentiment else "None")
# #         entity_list.extend([ent for ent, _ in entities] or ["None"])

# #         enriched_articles.append({
# #             "title": title,
# #             "description": description,
# #             "url": url_link,
# #             "image": image,
# #             "sentiment": sentiment,
# #             "entities": entities if entities else [("None", "None")],
# #             "published_at": published_at,
# #             "source": source
# #         })

# #     # Normalize sentiment for charts
# #     sentiment_counts_raw = Counter(sentiment_list)
# #     total = sum(sentiment_counts_raw.values()) or 1
# #     sentiment_counts = {k: v / total for k, v in sentiment_counts_raw.items()}
# #     for s in ["Positive","Neutral","Negative","None"]:
# #         if s not in sentiment_counts:
# #             sentiment_counts[s] = 0

# #     entity_counts = dict(Counter(entity_list).most_common(10))

# #     return render_template(
# #         "trending.html",
# #         articles=enriched_articles,
# #         sentiment_counts=sentiment_counts,
# #         entity_counts=entity_counts,
# #         selected_area=selected_area,
# #         selected_country=selected_country,
# #         selected_date=selected_date,
# #         keyword=keyword,
# #         category_map=category_map
# #     )


# # @bp.route("/trending", methods=["GET", "POST"])
# # def trending():
# #     selected_area = request.form.get("interested_area", "None")
# #     selected_country = request.form.get("country", "None")
# #     selected_date = request.form.get("date_filter", "None")
# #     keyword = request.form.get("keyword", "")

# #     url = "https://gnews.io/api/v4/top-headlines"
# #     params = {"token": API_KEY, "lang": "en", "max": 30}

# #     if selected_area != "None" and selected_area in category_map:
# #         params["topic"] = category_map[selected_area]
# #     if selected_country != "None" and selected_country:
# #         params["country"] = selected_country
# #     if keyword:
# #         url = "https://gnews.io/api/v4/search"
# #         params["q"] = keyword

# #     articles = fetch_gnews(url, params)
# #     if not articles:
# #         flash("No news found for the selected filters.", "warning")

# #     # ================== Date filtering ==================
# #     now = datetime.utcnow()
# #     threshold = None
# #     if selected_date == "last_hours":
# #         threshold = now - timedelta(hours=6)
# #     elif selected_date == "today":
# #         threshold = datetime(now.year, now.month, now.day)
# #     elif selected_date == "yesterday":
# #         threshold = datetime(now.year, now.month, now.day) - timedelta(days=1)
# #     elif selected_date == "past_week":
# #         threshold = now - timedelta(days=7)

# #     enriched_articles = []
# #     sentiment_list = []
# #     entity_list = []

# #     for art in articles:
# #         published_at_raw = art.get("publishedAt")
# #         if published_at_raw:
# #             try:
# #                 published_at_dt = datetime.strptime(published_at_raw, "%Y-%m-%dT%H:%M:%SZ")
# #                 if threshold and published_at_dt < threshold:
# #                     continue
# #                 # Convert to IST
# #                 published_at_dt += timedelta(hours=5, minutes=30)
# #                 published_at = published_at_dt.strftime("%d %b %Y, %H:%M IST")
# #             except:
# #                 published_at = "None"
# #         else:
# #             published_at = "None"

# #         title = art.get("title") or "None"
# #         description = art.get("description") or "None"
# #         url_link = art.get("url") or "#"
# #         image = art.get("image") or ""
# #         source = art.get("source", {}).get("name") or "None"

# #         content = title + " " + description
# #         nlp_result = analyze_text(content)
# #         sentiment = nlp_result.get("sentiment", "None")
# #         entities = nlp_result.get("entities", [])

# #         sentiment_list.append(sentiment if sentiment else "None")
# #         entity_list.extend([ent for ent, _ in entities] if entities else ["None"])

# #         enriched_articles.append({
# #             "title": title,
# #             "description": description,
# #             "url": url_link,
# #             "image": image,
# #             "sentiment": sentiment,
# #             "entities": entities if entities else [("None", "None")],
# #             "published_at": published_at,
# #             "source": source
# #         })

# #     # ================== Prepare charts ==================
# #     sentiment_counts_raw = Counter(sentiment_list)
# #     sentiment_counts = {
# #         "Positive": sentiment_counts_raw.get("Positive", 0),
# #         "Neutral": sentiment_counts_raw.get("Neutral", 0),
# #         "Negative": sentiment_counts_raw.get("Negative", 0),
# #         "None": sentiment_counts_raw.get("None", 0)
# #     }

# #     entity_counts = dict(Counter(entity_list).most_common(10))
# #     if not entity_counts:
# #         entity_counts = {"None": 1}

# #     return render_template(
# #         "trending.html",
# #         articles=enriched_articles,
# #         sentiment_counts=sentiment_counts,
# #         entity_counts=entity_counts,
# #         selected_area=selected_area,
# #         selected_country=selected_country,
# #         selected_date=selected_date,
# #         keyword=keyword,
# #         category_map=category_map
# #     )

# # @bp.route("/trending", methods=["GET", "POST"])
# # def trending():
# #     selected_area = request.form.get("interested_area", "None")
# #     selected_country = request.form.get("country", "None")
# #     selected_date = request.form.get("date_filter", "None")
# #     keyword = request.form.get("keyword", "")

# #     url = "https://gnews.io/api/v4/top-headlines"
# #     params = {"token": API_KEY, "lang": "en", "max": 30}

# #     if selected_area != "None" and selected_area in category_map:
# #         params["topic"] = category_map[selected_area]
# #     if selected_country != "None":
# #         params["country"] = selected_country
# #     if keyword:
# #         url = "https://gnews.io/api/v4/search"
# #         params["q"] = keyword

# #     articles = fetch_gnews(url, params)
# #     if not articles:
# #         flash("No news found for the selected filters.", "warning")

# #     # Date filtering
# #     now = datetime.utcnow()
# #     threshold = None
# #     if selected_date == "last_hours":
# #         threshold = now - timedelta(hours=6)
# #     elif selected_date == "today":
# #         threshold = datetime(now.year, now.month, now.day)
# #     elif selected_date == "yesterday":
# #         threshold = datetime(now.year, now.month, now.day) - timedelta(days=1)
# #     elif selected_date == "past_week":
# #         threshold = now - timedelta(days=7)

# #     enriched_articles = []
# #     sentiment_list = []
# #     entity_list = []

# #     for art in articles:
# #         published_at_raw = art.get("publishedAt")
# #         if published_at_raw:
# #             try:
# #                 published_at_dt = datetime.strptime(published_at_raw, "%Y-%m-%dT%H:%M:%SZ")
# #                 if threshold and published_at_dt < threshold:
# #                     continue
# #                 published_at_dt += timedelta(hours=5, minutes=30)  # IST
# #                 published_at = published_at_dt.strftime("%d %b %Y, %H:%M IST")
# #             except:
# #                 published_at = "None"
# #         else:
# #             published_at = "None"

# #         title = art.get("title") or "None"
# #         description = art.get("description") or "None"
# #         content = title + " " + description

# #         nlp_result = analyze_text(content)
# #         sentiment = nlp_result.get("sentiment", "None")
# #         entities = nlp_result.get("entities", [])
# #         if not entities:
# #             entities = [("None", "None")]

# #         sentiment_list.append(sentiment if sentiment else "None")
# #         entity_list.extend([ent for ent, _ in entities] or ["None"])

# #         enriched_articles.append({
# #             "title": title,
# #             "description": description,
# #             "url": art.get("url") or "#",
# #             "image": art.get("image") or "",
# #             "sentiment": sentiment,
# #             "entities": entities,
# #             "published_at": published_at,
# #             "source": art.get("source", {}).get("name") or "None"
# #         })

# #     # Ensure all sentiment keys exist for chart
# #     sentiment_counts_raw = Counter(sentiment_list)
# #     sentiment_counts = {
# #         "Positive": sentiment_counts_raw.get("Positive", 0),
# #         "Neutral": sentiment_counts_raw.get("Neutral", 0),
# #         "Negative": sentiment_counts_raw.get("Negative", 0),
# #         "None": sentiment_counts_raw.get("None", 0)
# #     }

# #     # Top 10 entities for chart
# #     entity_counts = dict(Counter(entity_list).most_common(10))
# #     if not entity_counts:
# #         entity_counts = {"None": 1}

# #     return render_template(
# #         "trending.html",
# #         articles=enriched_articles,
# #         sentiment_counts=sentiment_counts,
# #         entity_counts=entity_counts,
# #         selected_area=selected_area,
# #         selected_country=selected_country,
# #         selected_date=selected_date,
# #         keyword=keyword,
# #         category_map=category_map
# #     )


# @bp.route("/trending", methods=["GET", "POST"])
# def trending():
#     selected_area = request.form.get("interested_area", "None")
#     selected_country = request.form.get("country", "None")
#     selected_date = request.form.get("date_filter", "None")
#     keyword = request.form.get("keyword", "")

#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 30}

#     if selected_area != "None" and selected_area in category_map:
#         params["topic"] = category_map[selected_area]
#     if selected_country != "None":
#         params["country"] = selected_country
#     if keyword:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = keyword

#     articles = fetch_gnews(url, params)
#     if not articles:
#         flash("No news found for the selected filters.", "warning")

#     # Date filtering
#     now = datetime.utcnow()
#     threshold = None
#     if selected_date == "last_hours":
#         threshold = now - timedelta(hours=6)
#     elif selected_date == "today":
#         threshold = datetime(now.year, now.month, now.day)
#     elif selected_date == "yesterday":
#         threshold = datetime(now.year, now.month, now.day) - timedelta(days=1)
#     elif selected_date == "past_week":
#         threshold = now - timedelta(days=7)

#     enriched_articles = []
#     sentiment_list = []
#     entity_list = []

#     for art in articles:
#         published_at_raw = art.get("publishedAt")
#         if published_at_raw:
#             try:
#                 published_at_dt = datetime.strptime(published_at_raw, "%Y-%m-%dT%H:%M:%SZ")
#                 if threshold and published_at_dt < threshold:
#                     continue
#                 published_at_dt += timedelta(hours=5, minutes=30)  # IST
#                 published_at = published_at_dt.strftime("%d %b %Y, %H:%M IST")
#             except:
#                 published_at = "None"
#         else:
#             published_at = "None"

#         title = art.get("title") or "None"
#         description = art.get("description") or "None"
#         content = title + " " + description

#         nlp_result = analyze_text(content)
#         sentiment = nlp_result.get("sentiment", "None")
#         entities = nlp_result.get("entities", [])
#         if not entities:
#             entities = [("None", "None")]

#         sentiment_list.append(sentiment if sentiment else "None")
#         entity_list.extend([ent for ent, _ in entities] or ["None"])

#         enriched_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url") or "#",
#             "image": art.get("image") or "",
#             "sentiment": sentiment,
#             "entities": entities,
#             "published_at": published_at,
#             "source": art.get("source", {}).get("name") or "None"
#         })

#     # Ensure all sentiment keys exist for chart
#     sentiment_counts_raw = Counter(sentiment_list)
#     sentiment_counts = {
#         "Positive": int(sentiment_counts_raw.get("Positive", 0)),
#         "Neutral": int(sentiment_counts_raw.get("Neutral", 0)),
#         "Negative": int(sentiment_counts_raw.get("Negative", 0)),
#         "None": int(sentiment_counts_raw.get("None", 0))
#     }

#     # Top 10 entities for chart
#     entity_counts = dict(Counter(entity_list).most_common(10))
#     if not entity_counts:
#         entity_counts = {"None": 1}

#     return render_template(
#         "trending.html",
#         articles=enriched_articles,
#         sentiment_counts=sentiment_counts,
#         entity_counts=entity_counts,
#         selected_area=selected_area,
#         selected_country=selected_country,
#         selected_date=selected_date,
#         keyword=keyword,
#         category_map=category_map
#     )


# # ================== Login ==================
# @bp.route("/login", methods=["GET", "POST"])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for("main.dashboard"))

#     if request.method == "POST":
#         login_id = request.form.get("login_id")
#         password = request.form.get("password")
#         user = User.query.filter((User.email == login_id) | (User.username == login_id)).first()

#         if user and user.check_password(password):
#             login_user(user)
#             flash(f"Welcome back, {user.username}!", "success")
#             return redirect(url_for("main.dashboard"))
#         else:
#             flash("Login failed. Check username/email and password.", "danger")
#             return redirect(url_for("main.login"))

#     return render_template("login.html")

# # ================== Logout ==================
# @bp.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     flash("You have been logged out.", "info")
#     return redirect(url_for("main.home"))

# # ================== Dashboard ==================
# @bp.route("/dashboard")
# @login_required
# def dashboard():
#     interested_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 5}

#     if interested_area in category_map:
#         params["topic"] = category_map[interested_area]
#     elif interested_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = interested_area

#     articles = fetch_gnews(url, params)
#     analyzed_articles = []

#     for art in articles:
#         title = art.get("title") or "None"
#         description = art.get("description") or "None"
#         content = title + " " + description
#         nlp_result = analyze_text(content)
#         analyzed_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url") or "#",
#             "image": art.get("image") or "",
#             "publishedAt": art.get("publishedAt") or "None",
#             "sentiment": nlp_result.get("sentiment", "None"),
#             "sentiment_score": nlp_result.get("sentiment_score"),
#             "entities": nlp_result.get("entities", []) or [("None","None")]
#         })

#     user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.date_created.desc()).all()
#     return render_template(
#         "dashboard.html",
#         username=current_user.username,
#         reports=user_reports,
#         articles=analyzed_articles,
#         category_map=category_map
#     )

# # ================== Reports ==================
# @bp.route("/reports")
# @login_required
# def reports():
#     reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.date_created.desc()).all()
#     return render_template("reports.html", reports=reports)

# # ================== Generate Report ==================
# @bp.route("/generate_report", methods=["POST"])
# @login_required
# def generate_report():
#     selected_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 10}

#     if selected_area in category_map:
#         params["topic"] = category_map[selected_area]
#     elif selected_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = selected_area

#     articles = fetch_gnews(url, params)
#     if not articles:
#         flash("No news found for your area. Report not generated.", "warning")
#         return redirect(url_for("main.dashboard"))

#     report_lines = [
#         f"NewsPulse Report for {current_user.username}",
#         f"Generated at: {datetime.utcnow()} UTC",
#         f"Interested Area: {selected_area}",
#         "",
#         "Trending News and Analysis:\n"
#     ]

#     for idx, art in enumerate(articles, start=1):
#         title = art.get("title") or "None"
#         description = art.get("description") or "None"
#         content = title + " " + description

#         published_at = art.get("publishedAt")
#         if published_at:
#             try:
#                 published_at_dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
#                 published_at = published_at_dt.strftime("%d %b %Y, %H:%M UTC")
#             except:
#                 published_at = "None"
#         else:
#             published_at = "None"

#         nlp_result = analyze_text(content)
#         sentiment = nlp_result.get("sentiment", "None")
#         sentiment_score = nlp_result.get("sentiment_score", None)
#         entities = [ent for ent, _ in nlp_result.get("entities", [])] or ["None"]

#         report_lines.append(f"{idx}. Title: {title}")
#         report_lines.append(f"   Description: {description}")
#         report_lines.append(f"   URL: {art.get('url') or '#'}")
#         report_lines.append(f"   Published: {published_at}")
#         report_lines.append(f"   Sentiment: {sentiment} ({sentiment_score})")
#         report_lines.append(f"   Entities: {', '.join(entities)}\n")

#     report_text = "\n".join(report_lines)
#     reports_dir = os.path.join(os.getcwd(), "generated_reports")
#     os.makedirs(reports_dir, exist_ok=True)
#     filename = f"report_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.txt"
#     file_path = os.path.join(reports_dir, secure_filename(filename))
#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(report_text)

#     report = Report(user_id=current_user.id, file_path=file_path, text=report_text)
#     db.session.add(report)
#     db.session.commit()
#     flash(f"✅ Detailed report '{filename}' generated successfully!", "success")
#     return redirect(url_for("main.reports"))

# # ================== Download Report ==================
# @bp.route("/download_report/<int:report_id>")
# @login_required
# def download_report(report_id):
#     report = Report.query.get_or_404(report_id)
#     if report.user_id != current_user.id:
#         flash("❌ Unauthorized access!", "danger")
#         return redirect(url_for("main.reports"))
#     return send_file(report.file_path, as_attachment=True)

# # ================== Profile ==================
# @bp.route("/profile", methods=["GET", "POST"])
# @login_required
# def profile():
#     if request.method == "POST":
#         current_user.username = request.form.get("username")
#         current_user.email = request.form.get("email")
#         current_user.interested_area = request.form.get("interested_area")
#         db.session.commit()
#         flash("Profile updated successfully!", "success")
#         return redirect(url_for("main.profile"))

#     return render_template("profile.html", category_map=category_map)
# import os
# import requests
# from flask import Blueprint, render_template, request, redirect, url_for, flash
# from flask_login import login_user, logout_user, current_user, login_required
# from dotenv import load_dotenv
# from collections import Counter
# from datetime import datetime, timedelta

# from . import db
# from .models import User   # ✅ Removed Report import
# from .nlp_utils import analyze_text

# load_dotenv()
# bp = Blueprint("main", __name__)

# # ================== API KEY ==================
# API_KEY = os.getenv("NEWS_API_KEY") or os.getenv("API_KEY")
# if not API_KEY:
#     raise ValueError("❌ Missing API key! Set NEWS_API_KEY or API_KEY in .env")

# # ================== Category map ==================
# category_map = {
#     "Technology": "technology",
#     "Sports": "sports",
#     "Health": "health",
#     "Business": "business",
#     "Politics": "politics",
#     "Science": "science",
#     "World": "world",
#     "Entertainment": "entertainment"
# }

# # ================== GNews helper ==================
# def fetch_gnews(url, params):
#     try:
#         response = requests.get(url, params=params)
#         if response.status_code != 200:
#             try:
#                 error_msg = response.json().get("errors", response.text)
#             except:
#                 error_msg = response.text
#             flash(f"⚠️ GNews Error: {error_msg}", "danger")
#             return []
#         return response.json().get("articles", [])
#     except Exception as e:
#         flash(f"⚠️ GNews Exception: {str(e)}", "danger")
#         return []

# # ================== Home ==================
# @bp.route("/")
# def home():
#     return render_template("index.html", category_map=category_map)

# # ================== Register ==================
# @bp.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form.get("username")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         interested_area = request.form.get("interested_area")

#         if User.query.filter((User.username == username) | (User.email == email)).first():
#             flash("Username or email already exists!", "danger")
#             return redirect(url_for("main.register"))

#         new_user = User(
#             username=username,
#             email=email,
#             interested_area=interested_area
#         )
#         new_user.set_password(password)
#         db.session.add(new_user)
#         db.session.commit()

#         flash("Account created successfully! Please log in.", "success")
#         return redirect(url_for("main.login"))

#     return render_template("register.html", category_map=category_map)

# # ================== Trending News ==================
# @bp.route("/trending", methods=["GET", "POST"])
# def trending():
#     selected_area = request.form.get("interested_area", "None")
#     selected_country = request.form.get("country", "None")
#     selected_date = request.form.get("date_filter", "None")
#     keyword = request.form.get("keyword", "")

#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 30}

#     if selected_area != "None" and selected_area in category_map:
#         params["topic"] = category_map[selected_area]
#     if selected_country != "None":
#         params["country"] = selected_country
#     if keyword:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = keyword

#     articles = fetch_gnews(url, params)
#     if not articles:
#         flash("No news found for the selected filters.", "warning")

#     # Date filtering
#     now = datetime.utcnow()
#     threshold = None
#     if selected_date == "last_hours":
#         threshold = now - timedelta(hours=6)
#     elif selected_date == "today":
#         threshold = datetime(now.year, now.month, now.day)
#     elif selected_date == "yesterday":
#         threshold = datetime(now.year, now.month, now.day) - timedelta(days=1)
#     elif selected_date == "past_week":
#         threshold = now - timedelta(days=7)

#     enriched_articles = []
#     sentiment_list = []
#     entity_list = []

#     for art in articles:
#         published_at_raw = art.get("publishedAt")
#         if published_at_raw:
#             try:
#                 published_at_dt = datetime.strptime(published_at_raw, "%Y-%m-%dT%H:%M:%SZ")
#                 if threshold and published_at_dt < threshold:
#                     continue
#                 published_at_dt += timedelta(hours=5, minutes=30)  # IST
#                 published_at = published_at_dt.strftime("%d %b %Y, %H:%M IST")
#             except:
#                 published_at = "None"
#         else:
#             published_at = "None"

#         title = art.get("title") or "None"
#         description = art.get("description") or "None"
#         content = title + " " + description

#         nlp_result = analyze_text(content)
#         sentiment = nlp_result.get("sentiment", "None")
#         entities = nlp_result.get("entities", [])
#         if not entities:
#             entities = [("None", "None")]

#         sentiment_list.append(sentiment if sentiment else "None")
#         entity_list.extend([ent for ent, _ in entities] or ["None"])

#         enriched_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url") or "#",
#             "image": art.get("image") or "",
#             "sentiment": sentiment,
#             "entities": entities,
#             "published_at": published_at,
#             "source": art.get("source", {}).get("name") or "None"
#         })

#     # Ensure all sentiment keys exist for chart
#     sentiment_counts_raw = Counter(sentiment_list)
#     sentiment_counts = {
#         "Positive": int(sentiment_counts_raw.get("Positive", 0)),
#         "Neutral": int(sentiment_counts_raw.get("Neutral", 0)),
#         "Negative": int(sentiment_counts_raw.get("Negative", 0)),
#         "None": int(sentiment_counts_raw.get("None", 0))
#     }

#     # Top 10 entities for chart
#     entity_counts = dict(Counter(entity_list).most_common(10))
#     if not entity_counts:
#         entity_counts = {"None": 1}

#     return render_template(
#         "trending.html",
#         articles=enriched_articles,
#         sentiment_counts=sentiment_counts,
#         entity_counts=entity_counts,
#         selected_area=selected_area,
#         selected_country=selected_country,
#         selected_date=selected_date,
#         keyword=keyword,
#         category_map=category_map
#     )

# # ================== Login ==================
# @bp.route("/login", methods=["GET", "POST"])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for("main.dashboard"))

#     if request.method == "POST":
#         login_id = request.form.get("login_id")
#         password = request.form.get("password")
#         user = User.query.filter((User.email == login_id) | (User.username == login_id)).first()

#         if user and user.check_password(password):
#             login_user(user)
#             flash(f"Welcome back, {user.username}!", "success")
#             return redirect(url_for("main.dashboard"))
#         else:
#             flash("Login failed. Check username/email and password.", "danger")
#             return redirect(url_for("main.login"))

#     return render_template("login.html")

# # ================== Logout ==================
# @bp.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     flash("You have been logged out.", "info")
#     return redirect(url_for("main.home"))

# # ================== Dashboard ==================
# @bp.route("/dashboard")
# @login_required
# def dashboard():
#     interested_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 5}

#     if interested_area in category_map:
#         params["topic"] = category_map[interested_area]
#     elif interested_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = interested_area

#     articles = fetch_gnews(url, params)
#     analyzed_articles = []

#     for art in articles:
#         title = art.get("title") or "None"
#         description = art.get("description") or "None"
#         content = title + " " + description
#         nlp_result = analyze_text(content)
#         analyzed_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url") or "#",
#             "image": art.get("image") or "",
#             "publishedAt": art.get("publishedAt") or "None",
#             "sentiment": nlp_result.get("sentiment", "None"),
#             "sentiment_score": nlp_result.get("sentiment_score"),
#             "entities": nlp_result.get("entities", []) or [("None","None")]
#         })

#     return render_template(
#         "dashboard.html",
#         username=current_user.username,
#         articles=analyzed_articles,
#         category_map=category_map
#     )

# # ================== Profile ==================
# @bp.route("/profile", methods=["GET", "POST"])
# @login_required
# def profile():
#     if request.method == "POST":
#         current_user.username = request.form.get("username")
#         current_user.email = request.form.get("email")
#         current_user.interested_area = request.form.get("interested_area")
#         db.session.commit()
#         flash("Profile updated successfully!", "success")
#         return redirect(url_for("main.profile"))

#     return render_template("profile.html", category_map=category_map)




# import os
# import requests
# from flask import Blueprint, render_template, request, redirect, url_for, flash
# from flask_login import login_user, logout_user, current_user, login_required
# from dotenv import load_dotenv
# from collections import Counter
# from datetime import datetime, timedelta

# from . import db
# from .models import User
# from .nlp_utils import analyze_text

# load_dotenv()
# bp = Blueprint("main", __name__)

# # ================== API KEY ==================
# API_KEY = os.getenv("NEWS_API_KEY") or os.getenv("API_KEY")
# if not API_KEY:
#     raise ValueError("❌ Missing API key! Set NEWS_API_KEY or API_KEY in .env")

# # ================== Category map ==================
# category_map = {
#     "Technology": "technology",
#     "Sports": "sports",
#     "Health": "health",
#     "Business": "business",
#     "Politics": "politics",
#     "Science": "science",
#     "World": "world",
#     "Entertainment": "entertainment"
# }

# # ================== GNews helper ==================
# def fetch_gnews(url, params):
#     try:
#         response = requests.get(url, params=params)
#         if response.status_code != 200:
#             try:
#                 error_msg = response.json().get("errors", response.text)
#             except:
#                 error_msg = response.text
#             flash(f"⚠️ GNews Error: {error_msg}", "danger")
#             return []
#         return response.json().get("articles", [])
#     except Exception as e:
#         flash(f"⚠️ GNews Exception: {str(e)}", "danger")
#         return []

# # ================== Home ==================
# @bp.route("/")
# def home():
#     return render_template("index.html", category_map=category_map)

# # ================== Register ==================
# @bp.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form.get("username")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         interested_area = request.form.get("interested_area")

#         if User.query.filter((User.username == username) | (User.email == email)).first():
#             flash("Username or email already exists!", "danger")
#             return redirect(url_for("main.register"))

#         new_user = User(
#             username=username,
#             email=email,
#             interested_area=interested_area
#         )
#         new_user.set_password(password)
#         db.session.add(new_user)
#         db.session.commit()

#         flash("Account created successfully! Please log in.", "success")
#         return redirect(url_for("main.login"))

#     return render_template("register.html", category_map=category_map)

# # ================== Trending News ==================
# # @bp.route("/trending", methods=["GET", "POST"])
# # def trending():
# #     selected_area = request.form.get("interested_area", "None")
# #     selected_country = request.form.get("country", "None")
# #     selected_date = request.form.get("date_filter", "today")  # default today
# #     keyword = request.form.get("keyword", "")

# #     url = "https://gnews.io/api/v4/top-headlines"
# #     params = {"token": API_KEY, "lang": "en", "max": 30}

# #     # Category filter
# #     if selected_area != "None" and selected_area in category_map:
# #         params["topic"] = category_map[selected_area]

# #     # Country filter
# #     if selected_country != "None":
# #         params["country"] = selected_country

# #     # Keyword search
# #     if keyword:
# #         url = "https://gnews.io/api/v4/search"
# #         params["q"] = keyword

# #     articles = fetch_gnews(url, params)
# #     if not articles:
# #         flash("No news found for the selected filters.", "warning")

# #     # ------------------ Date Filtering ------------------
# #     now = datetime.utcnow()
# #     threshold_start = None
# #     threshold_end = now
# #     if selected_date == "last_hours":
# #         threshold_start = now - timedelta(hours=6)
# #     elif selected_date == "today":
# #         threshold_start = datetime(now.year, now.month, now.day)
# #     elif selected_date == "yesterday":
# #         yesterday = datetime(now.year, now.month, now.day) - timedelta(days=1)
# #         threshold_start = yesterday
# #         threshold_end = datetime(now.year, now.month, now.day)
# #     elif selected_date == "past_week":
# #         threshold_start = now - timedelta(days=7)

# #     enriched_articles = []
# #     sentiment_list = []
# #     entity_list = []

# #     for art in articles:
# #         published_at_raw = art.get("publishedAt")
# #         if published_at_raw:
# #             try:
# #                 published_at_dt = datetime.strptime(published_at_raw, "%Y-%m-%dT%H:%M:%SZ")
# #                 if threshold_start and published_at_dt < threshold_start:
# #                     continue
# #                 if threshold_end and published_at_dt > threshold_end:
# #                     continue
# #                 published_at_dt += timedelta(hours=5, minutes=30)  # IST
# #                 published_at = published_at_dt.strftime("%d %b %Y, %H:%M IST")
# #             except:
# #                 published_at = "None"
# #         else:
# #             published_at = "None"

# #         title = art.get("title") or "None"
# #         description = art.get("description") or "None"
# #         content = title + " " + description

# #         nlp_result = analyze_text(content)
# #         sentiment = nlp_result.get("sentiment", "None")
# #         entities = nlp_result.get("entities", [])
# #         if not entities:
# #             entities = [("None", "None")]

# #         sentiment_list.append(sentiment if sentiment else "None")
# #         entity_list.extend([ent for ent, _ in entities] or ["None"])

# #         enriched_articles.append({
# #             "title": title,
# #             "description": description,
# #             "url": art.get("url") or "#",
# #             "image": art.get("image") or "",
# #             "sentiment": sentiment,
# #             "entities": entities,
# #             "published_at": published_at,
# #             "source": art.get("source", {}).get("name") or "None"
# #         })

# #     # Ensure all sentiment keys exist for chart
# #     sentiment_counts_raw = Counter(sentiment_list)
# #     sentiment_counts = {
# #         "Positive": int(sentiment_counts_raw.get("Positive", 0)),
# #         "Neutral": int(sentiment_counts_raw.get("Neutral", 0)),
# #         "Negative": int(sentiment_counts_raw.get("Negative", 0)),
# #         "None": int(sentiment_counts_raw.get("None", 0))
# #     }

# #     # Top 10 entities for chart
# #     entity_counts = dict(Counter(entity_list).most_common(10))
# #     if not entity_counts:
# #         entity_counts = {"None": 1}

# #     return render_template(
# #         "trending.html",
# #         articles=enriched_articles,
# #         sentiment_counts=sentiment_counts,
# #         entity_counts=entity_counts,
# #         selected_area=selected_area,
# #         selected_country=selected_country,
# #         selected_date=selected_date,
# #         keyword=keyword,
# #         category_map=category_map
# #     )




# @bp.route("/trending", methods=["GET", "POST"])
# def trending():
#     selected_area = request.form.get("interested_area", "None")
#     selected_country = request.form.get("country", "None")
#     selected_date = request.form.get("date_filter", "today")  # default today
#     keyword = request.form.get("keyword", "")

#     # Determine date range
#     now = datetime.utcnow()
#     start_date = None
#     end_date = None

#     if selected_date == "last_hours":
#         start_date = now - timedelta(hours=6)
#         end_date = now
#     elif selected_date == "today":
#         start_date = datetime(now.year, now.month, now.day)
#         end_date = now
#     elif selected_date == "yesterday":
#         start_date = datetime(now.year, now.month, now.day) - timedelta(days=1)
#         end_date = datetime(now.year, now.month, now.day) - timedelta(seconds=1)
#     elif selected_date == "past_week":
#         start_date = now - timedelta(days=7)
#         end_date = now

#     # Base endpoint and params
#     url = "https://gnews.io/api/v4/search"  # Always search to support date filtering
#     params = {"token": API_KEY, "lang": "en", "max": 50}

#     # Keyword
#     if keyword:
#         params["q"] = keyword
#     elif selected_area != "None" and selected_area in category_map:
#         params["q"] = category_map[selected_area]

#     # Country
#     if selected_country != "None":
#         params["country"] = selected_country

#     # Add date filters in ISO format
#     if start_date:
#         params["from"] = start_date.isoformat()
#     if end_date:
#         params["to"] = end_date.isoformat()

#     # Fetch news
#     articles = fetch_gnews(url, params)
#     if not articles:
#         flash("No news found for the selected filters.", "warning")

#     # Enrich articles with NLP analysis and IST conversion
#     enriched_articles = []
#     sentiment_list = []
#     entity_list = []

#     for art in articles:
#         published_at_raw = art.get("publishedAt")
#         if published_at_raw:
#             try:
#                 published_at_dt = datetime.strptime(published_at_raw, "%Y-%m-%dT%H:%M:%SZ")
#                 published_at_dt += timedelta(hours=5, minutes=30)  # IST
#                 published_at = published_at_dt.strftime("%d %b %Y, %H:%M IST")
#             except:
#                 published_at = "None"
#         else:
#             published_at = "None"

#         title = art.get("title") or "None"
#         description = art.get("description") or "None"
#         content = title + " " + description

#         nlp_result = analyze_text(content)
#         sentiment = nlp_result.get("sentiment", "None")
#         entities = nlp_result.get("entities", [])
#         if not entities:
#             entities = [("None", "None")]

#         sentiment_list.append(sentiment if sentiment else "None")
#         entity_list.extend([ent for ent, _ in entities] or ["None"])

#         enriched_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url") or "#",
#             "image": art.get("image") or "",
#             "sentiment": sentiment,
#             "entities": entities,
#             "published_at": published_at,
#             "source": art.get("source", {}).get("name") or "None"
#         })

#     # Sentiment counts for chart
#     sentiment_counts_raw = Counter(sentiment_list)
#     sentiment_counts = {
#         "Positive": int(sentiment_counts_raw.get("Positive", 0)),
#         "Neutral": int(sentiment_counts_raw.get("Neutral", 0)),
#         "Negative": int(sentiment_counts_raw.get("Negative", 0)),
#         "None": int(sentiment_counts_raw.get("None", 0))
#     }

#     # Top 10 entities for chart
#     entity_counts = dict(Counter(entity_list).most_common(10))
#     if not entity_counts:
#         entity_counts = {"None": 1}

#     return render_template(
#         "trending.html",
#         articles=enriched_articles,
#         sentiment_counts=sentiment_counts,
#         entity_counts=entity_counts,
#         selected_area=selected_area,
#         selected_country=selected_country,
#         selected_date=selected_date,
#         keyword=keyword,
#         category_map=category_map
#     )



# import os
# import requests
# import pytz
# from flask import Blueprint, render_template, request, redirect, url_for, flash
# from flask_login import login_user, logout_user, current_user, login_required
# from dotenv import load_dotenv
# from collections import Counter
# from datetime import datetime, timedelta
# from collections import Counter, defaultdict



# from . import db
# from .models import User
# from .nlp_utils import analyze_text

# load_dotenv()
# bp = Blueprint("main", __name__)

# # ================== API KEY ==================
# API_KEY = os.getenv("NEWS_API_KEY") or os.getenv("API_KEY")
# if not API_KEY:
#     raise ValueError("❌ Missing API key! Set NEWS_API_KEY or API_KEY in .env")

# # ================== Category map ==================
# category_map = {
#     "Technology": "technology",
#     "Sports": "sports",
#     "Health": "health",
#     "Business": "business",
#     "Politics": "politics",
#     "Science": "science",
#     "World": "world",
#     "Entertainment": "entertainment"
# }

# # ================== GNews helper ==================
# def fetch_gnews(url, params):
#     try:
#         response = requests.get(url, params=params)
#         if response.status_code != 200:
#             try:
#                 error_msg = response.json().get("errors", response.text)
#             except:
#                 error_msg = response.text
#             flash(f"⚠️ GNews Error: {error_msg}", "danger")
#             return []
#         return response.json().get("articles", [])
#     except Exception as e:
#         flash(f"⚠️ GNews Exception: {str(e)}", "danger")
#         return []

# # ================== Home ==================
# @bp.route("/")
# def home():
#     return render_template("index.html", category_map=category_map)

# # ================== Register ==================
# @bp.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form.get("username")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         interested_area = request.form.get("interested_area")

#         if User.query.filter((User.username == username) | (User.email == email)).first():
#             flash("Username or email already exists!", "danger")
#             return redirect(url_for("main.register"))

#         new_user = User(
#             username=username,
#             email=email,
#             interested_area=interested_area
#         )
#         new_user.set_password(password)
#         db.session.add(new_user)
#         db.session.commit()

#         flash("Account created successfully! Please log in.", "success")
#         return redirect(url_for("main.login"))

#     return render_template("register.html", category_map=category_map)

# # ================== Trending News ==================







# @bp.route("/trending", methods=["GET", "POST"])
# def trending():
#     selected_area = request.form.get("interested_area", "None")
#     selected_country = request.form.get("country", "None")
#     keyword = request.form.get("keyword", "").strip()

#     # --- Fetch news articles (adapt with your API logic) ---
#     url = "https://gnews.io/api/v4/top-headlines" if selected_area != "None" else "https://gnews.io/api/v4/search"
#     params = {
#         "q": keyword if keyword else "news",
#         "token": os.getenv("GNEWS_API_KEY"),
#         "lang": "en",
#         "country": "in" if selected_country == "None" else selected_country.lower(),
#         "max": 50
#     }
#     response = requests.get(url, params=params)
#     articles = response.json().get("articles", [])

#     # --- Prepare sentiment analysis ---
#     sentiments = []
#     keywords = []
#     categories = []
#     sources = []

#     for article in articles:
#         title = article.get("title", "")
#         description = article.get("description", "")
#         content = f"{title}. {description}"

#         # Sentiment
#         blob = TextBlob(content)
#         polarity = blob.sentiment.polarity
#         if polarity > 0:
#             sentiments.append("Positive")
#         elif polarity < 0:
#             sentiments.append("Negative")
#         else:
#             sentiments.append("Neutral")

#         # Keywords (NER - just simple extraction here)
#         doc = nlp(content)
#         for ent in doc.ents:
#             keywords.append(ent.text)

#         # Categories placeholder (based on keyword match or fallback)
#         if "politics" in content.lower():
#             categories.append("Politics")
#         elif "sports" in content.lower():
#             categories.append("Sports")
#         elif "technology" in content.lower():
#             categories.append("Technology")
#         else:
#             categories.append("General")

#         # Source
#         sources.append(article.get("source", {}).get("name", "Unknown"))

#     # --- Count data ---
#     sentiment_counts = Counter(sentiments)
#     category_counts = Counter(categories)
#     source_counts = Counter(sources)
#     keyword_counts = Counter(keywords).most_common(5)  # Top 5 keywords for line chart

#     # --- Chart.js ready data ---
#     sentiment_counts_data = {
#         "labels": list(sentiment_counts.keys()),
#         "datasets": [
#             {
#                 "label": "Sentiments",
#                 "data": list(sentiment_counts.values()),
#                 "backgroundColor": [
#                     "rgba(75, 192, 192, 0.6)",
#                     "rgba(255, 99, 132, 0.6)",
#                     "rgba(255, 206, 86, 0.6)"
#                 ]
#             }
#         ]
#     }

#     category_counts_data = {
#         "labels": list(category_counts.keys()),
#         "datasets": [
#             {
#                 "label": "Categories",
#                 "data": list(category_counts.values()),
#                 "backgroundColor": [
#                     "rgba(54, 162, 235, 0.6)",
#                     "rgba(255, 159, 64, 0.6)",
#                     "rgba(153, 102, 255, 0.6)",
#                     "rgba(201, 203, 207, 0.6)"
#                 ]
#             }
#         ]
#     }

#     source_counts_data = {
#         "labels": list(source_counts.keys()),
#         "datasets": [
#             {
#                 "label": "Sources",
#                 "data": list(source_counts.values()),
#                 "backgroundColor": [
#                     "rgba(255, 205, 86, 0.6)",
#                     "rgba(75, 192, 192, 0.6)",
#                     "rgba(255, 99, 132, 0.6)",
#                     "rgba(54, 162, 235, 0.6)"
#                 ]
#             }
#         ]
#     }

#     line_chart_data = {
#         "labels": [kw for kw, _ in keyword_counts],
#         "datasets": [
#             {
#                 "label": "Top Keywords",
#                 "data": [count for _, count in keyword_counts],
#                 "borderColor": "rgba(75, 192, 192, 1)",
#                 "backgroundColor": "rgba(75, 192, 192, 0.2)",
#                 "fill": True,
#                 "tension": 0.3
#             }
#         ]
#     }

#     return render_template(
#         "trending.html",
#         sentiment_counts_data=sentiment_counts_data,
#         category_counts_data=category_counts_data,
#         source_counts_data=source_counts_data,
#         line_chart_data=line_chart_data,
#         articles=articles
#     )

# # # ================== Login ==================
# @bp.route("/login", methods=["GET", "POST"])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for("main.dashboard"))

#     if request.method == "POST":
#         login_id = request.form.get("login_id")
#         password = request.form.get("password")
#         user = User.query.filter((User.email == login_id) | (User.username == login_id)).first()

#         if user and user.check_password(password):
#             login_user(user)
#             flash(f"Welcome back, {user.username}!", "success")
#             return redirect(url_for("main.dashboard"))
#         else:
#             flash("Login failed. Check username/email and password.", "danger")
#             return redirect(url_for("main.login"))

#     return render_template("login.html")

# # ================== Logout ==================
# @bp.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     flash("You have been logged out.", "info")
#     return redirect(url_for("main.home"))

# # ================== Dashboard ==================
# @bp.route("/dashboard")
# @login_required
# def dashboard():
#     interested_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 5}

#     if interested_area in category_map:
#         params["topic"] = category_map[interested_area]
#     elif interested_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = interested_area

#     articles = fetch_gnews(url, params)
#     analyzed_articles = []

#     for art in articles:
#         title = art.get("title") or "None"
#         description = art.get("description") or "None"
#         content = title + " " + description
#         nlp_result = analyze_text(content)
#         analyzed_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url") or "#",
#             "image": art.get("image") or "",
#             "publishedAt": art.get("publishedAt") or "None",
#             "sentiment": nlp_result.get("sentiment", "None"),
#             "sentiment_score": nlp_result.get("sentiment_score"),
#             "entities": nlp_result.get("entities", []) or [("None","None")]
#         })

#     return render_template(
#         "dashboard.html",
#         username=current_user.username,
#         articles=analyzed_articles,
#         category_map=category_map
#     )

# # ================== Profile ==================
# @bp.route("/profile", methods=["GET", "POST"])
# @login_required
# def profile():
#     if request.method == "POST":
#         current_user.username = request.form.get("username")
#         current_user.email = request.form.get("email")
#         current_user.interested_area = request.form.get("interested_area")
#         db.session.commit()
#         flash("Profile updated successfully!", "success")
#         return redirect(url_for("main.profile"))

#     return render_template("profile.html", category_map=category_map)



# import os
# import requests
# import pytz
# from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
# from flask_login import login_user, logout_user, current_user, login_required
# from dotenv import load_dotenv
# from collections import Counter
# from datetime import datetime, timedelta
# from textblob import TextBlob
# import spacy

# from . import db
# from .models import User
# from .nlp_utils import analyze_text

# # ================== INIT ==================
# load_dotenv()
# bp = Blueprint("main", __name__)
# nlp = spacy.load("en_core_web_sm")  # load NLP model

# # ================== API KEY ==================
# API_KEY = os.getenv("NEWS_API_KEY") or os.getenv("API_KEY")
# if not API_KEY:
#     raise ValueError("❌ Missing API key! Set NEWS_API_KEY or API_KEY in .env")

# # ================== JINJA FILTER ==================
# def to_indian_time(utc_string):
#     """Convert UTC datetime string (from GNews) to IST format."""
#     try:
#         utc_dt = datetime.strptime(utc_string, "%Y-%m-%dT%H:%M:%SZ")
#         ist = pytz.timezone("Asia/Kolkata")
#         ist_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(ist)
#         return ist_dt.strftime("%d-%m-%Y %I:%M %p")  # Example: 30-08-2025 10:45 PM
#     except Exception:
#         return utc_string  # fallback if parsing fails

# # Register filter when blueprint is registered
# @bp.record_once
# def register_filters(setup_state):
#     app = setup_state.app
#     app.jinja_env.filters["to_indian_time"] = to_indian_time

# # ================== Category map ==================
# category_map = {
#     "Technology": "technology",
#     "Sports": "sports",
#     "Health": "health",
#     "Business": "business",
#     "Politics": "politics",
#     "Science": "science",
#     "World": "world",
#     "Entertainment": "entertainment"
# }

# # ================== GNews helper ==================
# def fetch_gnews(url, params):
#     try:
#         response = requests.get(url, params=params)
#         if response.status_code != 200:
#             try:
#                 error_msg = response.json().get("errors", response.text)
#             except:
#                 error_msg = response.text
#             flash(f"⚠️ GNews Error: {error_msg}", "danger")
#             return []
#         return response.json().get("articles", [])
#     except Exception as e:
#         flash(f"⚠️ GNews Exception: {str(e)}", "danger")
#         return []

# # ================== Home ==================
# @bp.route("/")
# def home():
#     return render_template("index.html", category_map=category_map)

# # ================== Register ==================
# @bp.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form.get("username")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         interested_area = request.form.get("interested_area")

#         if User.query.filter((User.username == username) | (User.email == email)).first():
#             flash("Username or email already exists!", "danger")
#             return redirect(url_for("main.register"))

#         new_user = User(
#             username=username,
#             email=email,
#             interested_area=interested_area
#         )
#         new_user.set_password(password)
#         db.session.add(new_user)
#         db.session.commit()

#         flash("Account created successfully! Please log in.", "success")
#         return redirect(url_for("main.login"))

#     return render_template("register.html", category_map=category_map)

# # ================== Trending News ==================
# # @bp.route("/trending", methods=["GET", "POST"])
# # def trending():
# #     selected_area = request.form.get("interested_area", "None")
# #     selected_country = request.form.get("country", "None")
# #     keyword = request.form.get("keyword", "").strip()

# #     # --- Fetch news articles ---
# #     url = "https://gnews.io/api/v4/top-headlines" if selected_area != "None" else "https://gnews.io/api/v4/search"
# #     params = {
# #         "q": keyword if keyword else "news",
# #         "token": os.getenv("GNEWS_API_KEY"),
# #         "lang": "en",
# #         "country": "in" if selected_country == "None" else selected_country.lower(),
# #         "max": 50
# #     }
# #     response = requests.get(url, params=params)
# #     articles = response.json().get("articles", [])

# #     # --- Prepare sentiment analysis ---
# #     sentiments, keywords, categories, sources = [], [], [], []

# #     for article in articles:
# #         title = article.get("title", "")
# #         description = article.get("description", "")
# #         content = f"{title}. {description}"

# #         # Sentiment with TextBlob
# #         blob = TextBlob(content)
# #         polarity = blob.sentiment.polarity
# #         if polarity > 0:
# #             sentiments.append("Positive")
# #         elif polarity < 0:
# #             sentiments.append("Negative")
# #         else:
# #             sentiments.append("Neutral")

# #         # NER with spaCy
# #         doc = nlp(content)
# #         for ent in doc.ents:
# #             keywords.append(ent.text)

# #         # Categories (basic matching)
# #         if "politics" in content.lower():
# #             categories.append("Politics")
# #         elif "sports" in content.lower():
# #             categories.append("Sports")
# #         elif "technology" in content.lower():
# #             categories.append("Technology")
# #         else:
# #             categories.append("General")

# #         # Sources
# #         sources.append(article.get("source", {}).get("name", "Unknown"))

# #     # --- Count data ---
# #     sentiment_counts = Counter(sentiments)
# #     category_counts = Counter(categories)
# #     source_counts = Counter(sources)
# #     keyword_counts = Counter(keywords).most_common(5)  # Top 5 keywords for line chart

# #     # --- Chart.js data ---
# #     sentiment_counts_data = {
# #         "labels": list(sentiment_counts.keys()),
# #         "datasets": [
# #             {"label": "Sentiments", "data": list(sentiment_counts.values())}
# #         ]
# #     }

# #     category_counts_data = {
# #         "labels": list(category_counts.keys()),
# #         "datasets": [
# #             {"label": "Categories", "data": list(category_counts.values())}
# #         ]
# #     }

# #     source_counts_data = {
# #         "labels": list(source_counts.keys()),
# #         "datasets": [
# #             {"label": "Sources", "data": list(source_counts.values())}
# #         ]
# #     }

# #     line_chart_data = {
# #         "labels": [kw for kw, _ in keyword_counts],
# #         "datasets": [
# #             {"label": "Top Keywords", "data": [count for _, count in keyword_counts]}
# #         ]
# #     }

# #     return render_template(
# #         "trending.html",
# #         sentiment_counts_data=sentiment_counts_data,
# #         category_counts_data=category_counts_data,
# #         source_counts_data=source_counts_data,
# #         line_chart_data=line_chart_data,
# #         articles=articles
# #     )


# # ================== Trending News ==================
# @bp.route("/trending", methods=["GET", "POST"])
# def trending():
#     selected_area = request.form.get("interested_area", "None")
#     selected_country = request.form.get("country", "None")
#     keyword = request.form.get("keyword", "").strip()

#     # --- Fetch news articles ---
#     url = "https://gnews.io/api/v4/top-headlines" if selected_area != "None" else "https://gnews.io/api/v4/search"
#     params = {
#         "q": keyword if keyword else "news",
#         "token": API_KEY,
#         "lang": "en",
#         "country": "in" if selected_country == "None" else selected_country.lower(),
#         "max": 50
#     }
#     articles_raw = fetch_gnews(url, params)

#     if not articles_raw:
#         flash("⚠️ No news articles found!", "warning")
#         return render_template("trending.html")

#     # --- Data prep ---
#     sentiments = []
#     categories = []
#     sources = []
#     keyword_counter = Counter()
#     keyword_time_series = {}  # {kw: {date: count}}

#     articles = []
#     for art in articles_raw:
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = f"{title}. {description}"

#         # --- Sentiment ---
#         blob = TextBlob(content)
#         polarity = blob.sentiment.polarity
#         if polarity > 0.1:
#             sentiments.append("Positive")
#         elif polarity < -0.1:
#             sentiments.append("Negative")
#         else:
#             sentiments.append("Neutral")

#         # --- NER keywords ---
#         doc = nlp(content)
#         keywords = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PERSON", "GPE", "EVENT"]]
#         for kw in keywords:
#             keyword_counter[kw] += 1
#             date_str = (art.get("publishedAt") or "")[:10]
#             if date_str:
#                 keyword_time_series.setdefault(kw, {}).setdefault(date_str, 0)
#                 keyword_time_series[kw][date_str] += 1

#         # --- Categories (basic detection) ---
#         if "politics" in content.lower():
#             categories.append("Politics")
#         elif "sports" in content.lower():
#             categories.append("Sports")
#         elif "technology" in content.lower():
#             categories.append("Technology")
#         elif "health" in content.lower():
#             categories.append("Health")
#         else:
#             categories.append("General")

#         # --- Sources ---
#         sources.append(art.get("source", {}).get("name", "Unknown"))

#         # --- Final article dict with IST time ---
#         articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url") or "#",
#             "image": art.get("image") or "",
#             "source": art.get("source", {}).get("name", "Unknown"),
#             "publishedAt": art.get("publishedAt"),
#             "publishedAtIST": to_indian_time(art.get("publishedAt")),
#             "keywords": keywords
#         })

#     # --- Counts ---
#     sentiment_counts = Counter(sentiments)
#     category_counts = Counter(categories)
#     source_counts = Counter(sources)

#     # --- Chart.js datasets ---
#     sentiment_counts_data = {
#         "labels": list(sentiment_counts.keys()),
#         "datasets": [{"label": "Sentiments", "data": list(sentiment_counts.values())}]
#     }

#     category_counts_data = {
#         "labels": list(category_counts.keys()),
#         "datasets": [{"label": "Categories", "data": list(category_counts.values())}]
#     }

#     source_counts_data = {
#         "labels": list(source_counts.keys()),
#         "datasets": [{"label": "Sources", "data": list(source_counts.values())}]
#     }

#     # --- Line chart (top 5 keywords over time) ---
#     top_keywords = [kw for kw, _ in keyword_counter.most_common(5)]
#     all_dates = sorted({d for kw in top_keywords for d in keyword_time_series.get(kw, {}).keys()})
#     datasets = []
#     for kw in top_keywords:
#         datasets.append({
#             "label": kw,
#             "data": [keyword_time_series.get(kw, {}).get(d, 0) for d in all_dates]
#         })

#     line_chart_data = {"labels": all_dates, "datasets": datasets}

#     # return render_template(
#     #     "trending.html",
#     #     sentiment_counts_data=sentiment_counts_data,
#     #     category_counts_data=category_counts_data,
#     #     source_counts_data=source_counts_data,
#     #     line_chart_data=line_chart_data,
#     #     articles=articles
#     # )
#     return render_template(
#     "trending.html",
#     articles=articles,
#     sentiment_counts_data=sentiment_counts_data if sentiment_counts_data else {},
#     category_counts_data=category_counts_data if category_counts_data else {},
#     source_counts_data=source_counts_data if source_counts_data else {},
#     line_chart_data=line_chart_data if line_chart_data else []
# )


# # ================== Login ==================
# @bp.route("/login", methods=["GET", "POST"])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for("main.dashboard"))

#     if request.method == "POST":
#         login_id = request.form.get("login_id")
#         password = request.form.get("password")
#         user = User.query.filter((User.email == login_id) | (User.username == login_id)).first()

#         if user and user.check_password(password):
#             login_user(user)
#             flash(f"Welcome back, {user.username}!", "success")
#             return redirect(url_for("main.dashboard"))
#         else:
#             flash("Login failed. Check username/email and password.", "danger")
#             return redirect(url_for("main.login"))

#     return render_template("login.html")

# # ================== Logout ==================
# @bp.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     flash("You have been logged out.", "info")
#     return redirect(url_for("main.home"))

# # ================== Dashboard ==================
# @bp.route("/dashboard")
# @login_required
# def dashboard():
#     interested_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 5}

#     if interested_area in category_map:
#         params["topic"] = category_map[interested_area]
#     elif interested_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = interested_area

#     articles = fetch_gnews(url, params)
#     analyzed_articles = []

#     for art in articles:
#         title = art.get("title") or "None"
#         description = art.get("description") or "None"
#         content = title + " " + description
#         nlp_result = analyze_text(content)
#         analyzed_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url") or "#",
#             "image": art.get("image") or "",
#             "publishedAt": art.get("publishedAt") or "None",
#             "sentiment": nlp_result.get("sentiment", "None"),
#             "sentiment_score": nlp_result.get("sentiment_score"),
#             "entities": nlp_result.get("entities", []) or [("None","None")]
#         })

#     return render_template(
#         "dashboard.html",
#         username=current_user.username,
#         articles=analyzed_articles,
#         category_map=category_map
#     )

# # ================== Profile ==================
# @bp.route("/profile", methods=["GET", "POST"])
# @login_required
# def profile():
#     if request.method == "POST":
#         current_user.username = request.form.get("username")
#         current_user.email = request.form.get("email")
#         current_user.interested_area = request.form.get("interested_area")
#         db.session.commit()
#         flash("Profile updated successfully!", "success")
#         return redirect(url_for("main.profile"))

#     return render_template("profile.html", category_map=category_map)


import os
import requests
import pytz
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from dotenv import load_dotenv
from collections import Counter
from datetime import datetime, timedelta
from textblob import TextBlob
import spacy

from . import db
from .models import User
from .nlp_utils import analyze_text

# ================== INIT ==================
load_dotenv()
bp = Blueprint("main", __name__)
nlp = spacy.load("en_core_web_sm")  # load NLP model

# ================== API KEY ==================
API_KEY = os.getenv("NEWS_API_KEY") or os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("❌ Missing API key! Set NEWS_API_KEY or API_KEY in .env")

# ================== JINJA FILTER ==================
def to_indian_time(utc_string):
    """Convert UTC datetime string (from GNews) to IST format."""
    try:
        utc_dt = datetime.strptime(utc_string, "%Y-%m-%dT%H:%M:%SZ")
        ist = pytz.timezone("Asia/Kolkata")
        ist_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(ist)
        return ist_dt.strftime("%d-%m-%Y %I:%M %p")  # Example: 30-08-2025 10:45 PM
    except Exception:
        return utc_string  # fallback if parsing fails

# Register filter when blueprint is registered
@bp.record_once
def register_filters(setup_state):
    app = setup_state.app
    app.jinja_env.filters["to_indian_time"] = to_indian_time

# ================== Category map ==================
category_map = {
    "World": "world",
    "Nation": "nation",
    "Business": "business",
    "Technology": "technology",
    "Entertainment": "entertainment",
    "Sports": "sports",
    "Science": "science",
    "Health": "health",
    "Politics": "politics"
}

# ================== GNews helper ==================
def fetch_gnews(url, params):
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            try:
                error_msg = response.json().get("errors", response.text)
            except:
                error_msg = response.text
            flash(f"⚠️ GNews Error: {error_msg}", "danger")
            return []
        return response.json().get("articles", [])
    except Exception as e:
        flash(f"⚠️ GNews Exception: {str(e)}", "danger")
        return []

# ================== Home ==================
@bp.route("/")
def home():
    return render_template("index.html", category_map=category_map)

# ================== Register ==================
@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        interested_area = request.form.get("interested_area")

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already exists!", "danger")
            return redirect(url_for("main.register"))

        new_user = User(
            username=username,
            email=email,
            interested_area=interested_area
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html", category_map=category_map)

# ================== Trending News ==================
# @bp.route("/trending", methods=["GET", "POST"])
# def trending():
#     selected_area = request.form.get("interested_area", "None")
#     selected_country = request.form.get("country", "None")
#     keyword = request.form.get("keyword", "").strip()

#     # --- Fetch news articles ---
#     url = "https://gnews.io/api/v4/top-headlines" if selected_area != "None" else "https://gnews.io/api/v4/search"
#     params = {
#         "q": keyword if keyword else "news",
#         "token": API_KEY,
#         "lang": "en",
#         "country": "in" if selected_country == "None" else selected_country.lower(),
#         "max": 50
#     }
#     if selected_area != "None" and selected_area.lower() in category_map.values():
#         params["topic"] = selected_area.lower()

#     articles_raw = fetch_gnews(url, params)
#     if not articles_raw:
#         flash("⚠️ No news articles found!", "warning")
#         return render_template("trending.html")

#     # --- Data prep ---
#     sentiments = []
#     categories = []
#     sources = []
#     keyword_counter = Counter()
#     keyword_time_series = {}  # {kw: {date: count}}

#     articles = []
#     for art in articles_raw:
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = f"{title}. {description}"

#         # --- Sentiment ---
#         blob = TextBlob(content)
#         polarity = blob.sentiment.polarity
#         if polarity > 0.1:
#             sentiment = "Positive"
#         elif polarity < -0.1:
#             sentiment = "Negative"
#         else:
#             sentiment = "Neutral"
#         sentiments.append(sentiment)

#         # --- NER keywords/entities ---
#         doc = nlp(content)
#         keywords = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PERSON", "GPE", "EVENT"]]
#         entities = [(ent.text, ent.label_) for ent in doc.ents]
#         for kw in keywords:
#             keyword_counter[kw] += 1
#             date_str = (art.get("publishedAt") or "")[:10]
#             if date_str:
#                 keyword_time_series.setdefault(kw, {}).setdefault(date_str, 0)
#                 keyword_time_series[kw][date_str] += 1

#         # --- Categories (basic detection) ---
#         if "politics" in content.lower():
#             categories.append("Politics")
#         elif "sports" in content.lower():
#             categories.append("Sports")
#         elif "technology" in content.lower():
#             categories.append("Technology")
#         elif "health" in content.lower():
#             categories.append("Health")
#         else:
#             categories.append("General")

#         # --- Sources ---
#         sources.append(art.get("source", {}).get("name", "Unknown"))

#         # --- Final article dict ---
#         articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url") or "#",
#             "image": art.get("image") or "",
#             "source": art.get("source", {}).get("name", "Unknown"),
#             "publishedAt": art.get("publishedAt"),
#             "publishedAtIST": to_indian_time(art.get("publishedAt")),
#             "sentiment": sentiment,
#             "entities": entities,
#             "keywords": keywords
#         })

#     # --- Counts ---
#     sentiment_counts = Counter(sentiments)
#     category_counts = Counter(categories)
#     source_counts = Counter(sources)

#     # --- Chart.js datasets ---
#     sentiment_counts_data = {
#         "labels": list(sentiment_counts.keys()),
#         "datasets": [{"label": "Sentiments", "data": list(sentiment_counts.values())}]
#     }

#     category_counts_data = {
#         "labels": list(category_counts.keys()),
#         "datasets": [{"label": "Categories", "data": list(category_counts.values())}]
#     }

#     source_counts_data = {
#         "labels": list(source_counts.keys()),
#         "datasets": [{"label": "Sources", "data": list(source_counts.values())}]
#     }

#     # --- Line chart (top 5 keywords over time) ---
#     top_keywords = [kw for kw, _ in keyword_counter.most_common(5)]
#     all_dates = sorted({d for kw in top_keywords for d in keyword_time_series.get(kw, {}).keys()})
#     datasets = []
#     for kw in top_keywords:
#         datasets.append({
#             "label": kw,
#             "data": [keyword_time_series.get(kw, {}).get(d, 0) for d in all_dates]
#         })

#     line_chart_data = {"labels": all_dates, "datasets": datasets}

#     return render_template(
#         "trending.html",
#         articles=articles,
#         sentiment_counts_data=sentiment_counts_data,
#         category_counts_data=category_counts_data,
#         source_counts_data=source_counts_data,
#         line_chart_data=line_chart_data
#     )

# @bp.route("/trending", methods=["GET", "POST"])
# def trending():
#     selected_area = request.form.get("interested_area", "None")
#     selected_country = request.form.get("country", "None")
#     keyword = request.form.get("keyword", "").strip()

#     # API endpoint
#     url = "https://gnews.io/api/v4/top-headlines" if selected_area != "None" else "https://gnews.io/api/v4/search"

#     params = {
#         "apikey": NEWS_API_KEY,
#         "lang": "en",
#         "max": 10,
#     }
#     if selected_area != "None":
#         params["topic"] = selected_area.lower()
#     if selected_country != "None":
#         params["country"] = selected_country.lower()
#     if keyword:
#         params["q"] = keyword

#     response = requests.get(url, params=params)
#     if response.status_code != 200:
#         flash("Failed to fetch news", "danger")
#         return render_template("trending.html")

#     news_data = response.json().get("articles", [])

#     articles = []
#     sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
#     category_counts = Counter()
#     source_counts = Counter()
#     line_chart_data = Counter()

#     for item in news_data:
#         title = item.get("title", "")
#         description = item.get("description", "")
#         content = f"{title} {description}"

#         # 🔹 Sentiment analysis
#         blob = TextBlob(content)
#         polarity = blob.sentiment.polarity
#         if polarity > 0.1:
#             sentiment = "positive"
#         elif polarity < -0.1:
#             sentiment = "negative"
#         else:
#             sentiment = "neutral"
#         sentiment_counts[sentiment] += 1

#         # 🔹 NER with spaCy
#         doc = nlp(content)
#         entities = [(ent.text, ent.label_) for ent in doc.ents]

#         # 🔹 Collect category/source/time stats
#         category_counts[selected_area] += 1 if selected_area != "None" else 0
#         if item.get("source", {}).get("name"):
#             source_counts[item["source"]["name"]] += 1
#         if item.get("publishedAt"):
#             date_str = item["publishedAt"][:10]
#             line_chart_data[date_str] += 1

#         articles.append({
#             "title": title,
#             "description": description,
#             "url": item.get("url"),
#             "source": item.get("source", {}).get("name"),
#             "publishedAt": item.get("publishedAt"),
#             "sentiment": sentiment,
#             "entities": entities
#         })

#     return render_template(
#         "trending.html",
#         articles=articles,
#         sentiment_counts_data=sentiment_counts,
#         category_counts_data=category_counts,
#         source_counts_data=source_counts,
#         line_chart_data=line_chart_data
#     )

# @bp.route("/trending", methods=["GET", "POST"])
# def trending():
#     selected_area = request.form.get("interested_area", "None")
#     selected_country = request.form.get("country", "None")
#     keyword = request.form.get("keyword", "").strip()

#     # Base URL
#     url = (
#         "https://gnews.io/api/v4/top-headlines"
#         if selected_area != "None"
#         else "https://gnews.io/api/v4/search"
#     )

#     # API Params
#     params = {
#         "apikey": API_KEY,   # ✅ FIXED
#         "lang": "en",
#         "max": 10,
#     }

#     if selected_area != "None":
#         params["topic"] = selected_area
#     if selected_country != "None":
#         params["country"] = selected_country.lower()
#     if keyword:
#         params["q"] = keyword

#     # Fetch articles
#     response = requests.get(url, params=params)
#     articles = response.json().get("articles", [])

#     sentiment_counts = Counter()
#     category_counts = Counter()
#     source_counts = Counter()
#     line_chart_data = {}

#     processed_articles = []
#     for article in articles:
#         content = f"{article.get('title', '')} {article.get('description', '')}"

#         # Sentiment
#         sentiment = TextBlob(content).sentiment.polarity
#         if sentiment > 0:
#             sentiment_label = "Positive"
#         elif sentiment < 0:
#             sentiment_label = "Negative"
#         else:
#             sentiment_label = "Neutral"
#         sentiment_counts[sentiment_label] += 1

#         # NER
#         doc = nlp(content)
#         entities = list(set([ent.text for ent in doc.ents]))

#         # Keywords (noun chunks)
#         keywords = [chunk.text for chunk in doc.noun_chunks]

#         # Dates for line chart
#         published_at = article.get("publishedAt", "")
#         if published_at:
#             try:
#                 dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
#                 date_str = dt.strftime("%Y-%m-%d")
#                 line_chart_data[date_str] = line_chart_data.get(date_str, 0) + 1
#                 published_at_ist = dt + timedelta(hours=5, minutes=30)
#             except:
#                 published_at_ist = published_at
#         else:
#             published_at_ist = "N/A"

#         # Source & Category
#         source = article.get("source", {}).get("name", "Unknown")
#         source_counts[source] += 1
#         category_counts[selected_area if selected_area != "None" else "General"] += 1

#         processed_articles.append({
#             "title": article.get("title"),
#             "description": article.get("description"),
#             "url": article.get("url"),
#             "image": article.get("image"),
#             "source": source,
#             "publishedAtIST": published_at_ist,
#             "keywords": keywords,
#             "entities": entities,
#             "sentiment": sentiment_label,
#         })

#     # Chart.js data
#     sentiment_counts_data = {
#         "labels": list(sentiment_counts.keys()),
#         "datasets": [{"data": list(sentiment_counts.values())}]
#     }

#     category_counts_data = {
#         "labels": list(category_counts.keys()),
#         "datasets": [{"data": list(category_counts.values())}]
#     }

#     source_counts_data = {
#         "labels": list(source_counts.keys()),
#         "datasets": [{"data": list(source_counts.values())}]
#     }

#     line_chart_data_formatted = {
#         "labels": list(line_chart_data.keys()),
#         "datasets": [{"label": "Mentions", "data": list(line_chart_data.values())}]
#     }

#     return render_template(
#         "trending.html",
#         articles=processed_articles,
#         sentiment_counts_data=sentiment_counts_data,
#         category_counts_data=category_counts_data,
#         source_counts_data=source_counts_data,
#         line_chart_data=line_chart_data_formatted,
#     )

# @bp.route("/trending", methods=["GET", "POST"])
# def trending():
#     selected_area = request.form.get("interested_area", "None")
#     selected_country = request.form.get("country", "None")
#     keyword = request.form.get("keyword", "").strip()

#     # Base URL
#     url = (
#         "https://gnews.io/api/v4/top-headlines"
#         if selected_area != "None"
#         else "https://gnews.io/api/v4/search"
#     )

#     # API Params
#     params = {
#         "apikey": API_KEY,
#         "lang": "en",
#         "max": 10,
#     }
#     if selected_area != "None":
#         params["topic"] = selected_area
#     if selected_country != "None":
#         params["country"] = selected_country.lower()
#     if keyword:
#         params["q"] = keyword

#     # Fetch articles
#     response = requests.get(url, params=params)
#     articles = response.json().get("articles", [])

#     sentiment_counts = Counter()
#     category_counts = Counter()
#     source_counts = Counter()
#     line_chart_data = {}

#     processed_articles = []
#     for article in articles:
#         content = f"{article.get('title', '')} {article.get('description', '')}"

#         # Sentiment
#         sentiment = TextBlob(content).sentiment.polarity
#         if sentiment > 0:
#             sentiment_label = "Positive"
#         elif sentiment < 0:
#             sentiment_label = "Negative"
#         else:
#             sentiment_label = "Neutral"
#         sentiment_counts[sentiment_label] += 1

#         # NER
#         doc = nlp(content)
#         entities = list(set([ent.text for ent in doc.ents]))

#         # Keywords
#         keywords = [chunk.text for chunk in doc.noun_chunks]

#         # Dates for line chart
#         published_at = article.get("publishedAt", "")
#         if published_at:
#             try:
#                 dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
#                 date_str = dt.strftime("%Y-%m-%d")
#                 line_chart_data[date_str] = line_chart_data.get(date_str, 0) + 1
#                 published_at_ist = dt + timedelta(hours=5, minutes=30)
#             except:
#                 published_at_ist = published_at
#         else:
#             published_at_ist = "N/A"

#         # Source & Category
#         source = article.get("source", {}).get("name", "Unknown")
#         source_counts[source] += 1
#         category_counts[selected_area if selected_area != "None" else "General"] += 1

#         processed_articles.append({
#             "title": article.get("title"),
#             "description": article.get("description"),
#             "url": article.get("url"),
#             "image": article.get("image"),
#             "source": source,
#             "publishedAtIST": published_at_ist,
#             "keywords": keywords,
#             "entities": entities,
#             "sentiment": sentiment_label,
#         })

#     # --- Category counts (all categories with highlight) ---
#     all_categories = ["World", "Nation", "Business", "Technology",
#                       "Entertainment", "Sports", "Science", "Health", "Politics"]
#     category_counts_complete = {cat: 0 for cat in all_categories}

#     for cat, count in category_counts.items():
#         display_name = cat.capitalize() if cat != "None" else "General"
#         if display_name in category_counts_complete:
#             category_counts_complete[display_name] = count
#         else:
#             category_counts_complete["General"] += count

#     selected_category_display = selected_area.capitalize() if selected_area != "None" else None

#     category_counts_data = {
#         "labels": list(category_counts_complete.keys()),
#         "datasets": [{
#             "data": list(category_counts_complete.values()),
#             "backgroundColor": [
#                 "#4e73df" if cat != selected_category_display else "#ff6384"
#                 for cat in category_counts_complete.keys()
#             ]
#         }]
#     }

#     # Chart.js data
#     sentiment_counts_data = {
#         "labels": list(sentiment_counts.keys()),
#         "datasets": [{"data": list(sentiment_counts.values())}]
#     }

#     source_counts_data = {
#         "labels": list(source_counts.keys()),
#         "datasets": [{"data": list(source_counts.values())}]
#     }

#     line_chart_data_formatted = {
#         "labels": list(line_chart_data.keys()),
#         "datasets": [{"label": "Mentions", "data": list(line_chart_data.values())}]
#     }

#     return render_template(
#         "trending.html",
#         articles=processed_articles,
#         sentiment_counts_data=sentiment_counts_data,
#         category_counts_data=category_counts_data,
#         source_counts_data=source_counts_data,
#         line_chart_data=line_chart_data_formatted,
#     )



# @bp.route("/trending", methods=["GET", "POST"])
# def trending():
#     selected_area = request.form.get("interested_area", "None")
#     selected_country = request.form.get("country", "None")
#     keyword = request.form.get("keyword", "").strip()

#     url = "https://gnews.io/api/v4/top-headlines" if selected_area != "None" else "https://gnews.io/api/v4/search"
#     params = {
#         "apikey": API_KEY,
#         "lang": "en",
#         "max": 10,
#     }
#     if selected_area != "None":
#         params["topic"] = selected_area
#     if selected_country != "None":
#         params["country"] = selected_country.lower()
#     if keyword:
#         params["q"] = keyword

#     response = requests.get(url, params=params)
#     articles = response.json().get("articles", [])

#     sentiment_counts = Counter()
#     category_counts = Counter()
#     source_counts = Counter()
#     line_chart_data = {}

#     processed_articles = []
#     for article in articles:
#         content = f"{article.get('title', '')} {article.get('description', '')}"

#         # Sentiment
#         polarity = TextBlob(content).sentiment.polarity
#         sentiment_label = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"
#         sentiment_counts[sentiment_label] += 1

#         # NER
#         doc = nlp(content)
#         entities = list(set([ent.text for ent in doc.ents]))
#         keywords = [chunk.text for chunk in doc.noun_chunks]

#         # Dates for line chart
#         published_at = article.get("publishedAt", "")
#         if published_at:
#             try:
#                 dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
#                 date_str = dt.strftime("%Y-%m-%d")
#                 line_chart_data[date_str] = line_chart_data.get(date_str, 0) + 1
#                 published_at_ist = dt + timedelta(hours=5, minutes=30)
#             except:
#                 published_at_ist = published_at
#         else:
#             published_at_ist = "N/A"

#         # Source & Category
#         source = article.get("source", {}).get("name", "Unknown")
#         source_counts[source] += 1
#         category = selected_area if selected_area != "None" else "General"
#         category_counts[category] += 1

#         processed_articles.append({
#             "title": article.get("title"),
#             "description": article.get("description"),
#             "url": article.get("url"),
#             "image": article.get("image"),
#             "source": source,
#             "publishedAtIST": published_at_ist,
#             "keywords": keywords,
#             "entities": entities,
#             "sentiment": sentiment_label,
#         })

#     # --- Fix KeyError by including 'General' ---
#     all_categories = list(category_map.keys()) + ["General"]
#     category_counts_complete = {cat: 0 for cat in all_categories}
#     for cat, count in category_counts.items():
#         display_name = cat.capitalize() if cat != "None" else "General"
#         if display_name in category_counts_complete:
#             category_counts_complete[display_name] += count
#         else:
#             category_counts_complete["General"] += count

#     selected_category_display = selected_area.capitalize() if selected_area != "None" else None
#     category_counts_data = {
#         "labels": list(category_counts_complete.keys()),
#         "datasets": [{
#             "data": list(category_counts_complete.values()),
#             "backgroundColor": [
#                 "#4e73df" if cat != selected_category_display else "#ff6384"
#                 for cat in category_counts_complete.keys()
#             ]
#         }]
#     }

#     # --- Chart.js data ---
#     sentiment_counts_data = {
#         "labels": list(sentiment_counts.keys()),
#         "datasets": [{"data": list(sentiment_counts.values())}]
#     }
#     source_counts_data = {
#         "labels": list(source_counts.keys()),
#         "datasets": [{"data": list(source_counts.values())}]
#     }
#     line_chart_data_formatted = {
#         "labels": list(line_chart_data.keys()),
#         "datasets": [{"label": "Mentions", "data": list(line_chart_data.values())}]
#     }

#     # --- Top stats ---
#     total_articles = len(processed_articles)
#     top_category = max(category_counts_complete, key=lambda k: category_counts_complete[k]) \
#                    if processed_articles else "N/A"
#     top_source = source_counts.most_common(1)[0][0] if source_counts else "N/A"

#     return render_template(
#         "trending.html",
#         articles=processed_articles,
#         sentiment_counts_data=sentiment_counts_data,
#         category_counts_data=category_counts_data,
#         source_counts_data=source_counts_data,
#         line_chart_data=line_chart_data_formatted,
#         total_articles=total_articles,
#         top_category=top_category,
#         top_source=top_source
#     )


# @bp.route("/trending", methods=["GET", "POST"])
# def trending():
#     # --- Get inputs from form or query params ---
#     selected_area = request.form.get("interested_area") or request.args.get("interested_area") or "None"
#     selected_country = request.form.get("country") or request.args.get("country") or "None"
#     keyword = request.form.get("keyword", "").strip() or request.args.get("keyword", "").strip() or "latest"

#     # --- Decide API endpoint ---
#     url = "https://gnews.io/api/v4/top-headlines" if selected_area != "None" else "https://gnews.io/api/v4/search"

#     params = {
#         "apikey": API_KEY,
#         "lang": "en",
#         "max": 10,
#     }
#     if selected_area != "None":
#         params["topic"] = selected_area
#     if selected_country != "None":
#         params["country"] = selected_country.lower()
#     if keyword:
#         params["q"] = keyword

#     # --- Fetch articles ---
#     response = requests.get(url, params=params)
#     data = response.json()
#     articles = data.get("articles", [])

#     # --- Prepare stats ---
#     sentiment_counts = Counter()
#     category_counts = Counter()
#     source_counts = Counter()
#     line_chart_data = {}
#     processed_articles = []

#     for article in articles:
#         content = f"{article.get('title','')} {article.get('description','')}"
#         # Sentiment
#         polarity = TextBlob(content).sentiment.polarity
#         sentiment_label = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"
#         sentiment_counts[sentiment_label] += 1

#         # NER
#         doc = nlp(content)
#         entities = list(set([ent.text for ent in doc.ents]))
#         keywords_list = [chunk.text for chunk in doc.noun_chunks]

#         # Published date
#         published_at = article.get("publishedAt")
#         if published_at:
#             try:
#                 dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
#                 date_str = dt.strftime("%Y-%m-%d")
#                 line_chart_data[date_str] = line_chart_data.get(date_str, 0) + 1
#                 published_at_ist = dt + timedelta(hours=5, minutes=30)
#             except:
#                 published_at_ist = published_at
#         else:
#             published_at_ist = "N/A"

#         # Source & category
#         source = article.get("source", {}).get("name", "Unknown")
#         source_counts[source] += 1
#         category = selected_area if selected_area != "None" else "General"
#         category_counts[category] += 1

#         processed_articles.append({
#             "title": article.get("title"),
#             "description": article.get("description"),
#             "url": article.get("url"),
#             "image": article.get("image"),
#             "source": source,
#             "publishedAtIST": published_at_ist,
#             "keywords": keywords_list,
#             "entities": entities,
#             "sentiment": sentiment_label,
#         })

#     # --- Prepare chart data ---
#     all_categories = list(category_map.keys()) + ["General"]
#     category_counts_complete = {cat: 0 for cat in all_categories}
#     for cat, count in category_counts.items():
#         display_name = cat.capitalize() if cat != "None" else "General"
#         if display_name in category_counts_complete:
#             category_counts_complete[display_name] += count
#         else:
#             category_counts_complete["General"] += count

#     selected_category_display = selected_area.capitalize() if selected_area != "None" else None
#     category_counts_data = {
#         "labels": list(category_counts_complete.keys()),
#         "datasets": [{
#             "data": list(category_counts_complete.values()),
#             "backgroundColor": [
#                 "#4e73df" if cat != selected_category_display else "#ff6384"
#                 for cat in category_counts_complete.keys()
#             ]
#         }]
#     }

#     sentiment_counts_data = {
#         "labels": list(sentiment_counts.keys()),
#         "datasets": [{"data": list(sentiment_counts.values())}]
#     }
#     source_counts_data = {
#         "labels": list(source_counts.keys()),
#         "datasets": [{"data": list(source_counts.values())}]
#     }
#     line_chart_data_formatted = {
#         "labels": list(line_chart_data.keys()),
#         "datasets": [{"label": "Mentions", "data": list(line_chart_data.values())}]
#     }

#     # --- Top stats ---
#     total_articles = len(processed_articles)
#     top_category = max(category_counts_complete, key=lambda k: category_counts_complete[k]) if processed_articles else "N/A"
#     top_source = source_counts.most_common(1)[0][0] if source_counts else "N/A"

#     return render_template(
#         "trending.html",
#         articles=processed_articles,
#         sentiment_counts_data=sentiment_counts_data,
#         category_counts_data=category_counts_data,
#         source_counts_data=source_counts_data,
#         line_chart_data=line_chart_data_formatted,
#         total_articles=total_articles,
#         top_category=top_category,
#         top_source=top_source
#     )

@bp.route("/trending", methods=["GET", "POST"])
def trending():
    # --- Get inputs from form or query params ---
    selected_area = request.form.get("interested_area") or request.args.get("interested_area") or "None"
    selected_country = request.form.get("country") or request.args.get("country") or "None"
    keyword = request.form.get("keyword", "").strip() or request.args.get("keyword", "").strip()

    # --- Decide API endpoint & params ---
    if keyword:  # if user typed a keyword, use search
        url = "https://gnews.io/api/v4/search"
        params = {
            "apikey": API_KEY,
            "lang": "en",
            "max": 10,
            "q": keyword,
        }
    else:  # no keyword → fallback to top-headlines
        url = "https://gnews.io/api/v4/top-headlines"
        params = {
            "apikey": API_KEY,
            "lang": "en",
            "max": 10,
        }

    # Add filters if provided
    if selected_area != "None":
        params["topic"] = selected_area
    if selected_country != "None":
        params["country"] = selected_country.lower()

    # --- Fetch articles ---
    response = requests.get(url, params=params)
    data = response.json()
    articles = data.get("articles", [])

    # --- Prepare stats ---
    sentiment_counts = Counter()
    category_counts = Counter()
    source_counts = Counter()
    line_chart_data = {}
    processed_articles = []

    for article in articles:
        content = f"{article.get('title','')} {article.get('description','')}"
        # Sentiment
        polarity = TextBlob(content).sentiment.polarity
        sentiment_label = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"
        sentiment_counts[sentiment_label] += 1

        # NER
        doc = nlp(content)
        entities = list(set([ent.text for ent in doc.ents]))
        keywords_list = [chunk.text for chunk in doc.noun_chunks]

        # Published date
        published_at = article.get("publishedAt")
        if published_at:
            try:
                dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
                date_str = dt.strftime("%Y-%m-%d")
                line_chart_data[date_str] = line_chart_data.get(date_str, 0) + 1
                published_at_ist = dt + timedelta(hours=5, minutes=30)
            except:
                published_at_ist = published_at
        else:
            published_at_ist = "N/A"

        # Source & category
        source = article.get("source", {}).get("name", "Unknown")
        source_counts[source] += 1
        category = selected_area if selected_area != "None" else "General"
        category_counts[category] += 1

        processed_articles.append({
            "title": article.get("title"),
            "description": article.get("description"),
            "url": article.get("url"),
            "image": article.get("image"),
            "source": source,
            "publishedAtIST": published_at_ist,
            "keywords": keywords_list,
            "entities": entities,
            "sentiment": sentiment_label,
        })

    # --- Prepare chart data ---
    all_categories = list(category_map.keys()) + ["General"]
    category_counts_complete = {cat: 0 for cat in all_categories}
    for cat, count in category_counts.items():
        display_name = cat.capitalize() if cat != "None" else "General"
        if display_name in category_counts_complete:
            category_counts_complete[display_name] += count
        else:
            category_counts_complete["General"] += count

    selected_category_display = selected_area.capitalize() if selected_area != "None" else None
    category_counts_data = {
        "labels": list(category_counts_complete.keys()),
        "datasets": [{
            "data": list(category_counts_complete.values()),
            "backgroundColor": [
                "#4e73df" if cat != selected_category_display else "#ff6384"
                for cat in category_counts_complete.keys()
            ]
        }]
    }

    sentiment_counts_data = {
        "labels": list(sentiment_counts.keys()),
        "datasets": [{"data": list(sentiment_counts.values())}]
    }
    source_counts_data = {
        "labels": list(source_counts.keys()),
        "datasets": [{"data": list(source_counts.values())}]
    }
    line_chart_data_formatted = {
        "labels": list(line_chart_data.keys()),
        "datasets": [{"label": "Mentions", "data": list(line_chart_data.values())}]
    }

    # --- Top stats ---
    total_articles = len(processed_articles)
    top_category = max(category_counts_complete, key=lambda k: category_counts_complete[k]) if processed_articles else "N/A"
    top_source = source_counts.most_common(1)[0][0] if source_counts else "N/A"

    return render_template(
        "trending.html",
        articles=processed_articles,
        sentiment_counts_data=sentiment_counts_data,
        category_counts_data=category_counts_data,
        source_counts_data=source_counts_data,
        line_chart_data=line_chart_data_formatted,
        total_articles=total_articles,
        top_category=top_category,
        top_source=top_source
    )

# ================== Login ==================
@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        login_id = request.form.get("login_id")
        password = request.form.get("password")
        user = User.query.filter((User.email == login_id) | (User.username == login_id)).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Login failed. Check username/email and password.", "danger")
            return redirect(url_for("main.login"))

    return render_template("login.html")

# ================== Logout ==================
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))

# ================== Dashboard ==================
# @bp.route("/dashboard")
# @login_required
# def dashboard():
#     interested_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 5}

#     if interested_area in category_map:
#         params["topic"] = category_map[interested_area]
#     elif interested_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = interested_area

#     articles = fetch_gnews(url, params)
#     analyzed_articles = []

#     for art in articles:
#         title = art.get("title") or "None"
#         description = art.get("description") or "None"
#         content = title + " " + description
#         nlp_result = analyze_text(content)
#         analyzed_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url") or "#",
#             "image": art.get("image") or "",
#             "publishedAt": art.get("publishedAt") or "None",
#             "sentiment": nlp_result.get("sentiment", "None"),
#             "sentiment_score": nlp_result.get("sentiment_score"),
#             "entities": nlp_result.get("entities", []) or [("None","None")]
#         })

#     return render_template(
#         "dashboard.html",
#         username=current_user.username,
#         articles=analyzed_articles,
#         category_map=category_map
#     )


# @bp.route("/dashboard")
# @login_required
# def dashboard():
#     interested_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 10}

#     # Adjust API call based on user interest
#     if interested_area in category_map:
#         params["topic"] = category_map[interested_area]
#     elif interested_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = interested_area

#     articles_raw = fetch_gnews(url, params)

#     analyzed_articles = []
#     category_counter = Counter()
#     source_counter = Counter()

#     for art in articles_raw:
#         title = art.get("title") or "No Title"
#         description = art.get("description") or ""
#         content = f"{title} {description}"

#         # NLP analysis
#         nlp_result = analyze_text(content)
#         analyzed_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url") or "#",
#             "image": art.get("image") or "",
#             "publishedAt": art.get("publishedAt") or "N/A",
#             "sentiment": nlp_result.get("sentiment", "Neutral"),
#             "sentiment_score": nlp_result.get("sentiment_score", 0),
#             "entities": nlp_result.get("entities", []) or [("None", "None")]
#         })

#         # Count categories (use General if none)
#         category = art.get("topic", "General").capitalize()
#         category_counter[category] += 1

#         # Count sources
#         source = art.get("source", {}).get("name", "Unknown")
#         source_counter[source] += 1

#     # Dashboard stats
#     total_articles = len(analyzed_articles)
#     top_category = category_counter.most_common(1)[0][0] if category_counter else "N/A"
#     top_source = source_counter.most_common(1)[0][0] if source_counter else "N/A"

#     return render_template(
#         "dashboard.html",
#         username=current_user.username,
#         articles=analyzed_articles,
#         total_articles=total_articles,
#         top_category=top_category,
#         top_source=top_source
#     )

# from collections import Counter

# @bp.route("/dashboard")
# @login_required
# def dashboard():
#     interested_area = current_user.interested_area or ""
#     url = "https://gnews.io/api/v4/top-headlines"
#     params = {"token": API_KEY, "lang": "en", "max": 10}

#     if interested_area in category_map:
#         params["topic"] = category_map[interested_area]
#     elif interested_area:
#         url = "https://gnews.io/api/v4/search"
#         params["q"] = interested_area

#     articles = fetch_gnews(url, params)
#     analyzed_articles = []
#     category_counter = Counter()
#     source_counter = Counter()

#     for art in articles:
#         title = art.get("title") or "None"
#         description = art.get("description") or "None"
#         content = title + " " + description
#         nlp_result = analyze_text(content)

#         # Count categories and sources
#         category = art.get("topic", "General").capitalize()
#         category_counter[category] += 1
#         source = art.get("source", {}).get("name", "Unknown")
#         source_counter[source] += 1

#         analyzed_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url") or "#",
#             "image": art.get("image") or "",
#             "publishedAt": art.get("publishedAt") or "None",
#             "sentiment": nlp_result.get("sentiment", "None"),
#             "sentiment_score": nlp_result.get("sentiment_score"),
#             "entities": nlp_result.get("entities", []) or [("None","None")]
#         })

#     total_articles = len(analyzed_articles)
#     top_category = category_counter.most_common(1)[0][0] if category_counter else "N/A"
#     top_source = source_counter.most_common(1)[0][0] if source_counter else "N/A"

#     return render_template(
#         "dashboard.html",
#         username=current_user.username,
#         articles=analyzed_articles,
#         total_articles=total_articles,
#         top_category=top_category,
#         top_source=top_source,
#         category_map=category_map
#     )

# @bp.route("/dashboard", methods=["GET", "POST"])
# @login_required
# def dashboard():
#     # Get filters from form if POST, else use user defaults
#     keyword = request.form.get("keyword", "")
#     interested_area = request.form.get("interested_area", current_user.interested_area or "")
#     country = request.form.get("country", "in")  # default India

#     # Base URL and params
#     if interested_area:
#         url = "https://gnews.io/api/v4/top-headlines"
#         params = {"token": API_KEY, "lang": "en", "max": 10, "topic": interested_area.lower()}
#     else:
#         url = "https://gnews.io/api/v4/search"
#         params = {"token": API_KEY, "lang": "en", "max": 10}
    
#     if keyword:
#         params["q"] = keyword
#     if country != "all":
#         params["country"] = country.lower()

#     # Fetch articles
#     articles = fetch_gnews(url, params)
#     analyzed_articles = []

#     # Stats counters
#     total_articles = 0
#     category_counter = Counter()
#     source_counter = Counter()

#     for art in articles:
#         title = art.get("title") or ""
#         description = art.get("description") or ""
#         content = f"{title} {description}"

#         # Sentiment + Entities
#         nlp_result = analyze_text(content)

#         # Category detection (simple)
#         cat = interested_area.capitalize() if interested_area else "General"
#         category_counter[cat] += 1

#         # Source
#         source = art.get("source", {}).get("name", "Unknown")
#         source_counter[source] += 1

#         analyzed_articles.append({
#             "title": title,
#             "description": description,
#             "url": art.get("url") or "#",
#             "image": art.get("image") or "",
#             "publishedAt": art.get("publishedAt") or "N/A",
#             "sentiment": nlp_result.get("sentiment", "Neutral"),
#             "sentiment_score": nlp_result.get("sentiment_score", 0),
#             "entities": nlp_result.get("entities", [])
#         })

#     total_articles = len(analyzed_articles)
#     top_category = category_counter.most_common(1)[0][0] if category_counter else "N/A"
#     top_source = source_counter.most_common(1)[0][0] if source_counter else "N/A"

#     return render_template(
#         "dashboard.html",
#         username=current_user.username,
#         articles=analyzed_articles,
#         total_articles=total_articles,
#         top_category=top_category,
#         top_source=top_source,
#         category_map=category_map
#     )
@bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    # Get filters from form if POST, else use user defaults
    keyword = request.form.get("keyword", "")
    interested_area = request.form.get("interested_area", current_user.interested_area or "")
    country = request.form.get("country", "in")  # default India

    # --- Decide API endpoint ---
    if keyword:  # if keyword given, use search
        url = "https://gnews.io/api/v4/search"
        params = {"token": API_KEY, "lang": "en", "max": 10, "q": keyword}
    elif interested_area:  # if interested area given, use top-headlines by topic
        url = "https://gnews.io/api/v4/top-headlines"
        params = {"token": API_KEY, "lang": "en", "max": 10, "topic": interested_area.lower()}
    else:  # no keyword & no area → fallback to general top-headlines
        url = "https://gnews.io/api/v4/top-headlines"
        params = {"token": API_KEY, "lang": "en", "max": 10}

    if country != "all":
        params["country"] = country.lower()

    # --- Fetch articles ---
    articles = fetch_gnews(url, params)
    analyzed_articles = []

    # Stats counters
    category_counter = Counter()
    source_counter = Counter()

    for art in articles:
        title = art.get("title") or ""
        description = art.get("description") or ""
        content = f"{title} {description}"

        # Sentiment + Entities
        nlp_result = analyze_text(content)

        # Category detection (simple)
        cat = interested_area.capitalize() if interested_area else "General"
        category_counter[cat] += 1

        # Source
        source = art.get("source", {}).get("name", "Unknown")
        source_counter[source] += 1

        analyzed_articles.append({
            "title": title,
            "description": description,
            "url": art.get("url") or "#",
            "image": art.get("image") or "",
            "publishedAt": art.get("publishedAt") or "N/A",
            "sentiment": nlp_result.get("sentiment", "Neutral"),
            "sentiment_score": nlp_result.get("sentiment_score", 0),
            "entities": nlp_result.get("entities", [])
        })

    total_articles = len(analyzed_articles)
    top_category = category_counter.most_common(1)[0][0] if category_counter else "N/A"
    top_source = source_counter.most_common(1)[0][0] if source_counter else "N/A"

    return render_template(
        "dashboard.html",
        username=current_user.username,
        articles=analyzed_articles,
        total_articles=total_articles,
        top_category=top_category,
        top_source=top_source,
        category_map=category_map
    )

# ================== Profile ==================
@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.username = request.form.get("username")
        current_user.email = request.form.get("email")
        current_user.interested_area = request.form.get("interested_area")
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("main.profile"))

    return render_template("profile.html", category_map=category_map)

