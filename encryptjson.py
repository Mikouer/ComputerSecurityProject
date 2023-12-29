from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import json

# Generate an RSA Key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=3072,
    backend=default_backend()
)

# Get the Public Key from the Private Key
public_key = private_key.public_key()

# Your JSON message
json_message = "PASSWORD123"

# Convert JSON to bytes
json_bytes = json.dumps(json_message).encode()

# Encrypting the message
encrypted = public_key.encrypt(
    json_bytes,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Decrypting the message
original_message = private_key.decrypt(
    encrypted,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Decode from bytes to string
decoded_message = original_message.decode('utf-8')

print("Original JSON:", json_message)
print("Encrypted:    ", encrypted)
print("Decrypted JSON:", json.loads(decoded_message))
