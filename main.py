""" 
Roblox API Example

An example to show my capabilities with roblox API (I had some fun doing this though, it was a nice challenge)

Author: AestheticLosing
"""

import matplotlib.pyplot as plt 
import api
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv(dotenv_path="Group-Income-Analytics/data/user_info.env")

# Variables 
COOKIE = os.getenv("COOKIE") # Get user cookie from user info csv file.
START_DATE = "2025-08-18" # just some random start date ig (not really important for now)
END_DATE = date.today().strftime("%Y-%m-%d") # current date

REQUESTS = { # API information for requests
    "universe_revenue_daily":{ # Requires universe id as data parameter (when getting request info)
        "url":"https://apis.roblox.com/analytics-query-gateway/v1/metrics/resource/RESOURCE_TYPE_UNIVERSE/id/{0}", 
        "payload":{
            "resourceType": "RESOURCE_TYPE_UNIVERSE",
            "resourceId": "{0}",
            "query": {
                "metric": "DailyRevenue",
                "granularity": "METRIC_GRANULARITY_ONE_DAY",
                "breakdown": [],
                "startTime": f"{START_DATE}T00:00:00.000Z",
                "endTime": f"{END_DATE}T00:00:00.000Z"
            }
        },
    },
    "group_ugc_revenue_daily":{ # requires group id as data parameter (when getting request info)
        "url":"https://apis.roblox.com/developer-analytics-aggregations/v1/metrics/avatar/owner/Group/{0}",
        "payload":{
            "metric": "Revenue",
            "granularity": "OneDay",
            "breakdown": ["Product"],
            "startTime": f"{START_DATE}T00:00:00.000Z",
            "endTime": f"{END_DATE}T00:00:00.000Z"
        }
    },
    "group_games":{ # requires group id as data parameter (when getting request info)
        "url":"https://apis.roblox.com/universes/v1/search?CreatorType=Group&CreatorTargetId={0}&IsArchived=false&PageIndex=0&PageSize=10&SortParam=LastUpdated&SortOrder=Desc", # Idk why the payload has to match a random query in the url for this to work, and why they can't just do it based on the payload but whatever
        "payload":{ # (idek if a payload is required for this one (common sense would say no with any basic api knowledge) but roblox's site does it so fuck it I'm too lazy to test it)
            "CreatorType":"Group",
            "CreatorTargetId:":"{0}",
            "IsArchived": False,
            "PageIndex": 0, 
            "PageSize": 10, # Change this later (kinda limiting but whatever I might just add some giant size fr) (prob have to change it in url as well cuz of how weird their api is fr) 
            "SortParam": "LastUpdated",
            "SortOrder": "Desc"
        }
    },
    "creator_groups":{
        "url":"https://apis.roblox.com/creator-home-api/v1/groups",
        "payload":{}
    }
}

API_REQUEST_COOKIES = { # This can be constant since there shouldn't be any other cookies I need to use, kinda just a formatting thing lol
    ".ROBLOSECURITY": COOKIE,
}

# Functions
def get_request_information(request_name:str, request_data:str = ""):
    """Gets url and payload information to be used to call an api

    Args:
        request_name (str): Name of the request type
        request_data (str): String used for the request (just a singular string for formatting)

    Returns:
        tuple: Returns a url and payload in (url,payload) format.
    """
    if request_name in REQUESTS.keys():
        request_info = REQUESTS[request_name].copy()
        formatted_url = request_info["url"].format(request_data)
        formatted_payload = request_info["payload"].copy()
        
        for key in formatted_payload:
            if type(formatted_payload[key]) == str:
                formatted_payload[key] = formatted_payload[key].format(request_data) # kinda brute forced this cuz im too lazy and I just wanted to speed run a more organized method for adding new api calls

        return formatted_url,formatted_payload

def parse_game_revenue_data(api_json,result={}):
    """Converts api json data into python dict

    Args:
        api_json (json): api response json

    Returns:
        dict[string,integer]: Dictionary of data retrieved from api json [date,value]
    """
    for i in range(len(api_json["operation"]["queryResult"]["values"])): 
        data_points = api_json["operation"]["queryResult"]["values"][i]["dataPoints"]
        for point in data_points:
            time = point["time"][0:10]
            value = point["value"]
            
            if time in result.keys():
                result[time] += value
            else:
                result[time] = value
    
    return result

