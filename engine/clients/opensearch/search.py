import multiprocessing as mp
import uuid
from typing import List, Tuple

from opensearchpy import OpenSearch

from dataset_reader.base_reader import Query
from engine.base_client.search import BaseSearcher
from engine.clients.opensearch.config import (
    OPENSEARCH_INDEX,
    OPENSEARCH_PASSWORD,
    OPENSEARCH_PORT,
    OPENSEARCH_USER,
)
from engine.clients.opensearch.parser import OpenSearchConditionParser


class ClosableOpenSearch(OpenSearch):
    def __del__(self):
        self.close()


def _get_hit_id(hit):
    id_from_payload = hit.get("_source", {}).get("item_id")
    return id_from_payload if id_from_payload else uuid.UUID(hex=hit["_id"]).int


class OpenSearchSearcher(BaseSearcher):
    search_params = {}
    client: OpenSearch = None
    parser = OpenSearchConditionParser()

    @classmethod
    def get_mp_start_method(cls):
        return "forkserver" if "forkserver" in mp.get_all_start_methods() else "spawn"

    @classmethod
    def init_client(cls, host, distance, connection_params: dict, search_params: dict):
        init_params = {
            **{
                "verify_certs": False,
                "request_timeout": 90,
                "retry_on_timeout": True,
            },
            **connection_params,
        }
        cls.client: OpenSearch = OpenSearch(
            f"http://{host}:{OPENSEARCH_PORT}",
            basic_auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD),
            **init_params,
        )
        cls.search_params = search_params
        cls.use_post_filter = search_params.get("use_post_filter", False)
        cls.use_boolean_post_filter = search_params.get("use_boolean_post_filter", False)

    @classmethod
    def search_one(cls, query: Query, top: int) -> List[Tuple[int, float]]:
        opensearch_query = {
            "knn": {
                "vector": {
                    "vector": query.vector,
                    "k": top,
                }
            }
        }

        meta_conditions = cls.parser.parse(query.meta_conditions)

        if cls.use_boolean_post_filter:
            opensearch_query["knn"]["vector"]["k"] = round(top * 3)
            search_body = {
                "size": top,
                "query": {
                    "bool": {
                        "must": [opensearch_query],
                        "filter": meta_conditions,
                    }
                },
            }
        elif cls.use_post_filter:
            opensearch_query["knn"]["vector"]["k"] = round(top * 3)
            search_body = {
                "query": opensearch_query,
                "size": top,
                "post_filter": meta_conditions
            }
        else:
            if meta_conditions:
                opensearch_query["knn"]["vector"]["filter"] = meta_conditions
            search_body = {
                "query": opensearch_query,
                "size": top,
            }

        res = cls.client.search(
            index=OPENSEARCH_INDEX,
            body=search_body,
            params={
                "timeout": 60,
            },
        )
        return [
            (_get_hit_id(hit), hit["_score"])
            for hit in res["hits"]["hits"]
        ]

    @classmethod
    def setup_search(cls):
        if cls.search_params:
            cls.client.indices.put_settings(
                body=cls.search_params["config"], index=OPENSEARCH_INDEX
            )
