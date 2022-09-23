import string
import random


def generate_complaint_id() -> str:
    """generate id for every complains/suggestion received.

    Returns:
        str: generated complaint id
    """
    generated_id = "".join(
        [random.choice(string.ascii_uppercase + string.digits) for _ in range(11)]
    )
    complaint_id = f"CNO#{generated_id}"
    return complaint_id
