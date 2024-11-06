from typing import Iterator
import random


def generate_random_string(length):
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits + string.whitespace, k=length))


RANDOM_TEXT = "By default, the k-NN plugin supports the indexing and querying of vectors of type float, where each dimension of the vector occupies 4 bytes of memory. For use cases that require ingestion on a large scale, keeping float vectors can be expensive because OpenSearch needs to construct, load, save, and search graphs (for native nmslib and faiss engines). To reduce the memory footprint, you can use vector quantization."

MOCK_X_IDS = [f"{i}" for i in range(100)]
MOCK_Y_IDS = [f"{i}" for i in range(100)]
MOCK_Z_IDS = [f"{i}" for i in range(100)]


def flatten_filters(data, prefix=""):
    result = []

    for i in range(data["values_count"]):
        base_value = f"{prefix}{data['name']}_{i}"
        current_level = {
            "name": data["name"],
            "type": data["type"],
            "value": base_value
        }

        if "next_level" in data:
            # Get next level combinations and append current level to each combination
            next_level_combinations = flatten_filters(data["next_level"],
                                                      prefix=base_value + "_")
            for combination in next_level_combinations:
                result.append([current_level] + combination)
        else:
            # If no further levels, add as a single-level group
            result.append([current_level])

    return result


def read_payloads(index: int) -> dict:
    return {
        "x_id": random.choice(MOCK_X_IDS),
        "y_id": random.choice(MOCK_Y_IDS),
        "z_id": random.choice(MOCK_Z_IDS),
        "type": "kbarticle",
        "chunking_strategy": "default",
        "body_text": RANDOM_TEXT,
        "item_id": index
    }
