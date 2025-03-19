import datetime
from typing import Tuple

import requests
import setup


def create_and_post_loads_from_list_of_items(
    list_of_item_loads: list, runs_payloads_list: list
) -> Tuple[list, dict, dict]:
    # Initialize an empty list to store load IDs
    load_ids_list = []
    load_api_url = f"{setup.api_url}/api/v1/loads"
    load_id_to_run_json_mapping = {}
    load_id_to_tot_item_count = {}
    # Loop through each JSON file in the folder
    for instance_number, item_list in enumerate(list_of_item_loads):
        org_name = "ups"
        date_time = str(datetime.datetime.now())
        date_time = date_time.replace("-", "")
        date_time = date_time.replace(" ", "")
        date_time = date_time.replace(":", "")
        date_time = date_time.replace(".", "")
        json_data = {
            "name": f"{org_name}_{instance_number}_{date_time}",
            "isUnloadingPriorityEnabled": False,
            "transportationMode": "Air",
            "items": item_list,
        }
        tot_item_count = sum(item["quantity"] for item in item_list)
        # Make the API call
        response = requests.post(load_api_url, json=json_data, headers=setup.headers)

        # Print the response for debugging
        print(f"Response for load {instance_number}: {response.status_code} - {response.text}")

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response JSON
            response_json = response.json()

            if not response_json["errorCode"]:
                # Extract and append the load ID to the list
                print("Added ok")
                load_id = response_json.get("result")
                load_ids_list.append(load_id)
                load_id_to_run_json_mapping[load_id] = runs_payloads_list[instance_number]
                load_id_to_tot_item_count[load_id] = tot_item_count
        else:
            print(
                f"Error making API request for load: {response.status_code} " f"- {response.text}"
            )
    return load_ids_list, load_id_to_run_json_mapping, load_id_to_tot_item_count
