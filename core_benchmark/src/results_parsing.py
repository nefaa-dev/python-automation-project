from datetime import datetime
from typing import Dict


def get_inference_run_time(run_result: Dict) -> float:
    date_format = "%Y-%m-%dT%H:%M:%S.%f"
    begin = datetime.strptime(run_result["createdOn"][:-6], date_format)
    end = datetime.strptime(run_result["finishedOn"][:-6], date_format)
    return (end - begin).total_seconds()


def get_container_guid_list(run_result: Dict) -> list:
    list_of_containers = run_result.get("containers", {}).get("data", [])
    if list_of_containers:
        return [container["id"] for container in list_of_containers]
    return []


def get_total_packed_container_volume_m3(
    run_result: Dict, guid_to_container_json_mapping: Dict
) -> float:
    # TODO: it would be better to do it this way but currently input guid and output guid are not
    # the same
    # packed_container_volume: float = sum(
    #     guid_to_container_json_mapping[guid].get("internalVolume")
    #     for guid in get_container_guid_list(run_result)
    # )
    guid_to_container_json_mapping
    packed_container_volume: float = sum(
        container["filledVolume"] / container["filledPercentage"]
        for container in run_result.get("containers", {}).get("data", [])
    )
    return packed_container_volume


def get_tot_unplaced_items_volume_mm3(run_result: Dict) -> float:
    remaining_items_vol: float = sum(
        item["item"]["height"] * item["item"]["length"] * item["item"]["width"]
        for item in run_result["remainingItems"]
    )
    return remaining_items_vol


def get_vol_in_final_bin_m3(run_result: Dict) -> float:
    list_of_containers = run_result.get("containers", {}).get("data", [])
    if list_of_containers:
        return float(list_of_containers[-1]["filledVolume"])
    return 0.0


def nb_items_packed(run_result: Dict) -> int:
    list_of_containers = run_result.get("containers", {}).get("data", [])
    total_items_packed_in_solution = sum(
        int(container["itemsCount"]) for container in list_of_containers
    )
    return total_items_packed_in_solution


def nb_items_unpacked(run_result: Dict) -> int:
    remaining_items_count: int = sum(
        item["remainingCount"] for item in run_result["remainingItems"]
    )
    return remaining_items_count
