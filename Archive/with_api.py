from serpapi import GoogleSearch
import json

params = {
    "api_key": "4184d8a8571e23abc760f45d227d56f617e35351ba40282de763d1b96f3a3bb1",         # https://serpapi.com/manage-api-key
    "engine": "google",       # serpapi parsing engine
    "q": "coca cola",         # search query
    "tbm": "nws"              # news results
}

search = GoogleSearch(params) # where data extraction happens
pages = search.pagination()   # returns an iterator of all pages

for page in pages:
    print(f"Current page: {page['serpapi_pagination']['current']}")

    for result in page["news_results"]:
        print(f"Title: {result['title']}\nLink: {result['link']}\n")