# This code is used to verify this Log from Gen2
# "C:\Users\vor5hc\OneDrive - Bosch Group\task\hgt\970502_anchorLearn_investigation\test_log\sw_update\anchor_1_INCAR_extracted_log.txt"


from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import utils

private_key_hex = "0c 8d 19 98 da 96 2a 3a b3 4d 6b 3f e5 b2 8c 24 f9 c0 20 09 9c 74 f0 5c 6d 70 92 96 65 47 df 55"

def boschSigCal(seed_str):
    hex_data_raw = seed_str
    
    data = bytes.fromhex(hex_data_raw)
    private_key_bytes = bytes.fromhex(private_key_hex)

    # Load private key from bytes (as integer)
    private_value = int.from_bytes(private_key_bytes, byteorder='big')
    private_key = ec.derive_private_key(private_value, ec.SECP256R1(), default_backend())

    # Signing:
    signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))

    # Decode DER signature to get r and s
    r, s = utils.decode_dss_signature(signature)

    # Convert to 64 bytes (32 bytes each for r and s)
    signature_64 = r.to_bytes(32, byteorder='big') + s.to_bytes(32, byteorder='big')


    return signature_64