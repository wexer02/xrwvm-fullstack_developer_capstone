"""Sentiment microservice using the course's bundled VADER lexicon."""
from pathlib import Path
import nltk
from flask import Flask, jsonify
from nltk.sentiment import SentimentIntensityAnalyzer

app = Flask(__name__)
nltk.data.path.insert(0, str(Path(__file__).parent))
analyzer = SentimentIntensityAnalyzer(lexicon_file='sentiment/vader_lexicon.zip/vader_lexicon/vader_lexicon.txt')


@app.get('/')
def home():
    return jsonify(service='Sentiment Analyzer', status='ready')


@app.get('/analyze/<path:text>')
def analyze_sentiment(text):
    score = analyzer.polarity_scores(text)['compound']
    sentiment = 'positive' if score >= 0.05 else 'negative' if score <= -0.05 else 'neutral'
    return jsonify(sentiment=sentiment)
