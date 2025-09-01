
# import spacy
# from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
# import nltk
# import torch

# # Download required NLTK data only once
# nltk.download('punkt', quiet=True)

# # -------------------------------
# # SpaCy NER
# # -------------------------------
# try:
#     nlp_spacy = spacy.load("en_core_web_sm")
# except OSError:
#     from spacy.cli import download
#     download("en_core_web_sm")
#     nlp_spacy = spacy.load("en_core_web_sm")

# # -------------------------------
# # Hugging Face Sentiment Analysis (POSITIVE / NEUTRAL / NEGATIVE)
# # -------------------------------
# MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"

# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
# model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, return_all_scores=False)

# # Mapping from model labels to readable labels
# LABEL_MAPPING = {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"}

# def analyze_text(text):
#     """
#     Analyze text for sentiment and named entities.
    
#     Parameters:
#         text (str): Input text to analyze.
        
#     Returns:
#         sentiment (str): Sentiment label (POSITIVE / NEUTRAL / NEGATIVE)
#         entities (list): List of tuples (entity_text, entity_label)
#     """
#     # -------------------------------
#     # Sentiment Analysis
#     # -------------------------------
#     try:
#         result = sentiment_pipeline(text)[0]
#         # Hugging Face model may return label as string or int, ensure int mapping
#         if isinstance(result['label'], str) and result['label'].isdigit():
#             label_idx = int(result['label'])
#         elif isinstance(result['label'], str):
#             # sometimes the label comes as 'LABEL_0', 'LABEL_1', 'LABEL_2'
#             label_idx = int(result['label'].split('_')[-1])
#         else:
#             label_idx = result['label']

#         sentiment = LABEL_MAPPING.get(label_idx, "UNKNOWN")
#     except Exception as e:
#         sentiment = f"Error: {e}"

#     # -------------------------------
#     # Named Entity Recognition
#     # -------------------------------
#     try:
#         doc = nlp_spacy(text)
#         entities = [(ent.text, ent.label_) for ent in doc.ents]
#     except Exception as e:
#         entities = [("Error", str(e))]

#     return sentiment, entities



# import spacy
# from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
# import nltk

# # Download required NLTK data silently
# nltk.download('punkt', quiet=True)

# # -------------------------------
# # Load SpaCy model for NER
# # -------------------------------
# try:
#     nlp_spacy = spacy.load("en_core_web_sm")
# except OSError:
#     from spacy.cli import download
#     download("en_core_web_sm")
#     nlp_spacy = spacy.load("en_core_web_sm")

# # -------------------------------
# # Load Hugging Face model for Sentiment Analysis
# # -------------------------------
# MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"

# try:
#     tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
#     model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
#     sentiment_pipeline = pipeline(
#         "sentiment-analysis",
#         model=model,
#         tokenizer=tokenizer,
#         return_all_scores=False
#     )
# except Exception as e:
#     sentiment_pipeline = None
#     print(f"[ERROR] Failed to load sentiment model: {e}")

# # Label mapping for sentiment output
# LABEL_MAPPING = {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"}


# def analyze_text(text: str):
#     """
#     Analyze text for sentiment and named entities.

#     Parameters:
#         text (str): Input text to analyze.

#     Returns:
#         sentiment (str): Sentiment label (POSITIVE / NEUTRAL / NEGATIVE)
#         entities (list): List of tuples (entity_text, entity_label)
#     """
#     sentiment = "UNKNOWN"
#     entities = []

#     # -------------------------------
#     # Sentiment Analysis
#     # -------------------------------
#     if sentiment_pipeline:
#         try:
#             result = sentiment_pipeline(text[:512])[0]  # Truncate for model limit
#             label_raw = result['label']

#             # Convert label to integer index
#             if isinstance(label_raw, str):
#                 if label_raw.isdigit():
#                     label_idx = int(label_raw)
#                 else:
#                     label_idx = int(label_raw.split('_')[-1])
#             else:
#                 label_idx = int(label_raw)

#             sentiment = LABEL_MAPPING.get(label_idx, "UNKNOWN")
#         except Exception as e:
#             sentiment = f"Error: {e}"

#     # -------------------------------
#     # Named Entity Recognition (NER)
#     # -------------------------------
#     try:
#         doc = nlp_spacy(text)
#         entities = [(ent.text, ent.label_) for ent in doc.ents]
#     except Exception as e:
#         entities = [("NER Error", str(e))]

#     return sentiment, entities



# # app/nlp_utils.py
# import spacy
# from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
# import nltk

# nltk.download('punkt', quiet=True)

# # Load SpaCy model
# try:
#     nlp_spacy = spacy.load("en_core_web_sm")
# except OSError:
#     from spacy.cli import download
#     download("en_core_web_sm")
#     nlp_spacy = spacy.load("en_core_web_sm")

# # Load Hugging Face sentiment model
# MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"
# try:
#     tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
#     model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
#     sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
# except Exception as e:
#     sentiment_pipeline = None
#     print(f"[ERROR] Failed to load sentiment model: {e}")

