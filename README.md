# 📰 NewsPulse – AI News Trend Analyzer

---

## 1. Project Overview
```text
NewsPulse is a modern web application that analyzes trending news using AI and NLP.
Users can filter news by category, country, or keyword and gain insights through:

- Sentiment analysis
- Entity recognition
- Visual dashboards

```

---

## 2. Features
```text
- User Authentication (Register, Login, Profile, Logout)
- Personalized Dashboard with glassmorphic design
- Trending News with filters (Category, Country, Keyword)
- Visualizations: Sentiment Chart, Entity Chart, Word Cloud
- Modern UI: Gradient sidebar, animations, responsive design

```

---

## 3. Folder Structure
```plaintext
NewsPulse/
│
├─ app/
│	├─   init  .py
│	├─ routes.py
│	├─ models.py
│	├─ nlp_utils.py
│	├─ templates/
| |  ├─	base.html
| |  ├─	index.html
| |  ├─	dashboard.html
| |  ├─	login.html
| |  ├─	register.html
| |  ├─	profile.html
| |  └─	trending.html
|  └─ static/
|    ├─ css/
|     └─ style.css
|    └─ js/
|      └─ script.js
│	│	├─	base.html
│	│	├─	index.html
│	│	├─	dashboard.html
│	│	├─	login.html
│	│	├─	register.html
│	│	├─	profile.html
│	│	└─	trending.html






```


---

## 4. Technologies Used
```text
Backend: Flask, Flask-Login, SQLAlchemy (SQLite)
Frontend: HTML, CSS, Bootstrap 5
NLP: spaCy (entity extraction), TextBlob (sentiment analysis)
Visualization: Chart.js, WordCloud
Tools: dotenv, werkzeug

```

---

## 5. Installation & Setup
```
### Clone Repository
git clone https://github.com/username/NewsPulse.git
cd NewsPulse

### Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

### Install Dependencies
pip install -r requirements.txt

### Add environment variables in .env
SECRET_KEY=your_secret_key
NEWS_API_KEY=your_news_api_key

### Run the app
python run.py

```

---


## 6. Application Flow
```text
1. Home → Intro & Login/Register
2. Register/Login → Access Dashboard
3. Dashboard → Quick access to Trending News & Profile
4. Trending News → AI-powered analysis (sentiment, entities, word cloud)
5. Profile → Update user details
6. Logout → Secure session end
```

---

## 7. Future Enhancements
```text
- Dark mode toggle
- Real-time updates with WebSockets
- User-specific alerts (Telegram/Email)
- Advanced NLP (summarization, topic modeling)
```
