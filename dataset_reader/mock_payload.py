from typing import Iterator
import random


def generate_random_string(length):
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits + string.whitespace, k=length))


RANDOM_TEXT = generate_random_string(1000)

MOCK_A_IDS = [f"{i}" for i in range(100)]
MOCK_G_IDS = [f"{i}" for i in range(100)]
MOCK_E_IDS = [f"{i}" for i in range(100)]
MOCK_EX_IDS = [f"{i}" for i in range(100)]
MOCK_X_IDS = [f"{i}" for i in range(100)]
MOCK_Y_IDS = [f"{i}" for i in range(100)]
MOCK_Z_IDS = [f"{i}" for i in range(100)]


def _compute_a_id(index: int) -> str:
    # Total 100000 items, 0-99999 a_id is 0, 10000-19999 a_id is 1, 20000-29999 a_id is 2, ...
    return f"a_id_{index // 10000}"


def _compute_g_id(index: int) -> str:
    # Every 1000 items, g_id will increase by 1
    a_id = _compute_a_id(index)
    index_in_a_id = index % 10000
    return f"{a_id}_g_id_{index_in_a_id // 1000}"


def read_payloads(index: int) -> dict:
    return {
        # "a_id": _compute_a_id(index),
        # "g_id": _compute_g_id(index),
        "a_id": "a_id",
        "g_id": "g_id",
        "e_id": random.choice(MOCK_E_IDS),
        "ex_id": random.choice(MOCK_EX_IDS),
        "x_id": random.choice(MOCK_X_IDS),
        "y_id": random.choice(MOCK_Y_IDS),
        "z_id": random.choice(MOCK_Z_IDS),
        "type": "kbarticle",
        "chunking_strategy": "default",
        "body_text": RANDOM_TEXT,
        "item_idex": index
    }