# LABEL_MAPPING = {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"}

# def analyze_text(text):
#     from textblob import TextBlob
#     import spacy
#     nlp = spacy.load("en_core_web_sm")

#     # Sentiment
#     blob = TextBlob(text)
#     polarity = blob.sentiment.polarity
#     if polarity > 0.1:
#         sentiment = "POSITIVE"
#     elif polarity < -0.1:
#         sentiment = "NEGATIVE"
#     else:
#         sentiment = "NEUTRAL"

#     # Entities
#     doc = nlp(text)
#     entities = [(ent.text, ent.label_) for ent in doc.ents]

#     # ✅ Return dict (not tuple!)
#     return {
#         "sentiment": sentiment,
#         "score": polarity,
#         "entities": entities
#     }



# def analyze_news(news_list):
#     """
#     Analyze a list of news articles.
#     Returns:
#         analyzed_news: list of dicts with sentiment & entities
#         top_entities: list of top 5 entities
#     """
#     analyzed_news = []
#     entity_count = {}

#     for news in news_list:
#         title = news.get("title", "")
#         desc = news.get("description", "")
#         text = f"{title} {desc}"
#         sentiment, entities = analyze_text(text)
#         analyzed_news.append({
#             "title": title,
#             "description": desc,
#             "sentiment": sentiment,
#             "entities": entities
#         })
#         for ent_text, _ in entities:
#             entity_count[ent_text] = entity_count.get(ent_text, 0) + 1

#     top_entities = sorted(entity_count.items(), key=lambda x: x[1], reverse=True)[:5]
#     return analyzed_news, top_entities





# app/nlp_utils.py
import spacy
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# -------------------------
# Load SpaCy model for NER
# -------------------------
try:
    nlp_spacy = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp_spacy = spacy.load("en_core_web_sm")

# -------------------------
# Load HuggingFace sentiment model
# -------------------------
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
except Exception as e:
    sentiment_pipeline = None
    print(f"[ERROR] Failed to load sentiment model: {e}")

# Mapping model labels → human-readable
LABEL_MAPPING = {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"}


# -------------------------
# Analyze a single text
# -------------------------
def analyze_text(text: str):
    """
    Analyze given text → sentiment + score + named entities
    """
    sentiment = "NEUTRAL"
    score = 0.0

    # ✅ Sentiment using HuggingFace pipeline
    if sentiment_pipeline:
        try:
            result = sentiment_pipeline(text[:512])[0]  # truncate to 512 tokens
            label = result["label"]
            score = float(result["score"])

            # HuggingFace labels like "LABEL_0"
            if label.startswith("LABEL_"):
                label_id = int(label.split("_")[1])
                sentiment = LABEL_MAPPING.get(label_id, "NEUTRAL")
            else:
                sentiment = label.upper()
        except Exception as e:
            print(f"[ERROR] Sentiment analysis failed: {e}")

    # ✅ Named Entity Recognition using SpaCy
    entities = []
    try:
        doc = nlp_spacy(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
    except Exception as e:
        print(f"[ERROR] NER failed: {e}")

    return {
        "sentiment": sentiment,
        "score": score,
        "entities": entities
    }


# -------------------------
# Analyze a list of news articles
# -------------------------
# def analyze_news(news_list):
#     """
#     Analyze a list of news articles.
#     Returns:
#         analyzed_news: list of dicts with sentiment & entities
#         top_entities: list of top 5 entities
#     """
#     analyzed_news = []
#     entity_count = {}

#     for news in news_list:
#         title = news.get("title", "")
#         desc = news.get("description", "")
#         text = f"{title} {desc}"

#         result = analyze_text(text)

#         analyzed_news.append({
#             "title": title,
#             "description": desc,
#             "sentiment": result["sentiment"],
#             "score": result["score"],
#             "entities": result["entities"]
#         })

#         for ent_text, _ in result["entities"]:
#             entity_count[ent_text] = entity_count.get(ent_text, 0) + 1

#     top_entities = sorted(entity_count.items(), key=lambda x: x[1], reverse=True)[:5]
#     return analyzed_news, top_entities
def analyze_news(news_list):
    """
    Analyze a list of news articles.
    Returns:
        analyzed_news: list of dicts with sentiment & entities
        top_entities: dict of top 5 entities with counts
    """
    analyzed_news = []
    entity_count = {}

    for news in news_list:
        title = news.get("title", "")
        desc = news.get("description", "")
        text = f"{title} {desc}"

        result = analyze_text(text)
        analyzed_news.append({
            "title": title,
            "description": desc,
            "sentiment": result["sentiment"],
            "score": result["score"],
            "entities": result["entities"]
        })

        for ent_text, _ in result["entities"]:
            entity_count[ent_text] = entity_count.get(ent_text, 0) + 1

    top_entities = dict(sorted(entity_count.items(), key=lambda x: x[1], reverse=True)[:5])
    return analyzed_news, top_entities
