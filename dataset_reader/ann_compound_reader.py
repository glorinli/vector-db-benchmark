import json
from typing import Iterator, List
import os

import numpy as np
from pathlib import Path

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
        self.mock_payload = os.getenv('MOCK_PAYLOAD') == 'true'
        print(f"MOCK_PAYLOAD: {self.mock_payload}")

    def read_payloads(self) -> Iterator[dict]:
        if self.mock_payload:
            index = 0
            while True:
                yield mock_payload.read_payloads(index)
                index += 1
        else:
            return super().read_payloads()

    def read_vectors(self) -> Iterator[List[float]]:
        vectors = np.load(self.path / self.VECTORS_FILE)
        for vector in vectors:
            if self.normalize:
                vector = vector / np.linalg.norm(vector)
            yield vector.tolist()

    def read_queries(self) -> Iterator[Query]:
        mock_meta_conditions = {
            "and": [
                {"a_id": {"match": {"value": "a_id"}}},
                # {"g_id": {"match": {"value": "g_id"}}},
                # {"type": {"match": {"value": "kbarticle"}}},
                # {"chunking_strategy": {"match": {"value": "default"}}},
            ]
        } if self.mock_payload else None

        with open(self.path / self.QUERIES_FILE) as payloads_fp:
            for idx, row in enumerate(payloads_fp):
                row_json = json.loads(row)
                vector = np.array(row_json["query"])
                if self.normalize:
                    vector /= np.linalg.norm(vector)
                yield Query(
                    vector=vector.tolist(),
                    sparse_vector=None,
                    meta_conditions=mock_meta_conditions if mock_meta_conditions else row_json["conditions"],
                    expected_result=row_json["closest_ids"],
                    expected_scores=row_json["closest_scores"],
                )
