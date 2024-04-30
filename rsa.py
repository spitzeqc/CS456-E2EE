import enc_utils as eu
import base64
import struct

def decrypt(cipher, d, n):
    messageint = pow(cipher, d, n)
    messagebytes = eu.int_to_bytes(messageint)
    message = messagebytes.decode('utf-8')
    return message

def encrypt(message, e, n):
    messageint = int.from_bytes(message.encode('utf-8'), byteorder='little', signed=False)
    cipher = pow(messageint, e, n)
    return cipher

class RSA:
    def __init__(self, keylen):
        self.e = 3
        self.d = None
        self.phi = None

        self.p = None
        self.q = None
        self.n = None

        while(True):
            self.p = eu.genprime(keylen)
            self.q = eu.genprime(keylen)
            while( self.p == self.q ):
                self.q = eu.genprime(keylen)

            self.phi = (self.p-1) * (self.q-1)
            tmp = eu.xgcd(self.phi, self.e)
            if tmp[0] == 1:
                self.d = tmp[2]
                while self.d < 0:
                    self.d += self.phi
                break
        self.n = (self.p) * (self.q)

    def decrypt(self, cipher):
        return decrypt(cipher, self.d, self.n)
    def encrypt(self, message):
        return encrypt(message, self.e, self.n)
