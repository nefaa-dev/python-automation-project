import json
import os

import helper
import load
import run
from container import get_containers

if __name__ == "__main__":
    # input_data_batch_directory = "/mnt/deep-pack/client_data/ups/finite/nb_container_types_2"
    input_data_batch_directory = os.environ["CI_PROJECT_DIR"] + "/packing-data/client_data/"
    input_data_batch_directory += "ups_sorted_for_inference/finite/nb_container_types2"
    available_containers = get_containers()
    (list_of_item_lists, containers_lists, original_filename_lists) = helper.core_json_to_api_infos(
        input_data_batch_directory, available_containers
    )
    index_filename_mapping = dict(enumerate(original_filename_lists))

    # We define this before posting the loads so that we can map the loads to the containers we
    # sent for that load.
    vol_min = 1
    ship_max = 2
    load_planning = vol_min if "infinite" in input_data_batch_directory else ship_max
    runs_payloads_list = run.define_run_payloads_from_list(
        containers_lists,
        load_planning=load_planning,
        execution_mode=1,
    )

    (
        loads_ids_list,
        load_id_to_run_json_mapping,
        load_id_to_tot_item_count,
    ) = load.create_and_post_loads_from_list_of_items(list_of_item_lists, runs_payloads_list)

    # Run batches with corresponding container json
    responses_list, load_ids_response_order, input_filenames_response_order = run.create_batch_runs(
        loads_ids_list, load_id_to_run_json_mapping
    )

    # Extract scores
    available_containers_dictionary = {
        container["id"]: container for container in available_containers
    }
    data_list = run.extract_results(
        responses_list,
        load_ids_response_order,
        input_filenames_response_order,
        available_containers_dictionary,
        load_id_to_tot_item_count,
        index_filename_mapping,
    )

    if not os.path.exists(os.environ["CI_PROJECT_DIR"] + "/core_benchmark/results"):
        os.makedirs(os.environ["CI_PROJECT_DIR"] + "/core_benchmark/results")
    # TODO create results
    with open(os.environ["CI_PROJECT_DIR"] + "/core_benchmark/results/results.json", "w") as fp:
        json.dump(data_list, fp)
