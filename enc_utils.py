import random
import struct

def int_to_bytes(number):
    ret = []
    while number != 0:
        ret.append(number & 0xFF)
        number = number >> 8
    return bytes(ret)

# Miller-Rabin prime test
def isprime(prime, rounds):
    def mr_expmod(a,b,m):
        v = 1
        while b > 0:
            if(b%2 == 0):
                a = pow(a, 2, m)
                z = pow(a, 2, m)
                # Rabin test
                if (z == 1) and ( a != 1 and a != m-1 ):
                    return 0 # This will trip the Miller test in isprime
                b = b//2
            else:
                b-=1
                v = (v*a) % m
        return v

    a = random.randint(1, prime-1)
    for _ in range(rounds):
        # Miller test
        if mr_expmod(a, prime, prime) != a:
            return False
    return True

# Generate a prime number with the length of keylen
# Currently too slow for anything greater than 512
def genprime(keylen=512, rounds=80):
    if keylen < 1:
        raise ValueError(f'Keylen is too small ({keylen}). Keylen must be >= 1')
    if rounds < 0:
        raise ValueError(f'Rounds is too small ({rounds}). Rounds must be >= 0')

    # Generate fixed values within number
    prime_core = (0x01 << keylen)
    prime_core |= 0x01

    current_prime = 0
    while(True):
        current_prime = prime_core | random.getrandbits(keylen)
        if isprime(current_prime, rounds):
            break
    return current_prime

def gcd(a, b):
	x = a
	y = b
	if y == 0:
		return x
	return gcd(y, x%b)

def gcd(a, b):
    A = a
    B = b
    while True:
        if B == 0:
            return A
        temp = A % B
        A = B
        B = temp


def xgcd(a, b):
    A = a
    B = b
    Q = a // b
    R = a % b
    x1 = 1
    y1 = 0
    x2 = 0
    y2 = 1

    while R != 0:
        xhat = x1 - (Q * x2)
        yhat = y1 - (Q * y2)

        A = B
        B = R
        Q = A // B
        R = A % B
        x1 = x2
        y1 = y2
        x2 = xhat
        y2 = yhat

    return [B, x2, y2]
