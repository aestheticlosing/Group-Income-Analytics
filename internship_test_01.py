""" 
Roblox API Example

An example to show my capabilities with roblox API (I had some fun doing this though, it was a nice challenge)

Author: AestheticLosing
"""

import requests
import matplotlib.pyplot as plt 

COOKIE = "INSERT COOKIE HERE" # Roblox account cookie (obv must have some sort of access to developer analytics for the game you're providing below)
UNIVERSE_ID = "0" # UNIVERSE ID (this is like the most simple api request to get so don't discredit me on this for being lazy) (https://apis.roblox.com/universes/v1/places/INSERT_PLACE_ID_HERE_IM_LAZY_LOL/universe)
START_DATE = "2025-07-28"
END_DATE = "2025-08-24"

# request stuff ig
url = f"https://apis.roblox.com/analytics-query-gateway/v1/metrics/resource/RESOURCE_TYPE_UNIVERSE/id/{UNIVERSE_ID}"

headers = {
    "Content-Type": "application/json",
    "origin": "https://create.roblox.com",
    "referer": "https://create.roblox.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
}

cookies = {
    ".ROBLOSECURITY": COOKIE,
}

payload = {
    "resourceType": "RESOURCE_TYPE_UNIVERSE",
    "resourceId": UNIVERSE_ID,
    "query": {
        "metric": "DailyRevenue",
        "granularity": "METRIC_GRANULARITY_ONE_DAY",
        "breakdown": [],
        "startTime": f"{START_DATE}T00:00:00.000Z",
        "endTime": f"{END_DATE}T00:00:00.000Z"
    }
}

# function stuff fr
def get_csrf_token(session):
    """Creates a csrf token for future api calls by sending an empty request and retrieving it from the response header.

    Args:
        session (requests.Session): Current python requests session

    Raises:
        Exception: No CSRF token was found in the response header
        Exception: An unexpected response code

    Returns:
        string: x_csrf_token to be used for calling the api
    """
    response = session.post(url, headers=headers, cookies=cookies, json=payload)
    if response.status_code == 403:
        csrf_token = response.headers.get("x-csrf-token")
        if csrf_token:
            return csrf_token
        else:
            raise Exception("CSRF token not found in response headers")
    elif response.status_code == 200:
        return None # Request succeeded without CSRF token (should never happen but whatever)
    else:
        raise Exception(f"Unexpected response: {response.status_code} - {response.text}")

def make_authenticated_request(session, csrf_token):
    """Sends a properly formatted api request 

    Args:
        session (requests.Session): Current python requests session
        csrf_token (string): x_csrf_token needed for api auth

    Returns:
        json: response json
    """
    auth_headers = headers.copy()
    auth_headers["X-CSRF-TOKEN"] = csrf_token

    response = session.post(url, headers=auth_headers, cookies=cookies, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Request failed: {response.status_code}")
        print(response.text)
        return None
    
def parse_revenue_data(api_json):
    """Converts api json data into 

    Args:
        api_json (json): api response json

    Returns:
        dict[string,integer]: Dictionary of data retrieved from api json
    """
    result = {}

    data_points = api_json["operation"]["queryResult"]["values"][0]["dataPoints"]
    for point in data_points:
        time = point["time"][0:10]
        value = point["value"]
        result[time] = value
    
    return result

def main():
    session = requests.Session() 
    csrf_token = get_csrf_token(session) # Create x-csrf-token for api call 
    
    if csrf_token:
        raw_json_data = make_authenticated_request(session, csrf_token) # call API
        
        if raw_json_data: # Can return None 
            data_dict = parse_revenue_data(raw_json_data) # Converts JSON Data into python dictionary (key = time, value = value) for graph
            total_earned = sum(data_dict.values()) # Total number of robux earned over selected values
            average_daily = total_earned // len(data_dict) # Average daily robux earned over selected period (Idk if it's supposed to be a decimal or not so I did floor division)   
            
            keys = data_dict.keys()
            values = data_dict.values()
            
            # Graph stuff
            plt.plot(list(keys),list(values))
            plt.xlabel("Dates")
            plt.ylabel("Robux Earned")
            plt.title(f"Average over selected period: {average_daily} | Total over selected period: {total_earned}") # Ik this is scuffed but it's whatever
            
            plt.xticks( # I had to look this part up cuz I've used matplotlib like 4 times ever in my life LOL idk ts
                ticks=range(len(keys)),
                labels=[key if i % 3 == 0 else '' for i, key in enumerate(keys)],
                rotation=45, ha='right'
            )
            
            plt.tight_layout()
            plt.gcf().canvas.manager.set_window_title("Daily Revenue") # I thought about doing another api request to put the game name here but im lowk too lazy cuz u get the point
            plt.show()

if __name__ == "__main__":
    main()