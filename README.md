A basic end-to-end encrypted messaging app. The "server" user gets to specify the bit length for the public key, 
while the "client" user gets to specify the shared secret key.

Relies on RSA for the public key, but can be replaced with Elliptic Curve ElGamal with minimal modification.
Currently required hardcoding the server address and port
