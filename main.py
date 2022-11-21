#!/usr/bin/python
# coding=utf8

from PIL import Image
import time
import cv2
import os
#pip install qrcode
#pip install cv2
#pip install opencv-python

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

def cacher(image,message):
	dimX,dimY = image.size
	im = image.load()
	message_binaire = ''.join([vers_8bit(c) for c in message])
	posx_pixel = 0
	posy_pixel = 0
	for bit in message_binaire:
		im[posx_pixel,posy_pixel] = modifier_pixel(im[posx_pixel,posy_pixel],bit)
		posx_pixel += 1
		if (posx_pixel == dimX):
			posx_pixel = 0
			posy_pixel += 1
		assert(posy_pixel < dimY)

def recuperer(image,taille):
	message = ""
	dimX,dimY = image.size
	im = image.load()
	posx_pixel = 0
	posy_pixel = 0
	for rang_car in range(0,taille):
		rep_binaire = ""
		for rang_bit in range(0,8):
			rep_binaire += recuperer_bit_pfaible(im[posx_pixel,posy_pixel])
			posx_pixel +=1
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
	#base64_bytes = part3.encode('ascii')
	#message_bytes = base64.b64decode(base64_bytes)
	#message = message_bytes.decode('ascii')
    print(part3)
    
    return [part1 , part2, message]


def getQRcode():
	img = cv2.imread("certif.png")
	crop_img = img[940:1105, 1430:1600]
	cv2.imwrite("qrcode2.png", crop_img)
	img=cv2.imread("qrcode2.png")
	det=cv2.QRCodeDetector()
	decodedText, points, _ = det.detectAndDecode(img)
	val, pts, st_code=det.detectAndDecode(img)
	print(val)
    
## Extraire le code d'une image:

nom_fichier = "certif.png"
message_a_traiter = 40    #A MODIFIER
mon_image = Image.open(nom_fichier)
message_retrouve = recuperer(mon_image, message_a_traiter)
print(message_retrouve)
listrep = decodeMessage(message_retrouve)
print(listrep)


getQRcode()
#https://gist.github.com/void-elf/0ed0e136d6d342974257c93f571e28b5



