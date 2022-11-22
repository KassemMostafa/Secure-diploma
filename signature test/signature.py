#!/usr/local/bin/python3
import OpenSSL
from OpenSSL import crypto
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding


def signDocument1(data): #openssl Lib
    key_file = open("../PKI/private/serveur1.key")
    key = key_file.read()
    key_file.close()
    pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key, b"test")
    encodedData = bytes(data, encoding='ascii')
    signData = OpenSSL.crypto.sign(pkey, encodedData, "sha256")
    encodedSig = base64.b64encode(signData)
    print("-----BEGIN DATA REQUEST-----")
    print(data)
    print("-----END DATA REQUEST-----")
    print("\n")
    print("Example 1")
    print("-----BEGIN SIGNATURE-----")
    print(encodedSig)
    print("-----END SIGNATURE-----")
    print("\n")
    print("Example 2")
    print("-----BEGIN SIGNATURE-----")
    print (encodedSig.decode('ascii'))
    print("-----END SIGNATURE-----")
    print("\n")
    print("Example 3")
    print("-----BEGIN SIGNATURE-----")
    print(str(encodedSig).replace("b'","").replace("'",""))
    print("-----END SIGNATURE-----")
    return encodedSig

def verifySignature1(signature, data): #openssl lib
    cert_file = open("../PKI/certs/serveur1.pem")
    certContent = cert_file.read()
    cert_file.close()
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, certContent)
    encodedData = bytes(data, encoding='ascii')
    decodedSig = base64.b64decode(signature)
    try:     
        crypto.verify(cert, decodedSig, encodedData, "sha256")
    except:
        return 0
    return 1

    


encodedSig1 = signDocument1("Hello World")

ver = verifySignature1(encodedSig1, "Hello World")
print(ver)


