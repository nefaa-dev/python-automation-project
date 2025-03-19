import json
import os
import time
from typing import Tuple

import requests
import setup
from results_parsing import (
    get_container_guid_list,
    get_inference_run_time,
    get_tot_unplaced_items_volume_mm3,
    get_total_packed_container_volume_m3,
    get_vol_in_final_bin_m3,
    nb_items_packed,
    nb_items_unpacked,
)


def define_run_payloads_from_list(
    containers_list: list, load_planning: int, execution_mode: int
) -> list:
    # Define the JSON payload which will be sent for the corresponding load
    payloads = [
        {
            "name": str(idx),
            "containers": containers,
            "loadPlanning": load_planning,
            "executionMode": execution_mode,
            "ignoreInvalidItems": False,
        }
        for idx, containers in enumerate(containers_list)
    ]
    return payloads


def create_batch_runs(
    load_ids: list, id_to_container_json_mapping: dict
) -> Tuple[list, list, list]:
    responses_list = []
    load_ids_list = []
    input_filenames_response_order = []
    for load_id in load_ids:
        # Define the URL with the load ID
        url = f"{setup.api_url}/api/v1/loads/{load_id}/runs"

        # Make the POST request with headers
        response = requests.post(
            url, json=id_to_container_json_mapping[load_id], headers=setup.headers
        )
        print(f"create run response :{response}")

        # Check the response status
        if response.status_code == 200:
            json_response = response.json()
            print(
                f"Successful Request for Run creation,for load ID: {load_id}, with error code: "
                f"{json_response['errorCode']}  and status code {response.status_code}"
            )
            if not json_response["errorCode"]:
                # Append the response JSON to the list
                responses_list.append(response.json())
                # Append the load_id to the list
                load_ids_list.append(load_id)
                input_filenames_response_order.append(id_to_container_json_mapping[load_id]["name"])
        else:
            print(
                f"Failed Request for Run creation run for load ID {load_id}. "
                f"Status code: {response.status_code}, Response: {response.text}"
            )

        # Introduce a delay
        time.sleep(3)
    return responses_list, load_ids_list, input_filenames_response_order


def extract_results(
    responses_list: list,
    load_ids_list: list,
    input_indexes: list,
    guid_to_container_json_mapping: dict,
    load_id_to_tot_item_count: dict,
    index_filename_mapping: dict,
) -> dict:
    # Create an empty list to store extracted information
    data_list = {}
    for i in range(len(load_ids_list)):
        load_id = load_ids_list[i]
        response_from_list = responses_list[i]
        original_input_file_name = index_filename_mapping[int(input_indexes[i])]
        original_input_file_name = os.path.split(original_input_file_name)[-1][:-5]
        if response_from_list:
            run_id = response_from_list.get("result", {}).get("runId")
            print(f"this is load is: {load_id}")
            # Format the API URL with the current runId and loadId
            # api_url = load_api_url.format(loadId=load_id, runId=run_id)
            api_url = f"{setup.api_url}/api/v1/loads/{load_id}/runs/{run_id}"
            print(f"this is the api_url: {api_url}")
            # Make the API call
            response = requests.get(api_url, headers=setup.headers)
            run_successful = response.status_code == 200
        else:
            run_successful = False

        # Process the response as needed
        if run_successful:
            response_json = response.json()
            result = response_json.get("result", {})
            run_request = result.get("runRequest", {})
            run_result = result.get("runResult", {})
            result_not_obtained_or_failed = (
                run_result.get("status", "") != "Succeeded"
                or run_result.get("status", "") != "Failed"
            )
            while result_not_obtained_or_failed:
                print(run_result.get("status", ""))
                response = requests.get(api_url, headers=setup.headers)
                response_json = response.json()
                result = response_json.get("result", {})
                run_request = result.get("runRequest", {})
                run_result = result.get("runResult", {})
                result_not_obtained_or_failed = (
                    run_result.get("status", "") != "Succeeded"
                    and run_result.get("status", "") != "Failed"
                )
            print(f"API call successful for runId={run_id}, loadId={load_id}")

            # Extract information from the response JSON
            response_json = response.json()
            result = response_json.get("result", {})
            run_request = result.get("runRequest", {})
            run_result = result.get("runResult", {})

            if not os.path.exists(os.environ["CI_PROJECT_DIR"] + "/core_benchmark/results"):
                os.makedirs(os.environ["CI_PROJECT_DIR"] + "/core_benchmark/results")
            with open(
                os.environ["CI_PROJECT_DIR"]
                + f"/core_benchmark/results/{original_input_file_name}_results.json",
                "w",
            ) as fp:
                json.dump(run_result, fp)

            # Print extracted information for debugging
            print(
                f"Extracted info for runId={run_id}, loadId={load_id}: {run_request}, {run_result}"
            )

            # Append extracted information to the list
            unplaced_mm3 = get_tot_unplaced_items_volume_mm3(run_result)
            packed_containers_m3 = get_total_packed_container_volume_m3(
                run_result, guid_to_container_json_mapping
            )
            vol_in_final_bin_m3 = get_vol_in_final_bin_m3(run_result)
            data = {
                "original_input_file_name": original_input_file_name,
                "runId": run_request.get("id"),
                "loadId": run_request.get("loadId"),
                "score": run_result.get("score"),
                "inference_run": get_inference_run_time(run_result),
                "container_guid_list": get_container_guid_list(run_result),
                "nb_containers": run_result.get("containers", {}).get("count", 0),
                "total_packed_container_volume": packed_containers_m3,
                "total_unpacked_items_volume": unplaced_mm3 / 1e9,
                "total_cost_volume_penalty_1": packed_containers_m3 + unplaced_mm3 / 1e9,
                "total_cost_volume_penalty_1e9": packed_containers_m3 + unplaced_mm3,
                "total_cost_volume_penalty_1_final_bin_vol": packed_containers_m3
                + unplaced_mm3 / 1e9
                + vol_in_final_bin_m3,
                "total_cost_volume_penalty_1e9_final_bin_vol": packed_containers_m3
                + unplaced_mm3
                + vol_in_final_bin_m3,
                "total_item_count_in_run": load_id_to_tot_item_count[load_id],
                "total_packed_item_count_in_result": nb_items_packed(run_result),
                # following line should be 0 in infinite container instances
                "total_unplaced_valid_items_in_solution": nb_items_unpacked(run_result),
            }
            if not os.path.exists(os.environ["CI_PROJECT_DIR"] + "/core_benchmark/results"):
                os.makedirs(os.environ["CI_PROJECT_DIR"] + "/core_benchmark/results")
            with open(
                os.environ["CI_PROJECT_DIR"]
                + f"/core_benchmark/results/{original_input_file_name}_summary.json",
                "w",
            ) as fp:
                json.dump(data, fp)
            data_list[original_input_file_name] = data

        else:
            data_list[original_input_file_name] = {"runfailed": "runfailed"}

    return data_list
