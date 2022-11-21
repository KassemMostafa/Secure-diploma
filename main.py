#!/usr/bin/python
# coding=utf8


from PIL import Image, ImageDraw, ImageFont
import segno
import cv2
import os
import base64
import OpenSSL
from OpenSSL import crypto
import json
import os


# pip install segno
# pip install qrcode
# pip install cv2
# pip install opencv-python


#######################################################Stéganographie##################################################################

def vers_8bit(c):
    chaine_binaire = bin(ord(c))[2:]
    return "0"*(8-len(chaine_binaire))+chaine_binaire


def modifier_pixel(pixel, bit):
    # on modifie que la composante rouge
    r_val = pixel[0]
    rep_binaire = bin(r_val)[2:]
    rep_bin_mod = rep_binaire[:-1] + bit
    r_val = int(rep_bin_mod, 2)
    return tuple([r_val] + list(pixel[1:]))


def recuperer_bit_pfaible(pixel):
    r_val = pixel[0]
    return bin(r_val)[-1]


def cacher(image, message):
    dimX, dimY = image.size
    im = image.load()
    message_binaire = ''.join([vers_8bit(c) for c in message])
    posx_pixel = 0
    posy_pixel = 0
    for bit in message_binaire:
        im[posx_pixel, posy_pixel] = modifier_pixel(
            im[posx_pixel, posy_pixel], bit)
        posx_pixel += 1
        if (posx_pixel == dimX):
            posx_pixel = 0
            posy_pixel += 1
        assert (posy_pixel < dimY)


def recuperer(image, taille):
    message = ""
    dimX, dimY = image.size
    im = image.load()
    posx_pixel = 0
    posy_pixel = 0
    for rang_car in range(0, taille):
        rep_binaire = ""
        for rang_bit in range(0, 8):
            rep_binaire += recuperer_bit_pfaible(im[posx_pixel, posy_pixel])
            posx_pixel += 1
            if (posx_pixel == dimX):
                posx_pixel = 0
                posy_pixel += 1
        message += chr(int(rep_binaire, 2))
    return message


def decodeMessage(message_retrouve):
    separator = ' ||'
    part1 = message_retrouve.split(separator, 1)[0]

    listOfWords = message_retrouve.split(' || ', 1)
    if len(listOfWords) > 0:
        message_retrouve = listOfWords[1]

    separator = ' ||'
    part2 = message_retrouve.split(separator, 1)[0]

    listOfWords = message_retrouve.split('|| ', 1)
    if len(listOfWords) > 0:
        part3 = listOfWords[1]

    return [part1, part2, part3]


def addStegano(imgName, stringToHide):
	img = Image.open(imgName)
	cacher(img, stringToHide)
	img.save(imgName)

###########################################################QRCode############################################################################################
def getQRcode():
    # ToDo correct error libpng warning: iCCP: known incorrect sRGB profile
    img = cv2.imread("cert.png")
    crop_img = img[900:1185, 1400:1680]
    cv2.imwrite("qrcode2.png", crop_img)
    img = cv2.imread("qrcode2.png")
    det = cv2.QRCodeDetector()
    val, pts, st_code = det.detectAndDecode(img)
    return val


def extrairePreuve():  # à afficher lors de la verification du qrcode
    return 0

def addQRCode():
	qr = Image.open("qrcode.png")
	img = Image.open("diplome.png")
	img.paste(qr, (1390,900))
	img.save("diplome.png")

def creerQRCode(signature):
	qr = segno.make(signature)
	qr.save('qrcode.png',light=None, scale= 3)
	addQRCode()

####################################################Certificat###########################################################################

def createSignature(data): #creates a signature based on the same data used by stegano	
	key_file = open("PKIprojet/diplome.key.pem", "r")
	key = key_file.read()
	key_file.close()
	if key.startswith('-----BEGIN '):
		pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key)
	else:
		pkey = crypto.load_pkcs12(key).get_privatekey()
	sign = OpenSSL.crypto.sign(pkey, data, "sha512") 
	data_base64 = base64.b64encode(sign).decode()
	return data_base64

######################################################Diplome###########################################################################
def createBaseDiploma(prenom,nom,diplome): #prend nom, prenom et intitulé, create diploma without qrcode or stégano
	nom = nom.upper()
	diplome = diplome.upper()
	img = Image.open("Blank_Certif.png")
	draw = ImageDraw.Draw(img)
	font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 70)
	draw.text((470, 480),"CERTIFICAT " + diplome ,(0,0,0),font=font,align='left',stroke_width=2,stroke_fill="black") #draws on top line	
	draw.text((680, 600),"DÉLIVRÉ À",(0,0,0),font=font,align='left',stroke_width=2,stroke_fill="black")
	draw.text((580, 720), prenom + " " + nom ,(0,0,0),font=font,align='left',stroke_width=2,stroke_fill="black")
	img.save("diplome.png")
	return 0 

def verifAttestation():
    message_retrouve = recuperer(Image.open("diplome.png"), 7392)
    listStega = decodeMessage(message_retrouve)
    listStega[1] = listStega[1].replace('0', '')
    listStega[1] = listStega[1].replace(' ', '')
    print("donné de l'image: " +
          listStega[0] + " || " + listStega[1] + " || " + "listStega[2]" )
    val = getQRcode()
    print(val)
    #val = base64.b64decode(val.encode())
    #print(val) 
    with open("doc.tsr", "wb") as file:
        file.write(base64.b64decode(listStega[2].encode()))
    os.system("rm rep.txt")
    cmd = "openssl ts -verify -in doc.tsr -queryfile diplome.tsq -CAfile cacert.pem -untrusted tsa.crt >> rep.txt"
    os.system(cmd)

    with open('rep.txt') as f:
        first_line = f.readline()
        first_line = first_line.strip()
    if 'OK' in first_line:
        TEST3 = True
        print("okok3")
    else:
        TEST3 = False   
    if (TEST3 == True ): 
        return 1
    else:
        return 2

############################################TimeStamp###################################################################################
def createTimestamp():
	os.system('openssl ts -query -data diplome.png -no_nonce -sha512 -cert -out diplome.tsq')
	os.system('curl -H "Content-Type: application/timestamp-query" --data-binary "@diplome.tsq" https://freetsa.org/tsr > diplome.tsr')
	data = open("diplome.tsr", "rb").read()
	timestamp = base64.b64encode(data).decode()
	return timestamp

def createSteganoContent(imgName, prenom, nom, diplome): #creates stegano content including timestamp
	steg = nom + " " +  prenom + " || " + diplome + " " 
	n = len(steg)
	if (n < 60):
		y = 60 - n
		while (y > 0):
			steg += "0"
			y -= 1
	timestamp = createTimestamp()
	result = steg + ' || ' + timestamp
	return result




def CreateDiploma(query): #Object { prenom: "", nom: "", diplome: "" }
	query2 = query[9:-1]
	j = json.loads(query2)
	prenom = j["prenom"]
	nom = j["nom"]
	diplome = j["diplome"]
	createBaseDiploma(prenom, nom, diplome)
	result = createSteganoContent("diplome.png", prenom, nom, diplome)
	signature = createSignature(result)
	creerQRCode(signature)
	return 0

query = '{"query":{"prenom":"eazeae","nom":"azeaze","diplome":"ezaeaz"}}'

CreateDiploma(query)
#https://gist.github.com/void-elf/0ed0e136d6d342974257c93f571e28b5