def parse_ugc_revenue_data(api_json,result={}):
    """Converts api json data into python dict

    Args:
        api_json (json): api response json

    Returns:
        dict[string,integer]: Dictionary of data retrieved from api json [date,value]
    """
    for i in range(len(api_json["values"])):
        data_points = api_json["values"][i]["datapoints"]
        for point in data_points:
            time = point["timestamp"][0:10]
            value = point["value"]
            
            if time in result.keys():
                result[time] += value
            else:
                result[time] = value
    
    return result

def parse_group_games_data(api_json,result={}):
    """Converts api json data into python dict

    Args:
        api_json (json): api response json

    Returns:
        dict[string,string]: Dictionary of data retrieved from api json [universe_id,game_name] # Must say I love the fact it deals with universe id and not some stupid main place id cuz that'd be hella annoying lowk
    """
    for i in range(len(api_json["data"])):
        group_info = api_json["data"][i]
        result[group_info["id"]] = group_info["name"]
    
    return result

def parse_creator_groups_data(api_json,result={}):
    """Converts api json data into python dict

    Args:
        api_json (json): api response json

    Returns:
        dict[string,string]: Dictionary of data retrieved from api json [group_name,group_id]
    """
    for i in range(len(api_json["groups"])):
        group_info = api_json["groups"][i]
        result[group_info["name"]] = group_info["id"]
    
    return result

def main(): # Yes this is all messy, I kinda speed ran it cuz I have very limited time and I want to get as much done as possible :sob:
    url,payload = get_request_information("creator_groups") # API Call to fetch roblox creator groups (groups that display on the creator page on roblox)
    raw_groups_data = api.make_get_request(url,API_REQUEST_COOKIES,payload)
    
    if raw_groups_data:
        groups_dict = parse_creator_groups_data(raw_groups_data)
        
        for group_name in groups_dict: # Iterate through roblox groups user has developer metrics access to
            id = groups_dict[group_name] # Group ID
            ugc_graph_data = {}
            games_graph_data = {}
            total_graph_data = {}
            group_games = {}
            total_revenue = 0
            average_revenue = 0
    
            url,payload = get_request_information("group_ugc_revenue_daily",id) # Get group UGC revenue info (per day format)
            raw_ugc_rev_data = api.make_post_request(url,API_REQUEST_COOKIES,payload)
            
            if raw_ugc_rev_data:
                total_graph_data = parse_ugc_revenue_data(raw_ugc_rev_data,ugc_graph_data)
            
            url,payload = get_request_information("group_games",id) # Get group games
            raw_group_games_data = api.make_get_request(url,API_REQUEST_COOKIES,payload)

            if raw_group_games_data:
                group_games = parse_group_games_data(raw_group_games_data,{})
                
                for game_id in group_games:
                    url,payload = get_request_information("universe_revenue_daily",game_id) # Get universe revenue
                    raw_universe_rev_data = api.make_post_request(url,API_REQUEST_COOKIES,payload)
                    
                    if raw_universe_rev_data:
                        parse_game_revenue_data(raw_universe_rev_data,games_graph_data) 
            
            games_timestamps = games_graph_data.keys()
            ugc_timestamps = ugc_graph_data.keys()
            
            total_graph_data.update(games_graph_data) # Merge games graph data into total
                    
            for timestamp in total_graph_data.keys(): # Set any missing graph data to 0 for a better look on plots
                if not timestamp in games_timestamps:
                    games_graph_data[timestamp] = 0
                
                if not timestamp in ugc_timestamps:
                    ugc_graph_data[timestamp] = 0
            
            total_revenue = sum(total_graph_data.values())
            average_revenue = total_revenue // max(len(total_graph_data.keys()),1)
            
            if total_revenue > 0: # Only display graph if game has revenue 
                plt.figure(group_name)
                plt.plot(list(ugc_graph_data.keys()),list(ugc_graph_data.values()),label = "UGC Revenue")
                plt.plot(list(games_graph_data.keys()),list(games_graph_data.values()),label = "Games Revenue")
                plt.plot(list(total_graph_data.keys()),list(total_graph_data.values()),label="Total")
                
                plt.xlabel("Dates")
                plt.ylabel("Robux Earned")
                plt.title(f"Average over selected period: {average_revenue} | Total over selected period: {total_revenue}")
                
                timestamps = total_graph_data.keys()
                plt.xticks( # I had to look this part up cuz I've used matplotlib like 4 times ever in my life LOL idk ts
                    ticks=range(len(timestamps)),
                    labels=[key if i % (3) == 0 else '' for i, key in enumerate(timestamps)],
                    rotation=45, ha='right'
                )
                
                plt.legend()
                plt.tight_layout()
                plt.gcf().canvas.manager.set_window_title(group_name)
                
        plt.show()

# Task(s)
if __name__ == "__main__":
    main()