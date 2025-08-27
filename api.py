""" 
Handles roblox API calls

Author: AestheticLosing
"""
import requests
import time

# Variables
SESSION = requests.Session() # Requests Session
HEADERS = { # I'm ngl this should probably remain constant through any API calls I should need to do here
    "Content-Type": "application/json",
    "origin": "https://create.roblox.com",
    "referer": "https://create.roblox.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "Accept":"*/*"
}

csrf_token = "" # csrf_token variable to be used later
last = 0

# Functions
def make_post_request(url : str, cookies : dict, payload : dict, fetched=False):
    """Makes an API post request from the given parameters
    
    * FORMATED FOR ROBLOX API ONLY *

    Args:
        url (str): url for API request
        cookies (dict): cookies needed for authentication
        payload (dict): request information

    Raises:
        Exception: An unexpected API response code was thrown

    Returns:
        json: JSON response from API
    """
    global last
    global csrf_token # Haven't done this in a while
    
    current_time = time.time()
    
    if last > 0:
        print(f"Time since last API call: {current_time - last} seconds, URL: {url}")
    last = current_time
        
    header = HEADERS.copy()
    header["X-CSRF-TOKEN"] = csrf_token
    
    # curr = time.time()
    # if curr - last <= CALL_INTERVAL:
    #     time.sleep(max(0,CALL_INTERVAL - (curr - last)))
    # last = curr
    
    response = SESSION.post(url, headers=header, cookies=cookies, json=payload)
    if response.status_code == 403 and not fetched:
        csrf_token = response.headers.get("x-csrf-token")
        return make_post_request(url,cookies,payload,fetched=True)
    elif response.status_code == 200:
        return response.json()
    else: # Might pass this 
        return None
        # raise Exception(f"Unexpected response: {response.status_code} - {response.text}")
    
def make_get_request(url : str, cookies : dict, payload : dict, fetched=False):
    """Makes an API get request from the given parameters
    
    * FORMATED FOR ROBLOX API ONLY *

    Args:
        url (str): url for API request
        cookies (dict): cookies needed for authentication
        payload (dict): request information

    Raises:
        Exception: An unexpected API response code was thrown

    Returns:
        json: JSON response from API
    """
    global last
    global csrf_token
    
    header = HEADERS.copy()
    header["X-CSRF-TOKEN"] = csrf_token
    
    # curr = time.time()
    # if curr - last <= CALL_INTERVAL:
    #     time.sleep(max(0,CALL_INTERVAL - (curr - last)))
    # last = curr
    
    response = SESSION.get(url, headers=header, cookies=cookies, json=payload)
    if response.status_code == 403 and not fetched:
        csrf_token = response.headers.get("x-csrf-token")
        return make_get_request(url,cookies,payload,fetched=True)
    elif response.status_code == 200:
        return response.json()
    else: # Might pass this if api throws response code if group has no UGC items and just handle lack of json in main
        return None
        # raise Exception(f"Unexpected response: {response.status_code} - {response.text}")