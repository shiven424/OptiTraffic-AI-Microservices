from cryptography.hazmat.primitives import serialization
import base64, json

# load PEM
with open("jwt_public.pem", "rb") as f:
    pub = serialization.load_pem_public_key(f.read())

numbers = pub.public_numbers()
# base64‑url encode modulus and exponent
def b64url(i):
    b = i.to_bytes((i.bit_length()+7)//8, "big")
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

jwk = {
  "kty": "RSA",
  "use": "sig",
  "alg": "RS256",
  "kid": "001",
  "n": b64url(numbers.n),
  "e": b64url(numbers.e)
}

jwks = { "keys": [jwk] }
with open("jwks.json","w") as f:
    json.dump(jwks, f, indent=2)
print("→ jwks.json written")
