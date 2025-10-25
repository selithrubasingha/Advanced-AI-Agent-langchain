from dotenv import load_dotenv
import os
import requests
from urllib.parse import quote_plus
import json
from dotenv import load_dotenv

load_dotenv()


def _make_api_request(url,**kwargs):
    api_key = os.getenv("BRIGHTDATA_API_KEY")

    headers = {
        "Authorization":f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url , headers=headers, **kwargs)

        print(f"Status Code: {response.status_code}")

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except Exception as e:
        print(f"Unknown error: {e}")
        return None


import json



def serp_search(query):
    base_url = "https://www.google.com/search"

    url =  "https://api.brightdata.com/request"

    payload = {
        "zone": "ai_agent",
        "url": f"{base_url}?q={quote_plus(query)}&brd_json=1",
        "format": "raw"
    }

    full_response = _make_api_request(url,json=payload)

    if not full_response:
        return None

    extracted_data = {#full response is a LARGE json string but only need to
        #get the relavent data strings
        "knowledge": full_response.get("knowledge", {}),
        "organic": full_response.get("organic", []),
    }
    return extracted_data #gives a json output



def reddit_search_api(keyword, num_of_posts=3):



    trigger_url = "https://api.brightdata.com/datasets/v3/scrape?dataset_id=gd_lk56epmy2i5g7lzu0k&notify=false&include_errors=true&type=discover_new&discover_by=keyword"

    data = json.dumps({
        "input": [
            {"keyword": "popular music", "num_of_posts": "2", "start_date": "01-01-2024", "end_date": "03-31-2024",
             "country": ""}]})

    response = _make_api_request(trigger_url,data=data)

    print(response)

reddit_search_api(" ")






