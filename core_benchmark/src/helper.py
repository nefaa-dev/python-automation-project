import json
import os
from typing import Tuple

from container import get_container_id


def core_json_to_api_infos(
    core_json_folder: str, available_containers: list
) -> Tuple[list, list, list]:
    core_json_files = [
        os.path.join(core_json_folder, f)
        for f in os.listdir(core_json_folder)
        if f.endswith(".json")
        if "timing_results" not in f
    ]

    # List of instance loads and containers
    loads_lists = []
    containers_lists = []
    original_filename_lists = []

    # Loop through all json files we're interested in
    for core_json_path in core_json_files:
        print(core_json_path)
        with open(core_json_path) as f:
            core_json_dict = json.load(f)

        # Change item keys to correspond to api format:
        instance_items_list = core_json_dict["items"]
        for item in instance_items_list:
            item.pop("item_id")
            item_name = item.pop("item_name")
            item["productName"] = item_name
            if "diameter" not in item:
                item["diameter"] = None
            if "length" not in item:
                item["length"] = None
            if "width" not in item:
                item["width"] = None
            item_count = item.pop("count")
            item["quantity"] = item_count
            orientation = item.pop("orientation")
            item["rotation"] = orientation
            orientation = item.pop("stacking_ground")
            item["stackingGround"] = orientation
            stacking_on_top = item.pop("stacking_on_top")
            item["stackingOnTop"] = stacking_on_top
            unloading_priority = item.pop("unloading_priority")
            item["unloadingPriority"] = unloading_priority
            loading_priority = item.pop("loading_priority")
            item["loadingPriority"] = loading_priority
        loads_lists.append(instance_items_list)

        # Container list in api format.
        instance_container_list = []
        for core_container in core_json_dict["containers_data"]:
            if core_container["container_type"] != "AirPallet":
                raise ValueError("Not written for anything but air pallets at the moment.")
            name = core_container["air_pallet_info"]["iata_code"]
            if core_container["air_pallet_info"]["contour"]:
                name += " "
                name += core_container["air_pallet_info"]["contour"]

            if "-F" not in name:
                # Skip "-F" since the corresponding unwinged should already exist and back end will
                # add it with the correct flag is enabled.
                container_id = get_container_id(name, available_containers)
                instance_container_list.append(
                    {
                        "containerId": container_id,
                        "count": core_container["count"],
                        "isWingedContourEnabled": True,
                    }
                )
        containers_lists.append(instance_container_list)
        original_filename_lists.append(core_json_path)

    return loads_lists, containers_lists, original_filename_lists
