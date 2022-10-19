import random
import string

def generate_transation_number() -> str:
    """Generate id number for every transaction."""
    generated_id = "".join( 
        [random.choice(string.ascii_uppercase + string.digits) for _ in range(11)]
    )
    transac_id = f"TN#{generated_id}"

    return transac_id

