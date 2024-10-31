import time

import typer
import requests
import os
import json
from dataset_reader import mock_payload

app = typer.Typer()


def _get_data_count(engine_name: str, server_host: str):
    try:
        if "qdrant" in engine_name:
            url = f"http://{server_host}:16333/collections/benchmark"
            response = requests.get(url)
            return response.json()["result"]["points_count"]
        elif "opensearch" in engine_name:
            url = f"http://{server_host}:29200/bench/_count"
            response = requests.get(url)
            return response.json()["count"]
        else:
            return -1
    except Exception as e:
        print("Error while getting data count", e)
        return -1


@app.command()
def run(
        engine_name: str = typer.Option(..., help="Engine name"),
        server_host: str = typer.Option(..., help="Server host"),
        dataset_name: str = typer.Option(..., help="Dataset name"),
):
    print("Running")
    filter_config = os.getenv('FILTER_CONFIG')

    with open("./filter_config.json") as json_file:
        filter_config = json.load(json_file).get(filter_config, {})

    distinct_filter = filter_config.get("distinct_fields")
    distinct_data_size = filter_config.get("distinct_data_size", 1)
    flattened_filters = mock_payload.flatten_filters(distinct_filter)
    print("Flattened filters size:", len(flattened_filters))

    triggered_group = set()
    while True:
        time.sleep(5)
        data_count = _get_data_count(engine_name, server_host)
        if data_count == -1:
            print("Error while getting data count. Retrying...")
            continue
        if data_count == 0:
            print("Data count is 0. Retrying...")
            continue
        latest_uploaded_group = data_count // distinct_data_size
        print(f"Data count: {data_count} Latest uploaded group: {latest_uploaded_group}")

        for group in range(latest_uploaded_group):
            if group in triggered_group:
                continue
            filter_for_group = flattened_filters[group]
            print("Triggering for group:", group, filter_for_group)
            triggered_group.add(group)

        if latest_uploaded_group >= len(flattened_filters):
            print("All groups are triggered")
            break


if __name__ == '__main__':
    app()
