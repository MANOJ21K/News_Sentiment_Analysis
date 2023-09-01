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


# Function to extract text using BeautifulSoup
def beautifulsoup_extract_text_fallback(response_content):
        # Create the BeautifulSoup object:
    soup = BeautifulSoup(response_content, 'html.parser')
    
    # Finding the text:
    text = soup.find_all(text=True)
    
    # Remove unwanted tag elements:
    cleaned_text = ''
    blacklist = [
        '[document]',
        'noscript',
        'header',
        'html',
        'meta',
        'head', 
        'input',
        'script',
        'style',
    ]

    # Loop over every item in the extracted text and make sure that the BeautifulSoup4 tag
    # is NOT in the blacklist
    for item in text:
        if item.parent.name not in blacklist:
            cleaned_text += '{} '.format(item)
            
    # Remove any tab separation and strip the text:
    cleaned_text = cleaned_text.replace('\t', '')
    return cleaned_text.strip()

# Function to extract text from a single web page
def extract_text_from_single_web_page(url):
    resp = None  # Initialize resp variable
    try:
        resp = requests.get(url, timeout=30)  # Set timeout to 30 seconds
        resp.raise_for_status()  # Raise an exception if the status code is not 200
        downloaded_url = trafilatura.fetch_url(url)
        try:
            a = trafilatura.extract(downloaded_url, output_format="json", with_metadata=True, include_comments=False, date_extraction_params={'extensive_search': True, 'original_date': True})
        except AttributeError:
            a = trafilatura.extract(downloaded_url, output_format="json", with_metadata=True, date_extraction_params={'extensive_search': True, 'original_date': True})
        if a:
            json_output = json.loads(a)
            return json_output['text']
        else:
            return beautifulsoup_extract_text_fallback(resp.content)
    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
        if resp is not None:
            return " ".join(beautifulsoup_extract_text_fallback(resp.content).split()[:10])
        else:
            return np.nan