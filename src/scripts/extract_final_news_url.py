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



def beautifulsoup_extract_text_fallback(response_content):
    
    # Create the beautifulsoup object:
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
        'style',]

    # Then we will loop over every item in the extract text and make sure that the beautifulsoup4 tag
    # is NOT in the blacklist
    for item in text:
        if item.parent.name not in blacklist:
            cleaned_text += '{} '.format(item)
            
    # Remove any tab separation and strip the text:
    cleaned_text = cleaned_text.replace('\t', '')
    return cleaned_text.strip()

def final_news_url(url):
    downloaded_url = trafilatura.fetch_url(url)
    try:
        a = trafilatura.extract(downloaded_url, output_format="json", with_metadata=True, include_comments=False, date_extraction_params={'extensive_search': True, 'original_date': True})
    except AttributeError:
        a = trafilatura.extract(downloaded_url, output_format="json", with_metadata=True, date_extraction_params={'extensive_search': True, 'original_date': True})
    if a:
        json_output = json.loads(a)
        return json_output['text']
    else:
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                return beautifulsoup_extract_text_fallback(resp.content)
            else:
                return np.nan
        except MissingSchema:
            return np.nan