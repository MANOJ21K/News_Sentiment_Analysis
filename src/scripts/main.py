from bs4 import BeautifulSoup
import json
import numpy as np
import requests
from requests.models import MissingSchema
import trafilatura
from gnews import GNews
import pandas as pd
import re
import trafilatura
from extract_final_news_url import final_news_url
from extract_news_description import extract_text_from_single_web_page
from datetime import datetime

# Import the Summarizer class from the correct location
from summarizer import Summarizer

from transformers import BertTokenizer
from transformers import BertForSequenceClassification
from transformers import pipeline

class NewsDataUnstructured():
    
    def __init__(self, ticker):
        self.ticker = ticker
        self.df = None
        
    def extract_news_url(self):
        google_news = GNews()
        google_news.period = '1d'
        google_news.max_results = 5  # number of responses across a keyword
        google_news.country = 'United States'  # News from a specific country 
        google_news.language = 'english'  # News in a specific language
        #google_news.exclude_websites = ['yahoo.com', 'cnn.com']  # Exclude news from specific website i.e Yahoo.com and CNN.com
        #google_news.start_date = (2020, 1, 1) # Search from 1st Jan 2020
        #google_news.end_date = (2020, 3, 1) # Search until 1st March 2020  
        news = google_news.get_news(self.ticker)

        # Extract relevant fields using list comprehension
        df_data = [{'title': entry['title'], 'url': entry['url'],
                    'published_date': entry['published date'],
                    'publisher': entry['publisher']['title']} for entry in news]

        # Create DataFrame
        self.df = pd.DataFrame(df_data)
        return self.df

    def initial_preprocessing(self):
        self.df['Final_URL'] = ''
        self.df['Description'] = self.df['url'].apply(lambda x: final_news_url(url=x))
        
        # Regular expression pattern to match URLs
        url_pattern = r'https?://[^\s/$.?#].[^\s]*'
        
        self.df['Final_URL'] = self.df['Description'].apply(lambda text: re.findall(url_pattern, text)[0] if re.findall(url_pattern, text) else None)
        self.df['Description'].fillna(self.df['title'], inplace=True)
        return self.df

    def extract_final_news(self):
        self.df['Description'] = self.df['Final_URL'].apply(lambda url: extract_text_from_single_web_page(url=url) if url else None)
        self.df['Description'].fillna(self.df['title'], inplace=True)
        return self.df

    def process_data(self):
        self.extract_news_url()
        self.initial_preprocessing()
        self.extract_final_news()
        # Replace for loop with apply
        self.df['Description'].fillna(self.df['title'], inplace=True)
        return self.df

    def post_processing(self):
        processed_data = self.process_data()
        
        df = processed_data[['published_date', 'Description', 'publisher', 'title']]
        # After importing pandas and datetime
        df['Date'] = df['published_date'].apply(lambda x: datetime.strptime(x, "%a, %d %b %Y %H:%M:%S %Z"))

        # To avoid the SettingWithCopyWarning, use .loc to modify the DataFrame explicitly
        df.loc[:, 'Date'] = df['Date']

        # Print the DataFrame with the 'Date' column
        df = df.iloc[:, 1:]
        return df
    
    def get_description(self):
        df = self.post_processing()
        summarizer = Summarizer()
        
        df['Final_Description'] = ""
        df['Final_Description'] = df['Description'].apply(lambda x: summarizer(x, min_length=10, max_length=512))
        return df
    
    def get_sentiment(self):
        df = self.get_description()
        max_token_length = 500  # Set the maximum token length

        df['Sentiment'] = ''
        model = BertForSequenceClassification.from_pretrained("ahmedrachid/FinancialBERT-Sentiment-Analysis",num_labels=3)
        tokenizer = BertTokenizer.from_pretrained("ahmedrachid/FinancialBERT-Sentiment-Analysis")
        nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
        
        def analyze_sentiment(text):
            segments = [text[j:j+max_token_length] for j in range(0, len(text), max_token_length)]
            sentiments = []
            for segment in segments:
                results = nlp(segment)
                sentiments.extend(results)
            return sentiments

        df['Sentiment'] = df['Final_Description'].apply(analyze_sentiment)
        df['Label'] = df['Sentiment'].apply(lambda x: x[0]['label'])
        df['Score'] = df['Sentiment'].apply(lambda x: x[0]['score'])
        df = df.drop('Sentiment', axis=1)
        df = df[['Date', 'publisher', 'Final_Description', 'Label', 'Score']]
        return df
