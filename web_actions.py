from dotenv import load_dotenv
import os
import requests
from urllib.parse import quote_plus
import json
from dotenv import load_dotenv
from snapshot_operations import poll_snapshot_status,download_snapshot


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


def _trigger_and_download_snapshot(snapshot_id):


    #"snapshot_id" is built in in the json response I think

    if not snapshot_id:
        return None

    #if the status of the snapshot is not in the 200 s do this
    if not poll_snapshot_status(snapshot_id):
        return None

    #raw data is the snapshot!! but what is the snapshot??
    raw_data = download_snapshot(snapshot_id)


    return raw_data


import json


def shorten_video_data(data_list):
    """
    Extracts specific keys from a list of video data DICTIONARIES.
    """
    shortened_list = []

    # Ensure the input is a list, even if you just pass one item
    if not isinstance(data_list, list):
        data_list = [data_list]

    # The items in data_list are already dictionaries, not strings
    for video_dict in data_list:
        try:
            # We are working with a dict, so just use .get()
            video_info = {
                "title": video_dict.get("title"),
                "transcript": video_dict.get("transcript"),
                "views": video_dict.get("views"),
                "likes": video_dict.get("likes"),
                "description": video_dict.get("description"),
                "video_url": video_dict.get("video_url")
            }
            shortened_list.append(video_info)

        except AttributeError as e:
            # This will catch if data_list contains something other than dicts
            print(f"Skipping item: Item is not a dictionary. Error: {e}")
        except Exception as e:
            # Catches any other unexpected errors
            print(f"Skipping item: Unknown error. Error: {e}")

    return shortened_list



def reddit_search_api(keyword, num_of_posts=3):



    trigger_url = "https://api.brightdata.com/datasets/v3/scrape?dataset_id=gd_lk56epmy2i5g7lzu0k&notify=false&include_errors=true&type=discover_new&discover_by=keyword"

    data = json.dumps({
        "input": [

            {"keyword": "java course", "num_of_posts": "4"}],
    })

    response = _make_api_request(trigger_url,data=data)

    data=_trigger_and_download_snapshot(response["snapshot_id"])

    llm_input_data=shorten_video_data(data)

    print(llm_input_data)

    return  llm_input_data











