from typing import Iterator
import random


def generate_random_string(length):
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits + string.whitespace, k=length))


RANDOM_TEXT = generate_random_string(1000)

MOCK_A_IDS = [f"{i}" for i in range(100)]


def read_payloads() -> dict:
    return {
        "a_id": random.choice(MOCK_A_IDS),
        "g_id": "g_id",
        "e_id": "e_id",
        "ex_id": "ex_id",
        "type": "kbarticle",
        "chunking_strategy": "default",
        "body_text": RANDOM_TEXT
    }
