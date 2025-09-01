<img width="1136" height="128" alt="image" src="https://github.com/user-attachments/assets/6cb6047c-f2c5-4e70-811d-b8016590a1b8" /># NewsPulse - AI News Trend Analyzer
NewsPulse is a real-time news analyzer that fetches, visualizes, and performs sentiment analysis on trending news, helping users track news trends and insights effortlessly.

## Project Overview
NewsPulse is a modern web application that analyzes trending news using AI and NLP techniques. Users can view trending topics, filter news by category, country, or keyword, and gain insights through sentiment analysis, entity recognition, and visual dashboards.

## Features
### User Authentication
•	Register: Create a new account with username, email, and password.
•	Login: Access the dashboard using username or email with password.
•	Profile: Update username and email.
•	Logout: Securely log out from the application.

### Dashboard
•	Personalized welcome message for logged-in users.
•	Quick access cards to Trending Topics and Profile Settings.
•	Modern glassmorphic card design with hover effects.

### Trending News
•	Filter Options: Category, Country, Keyword.
•	Visualizations: Sentiment Chart, Entity Frequency Chart, Source Popularity Chart, Word Cloud.
•	News Cards: Display title, description, source, publication date, sentiment, entities, and link to original article.

### Modern UI
•	Gradient sidebar navigation for logged-in users.
•	Glassmorphic cards with blurred background effect.
•	Gradient buttons with hover animations.
•	Floating, rounded flash messages.
•	Fully responsive for mobile, tablet, and desktop.


## Folder Structure
NewsPulse/
│
├─ app/
│	├─   init  .py
│	├─ routes.py
│	├─ models.py
│	├─ nlp_utils.py
│	├─ templates/
│	│	├─	base.html
│	│	├─	index.html
│	│	├─	dashboard.html
│	│	├─	login.html
│	│	├─	register.html
│	│	├─	profile.html
│	│	└─	trending.html
  └─ static/
  └─ js/
  └─ script.js
├─ venv/
├─ .env
├─ requirements.txt
└─ run.py



## Technologies Used
•	Backend: Python, Flask, Flask-Login, SQLAlchemy (SQLite)
•	Frontend: HTML, CSS, Bootstrap 5, Google Fonts
•	NLP & AI: spaCy for entity extraction, TextBlob for sentiment analysis
•	Visualization: Chart.js, WordCloud
•	Other Tools: dotenv for environment variables, werkzeug for password security




## Installation and Setup
  ### Clone Repository 
  git clone https://github.com/username/NewsPulse.git cd NewsPulse
  
  ### Create Virtual Environment
  python -m venv venv source  venv/bin/activate
  venv\Scripts\activate

  ### Install Dependencies
  pip install -r requirements.txt
  
  ### Setup Environment Variables Create a	file:
  SECRET_KEY=your_secret_key 
  API_KEY=your_news_api_key

  ### Run the Application
  python run.py
  open http://127.0.0.1:5000/  in your browser.

  
  ### Application Flow
  
  	Home Page: Introduction with login/register options.
  	Register/Login: Account creation and login.
  	Dashboard: Quick access to Trending News and Profile.
  	Trending News: View AI-powered sentiment analysis, entity recognition, and word cloud.
  	Profile Page: Edit account details.
  	Logout: End user session securely.


  ### UI & UX Features
  Gradient sidebar for navigation
  • Glassmorphic cards with blur effect
  • Gradient buttons with smooth hover effects
  • Floating flash messages for notifications
  • Responsive design for all screen sizes
  • Charts and Word Cloud for data visualization

  ### Future Enhancements

  •	Dark mode toggle
  •	Real-time news updates with WebSockets
  •	User-specific news alerts
  •	Telegram/Email notifications for trending news
  •	Advanced NLP features: summarization, topic modeling

  

  

