import enc_utils as eu
import random
import math

DEFAULT_GENERATOR = (89159992336322032844617539118540418130592399874888264124507995989182506796741,31147983867413449666681383206376158800678711457674440722392647634106461340534)
DEFAULT_CURVE_A = 82163109158490550745568060365949935122903584151308781751390478104193385810187
DEFAULT_CURVE_B = 73769374479299565877809734495580135080730792708282673962911780352135759487999

def pointAdd(P, Q, prime, a=None):
    if P == None:
        return Q
    if Q == None:
        return P
    if (P[0] == Q[0]) and (P[1] == -Q[1]):
        return None

    # Calculate slope
    m = None
    if (P[0] == Q[0]) and (P[1] == Q[1]):
        #m = (3*(P[0]**2) + a) // (2*P[1])
        inv = eu.xgcd(2*P[1], prime)
        while inv[1] < 0:
            inv[1] += prime

        m = ( ((3 * (P[0]**2)) + a) *inv[1] )% prime
    else:
        inv = eu.xgcd((Q[0]-P[0]), prime)
        while inv[1] < 0:
            inv[1] += prime

        m = (Q[1]-P[1]) * inv[1] % prime

    # Calculate 'C' value
    c = P[1] - (m*P[0]) % prime

    # Find the 'x' of our new point
    x3 = ( (m**2) - (P[0] + Q[0]) ) % prime
    y3 = -( ((m*x3) + c) ) % prime
    return (x3, y3)

def pointMultiply(m, P, prime, curvea):
    v = None
    a = P
    while(m>0):
        #print(m)
        if(m%2 == 0):
            a = pointAdd(a, a, prime, curvea)
            m = m//2
        else:
            m -= 1
            v = pointAdd(v, a, prime, curvea)
    return v
1024
def pointSubtract(R, Q, prime): # R - Q
    x3, y3 = R[0], R[1]
    x2, y2 = Q[0], Q[1]
    y3 = -y3 % prime

    # The slope will be the same for all points, so we can calculate using R and Q
    inv = eu.xgcd( (x3 - x2), prime )
    while inv[1] < 0:
        inv[1] += prime
    m = (y3-y2) * inv[1] % prime
    c = y3 - (m * x3) % prime

    # x3 = m^2 - (x1 + x2)
    x1 = -( (x3 - (m**2)) + x2 ) % prime
    y1 = ( (m * x1) + c ) % prime

    return (x1, y1)

def decrypt(cipher, halfmask, secret, prime, curvea):
    fullmask = pointMultiply(secret, halfmask, prime, curvea)
    return pointSubtract(cipher, fullmask, prime)

def encrypt(message, publicPoint, generator, prime, curvea):
    hiddenval = random.randint(2, prime)
    halfmask = pointMultiply(hiddenval, generator, prime, curvea)
    cipher = pointAdd( (message), pointMultiply(hiddenval, publicPoint, prime, curvea), prime, curvea )
    return (cipher, halfmask)

class ElGamal:
    def __init__(self, keylen=4096, prime=None, generator=DEFAULT_GENERATOR, curvea=DEFAULT_CURVE_A, curveb=DEFAULT_CURVE_B, publicKeys=None, privateKeys=None):
        existingPoint = None
        existingSecret = None
        if publicKeys != None:
            prime, existingPoint, generator, curvea, curveb = publicKeys

        if privateKeys != None:
            existingSecret, prime, generator, curvea, curveb = privateKeys

        self.generator = generator
        self.curvea = curvea
        self.curveb = curveb
        self.prime = eu.genprime(keylen) if prime==None else prime
        self.secret = random.randint(3, self.prime) if existingSecret == None else 0
        self.publicPoint = pointMultiply(self.secret, self.generator, self.prime, self.curvea) if existingPoint == None else existingPoint

    def exportPrivateKeys(self):
        return (self.secret, self.prime, self.generator, self.curvea, self.curveb)

    def exportPublicKeys(self):
        return (self.prime, self.publicPoint, self.generator, self.curvea, self.curveb)

    def decrypt(self, cipher, halfmask):
        return decrypt(cipher, halfmask, self.secret, self.prime, self.curvea)

    # Why you would need this, idk
    def encrypt(self, message):
        message_point = message
        if type(message) == str:
            message_x = int.from_bytes(message.encode("utf-8"), byteorder="big", signed=False)
            message_y = math.floor( math.sqrt((message_x**3 + self.curvea*message_x + self.curveb) % self.prime) )
            message_point = (message_x, message_y)
        return encrypt(message_point, self.publicPoint, self.generator, self.prime, self.curvea)

