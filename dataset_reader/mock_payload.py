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


def read_payloads() -> dict:
    return {
        "a_id": random.choice(MOCK_A_IDS),
        "g_id": random.choice(MOCK_G_IDS),
        "e_id": random.choice(MOCK_E_IDS),
        "ex_id": random.choice(MOCK_EX_IDS),
        "x_id": random.choice(MOCK_X_IDS),
        "y_id": random.choice(MOCK_Y_IDS),
        "z_id": random.choice(MOCK_Z_IDS),
        "type": "kbarticle",
        "chunking_strategy": "default",
        "body_text": RANDOM_TEXT
    }
