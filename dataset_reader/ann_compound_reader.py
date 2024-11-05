import json
import os
from pathlib import Path
from typing import Iterator, List

import numpy as np

from dataset_reader.base_reader import Query
from dataset_reader.json_reader import JSONReader
from dataset_reader import mock_payload


class AnnCompoundReader(JSONReader):
    """
    A reader created specifically to read the format used in
    https://github.com/qdrant/ann-filtering-benchmark-datasets, in which vectors
    and their metadata are stored in separate files.
    """

    VECTORS_FILE = "vectors.npy"
    QUERIES_FILE = "tests.jsonl"

    def __init__(self, path: Path, normalize=False):
        super().__init__(path, normalize)

        filter_config = os.getenv('FILTER_CONFIG')
        with open("./filter_config.json") as json_file:
            self.filter_config = json.load(json_file).get(filter_config, {})

    def _get_filters(self) -> list[list]:
        distinct_filter = self.filter_config.get("distinct_fields")

        flattened_filters = mock_payload.flatten_filters(distinct_filter)

        return flattened_filters

    def read_payloads(self) -> Iterator[dict]:
        if self.filter_config:
            distinct_data_size = self.filter_config.get("distinct_data_size", 1)
            filters = self._get_filters()
            for filter_group in filters:
                # Map each item's name to value
                for item_index in range(distinct_data_size):
                    extra_payload = mock_payload.read_payloads(item_index)
                    yield {item["name"]: item["value"] for item in filter_group} | extra_payload
        else:
            return super().read_payloads()

    def read_vectors(self) -> Iterator[List[float]]:
        vectors = np.load(self.path / self.VECTORS_FILE)

        count = 1
        if self.filter_config:
            filters = self._get_filters()
            count = len(filters)

        print(f"Vector read Count: {count}")

        for _ in range(count):
            for vector in vectors:
                if self.normalize:
                    vector = vector / np.linalg.norm(vector)
                yield vector.tolist()

    def read_queries(self) -> Iterator[Query]:
        mock_meta_conditions = []
        override_filter_config = os.getenv('OVERRIDE_FILTER_CONFIG')
        if override_filter_config:
            filter_group = json.loads(override_filter_config)
            mock_meta_conditions = [
                {
                    "and": [{item.get("name"): {"match": {"value": item.get("value")}} for item in filter_group}]
                }
            ]
        elif self.filter_config:
            filters = self._get_filters()
            # Pick filters every 10th query
            for i in range(0, 12, 5):
                filter_group = filters[i]
                mock_meta_conditions.append({
                    "and": [{item.get("name"): {"match": {"value": item.get("value")}} for item in filter_group}]
                })
        else:
            mock_meta_conditions = [None]

        for condition in mock_meta_conditions:
            if condition:
                and_cond = condition["and"]
                and_cond.append({"type": {"match": {"value": "kbarticle"}}})
                and_cond.append({"chunking_strategy": {"match": {"value": "default"}}})

        print(f"Condition count: {len(mock_meta_conditions)}")

        if mock_meta_conditions[0]:
            print(f"Condition: {mock_meta_conditions[0]}")

        for condition in mock_meta_conditions:
            with open(self.path / self.QUERIES_FILE) as payloads_fp:
                for idx, row in enumerate(payloads_fp):
                    row_json = json.loads(row)
                    vector = np.array(row_json["query"])
                    if self.normalize:
                        vector /= np.linalg.norm(vector)
                    yield Query(
                        vector=vector.tolist(),
                        sparse_vector=None,
                        meta_conditions=condition,
                        expected_result=row_json["closest_ids"],
                        expected_scores=row_json["closest_scores"],
                    )
