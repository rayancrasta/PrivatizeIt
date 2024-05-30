import time
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def keys_match(private_key_str: str, public_key_str: str) -> bool:
    # Deserialize the private key
    private_key = serialization.load_pem_private_key(
        private_key_str.encode(),
        password=None,
        backend=default_backend()
    )

    # Deserialize the public key
    public_key = serialization.load_pem_public_key(
        public_key_str.encode(),
        backend=default_backend()
    )

    # Extract the public key from the private key
    generated_public_key = private_key.public_key()

    # Compare the generated public key with the provided public key
    return generated_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ) == public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

# Example keys (shortened for example purposes, use real keys in practice)
private_key_pem = """
-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----
"""

public_key_pem = """
-----BEGIN PUBLIC KEY-----
...
-----END PUBLIC KEY-----
"""

# Measure the time taken
start_time = time.time()
result = keys_match(private_key_pem, public_key_pem)
end_time = time.time()

print("The keys match!" if result else "The keys do not match.")
print(f"Time taken: {end_time - start_time:.6f} seconds")
