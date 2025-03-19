import json
import os
from typing import cast

import requests
import setup


def get_containers() -> list:
    containers_api_url = f"{setup.api_url}/api/v1/containers"
    # Make the POST request with headers
    # response = requests.get(containers_api_url, headers=setup.headers)
    response = requests.get(containers_api_url, headers=setup.headers)

    if response.status_code == 200:
        response_body = response.json()
        print(
            "Successful Request for getting containers, with error code : "
            f"{response_body['errorCode']}, status code: {response.status_code}"
        )
    else:
        raise RuntimeError(
            f"Error getting containers. Status code: {response.status_code}, "
            f"Response: {response.text}"
        )

    response_body = response.json()

    containers_list = response_body["result"]
    if not os.path.exists("~/multi_bin_packing/core_benchmark/results"):
        os.makedirs("~/multi_bin_packing/core_benchmark/results")
    # TODO create results
    with open("~/multi_bin_packing/core_benchmark/results/containers_list.json", "w") as fp:
        json.dump(containers_list, fp)

    return cast(list, containers_list)


def get_container_id(name: str, containers_list: list) -> str:
    for container in containers_list:
        if container["name"] == name:
            id = container["id"]
            return cast(str, id)
    raise ValueError(f"Container name {name} not found in containers_list.")
