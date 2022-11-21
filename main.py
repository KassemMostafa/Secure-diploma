#!/usr/bin/python
# coding=utf8

from PIL import Image, ImageDraw, ImageFont
import segno
import os



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

def extrairePreuve(): #à afficher lors de la verification du qrcode
	return 0

def creerPass(): # utiliser lors de la création d'une attestation
	return 1

def creerQRCode():
	
	qr = segno.make("Mostafa Kassem | Ingénieur | Timestamp ", encoding="utf-8")
	qr.save('qrcode.png',light=None, scale= 5)
	return 0

def creerTimestamp():
	os.system("openssl ts -query -data certif.png -no_nonce -sha512 -cert -out file.tsq")
	os.system('curl -H "Content-Type: application/timestamp-query" --data-binary "@file.tsq" https://freetsa.org/tsr > file.tsr')
	return 0

def creerAttestation(): #lancé par l'admin à la création d'une attestation
	if (1 != creerPass()):
		return 0
	else:
		#accès signature (en attente de fichier de config)
		img = Image.open("Blank_Certif.png")
		draw = ImageDraw.Draw(img)
		font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 70)
		draw.text((470, 480),"CERTIFICAT INGENIEUR ",(0,0,0),font=font,align='left',stroke_width=2,stroke_fill="black") #draws on top line	
		draw.text((680, 600),"DÉLIVRÉ À",(0,0,0),font=font,align='left',stroke_width=2,stroke_fill="black")
		draw.text((580, 720),"Mostafa Kassem",(0,0,0),font=font,align='left',stroke_width=2,stroke_fill="black")
		creerQRCode()	
		qr = Image.open("qrcode.png")
		img.paste(qr, (1430,930))
		img = steganoAdd(img)
		img.save("certif.png")
		os.remove("qrcode.png")
		return 1



def steganoAdd(img):

	prenom = "Mostafa"
	nom = "Kassem"
	diplome = "ingenieur"
	timestamp = "10h06"
	steg = nom + " " +  prenom + " || " + diplome + " || " + timestamp 
	cacher(img, steg)
	return img 

# programme de demonstration

creerAttestation()





#openssl ca -in PKI/tempservercert.pem -cert PKI/certs/webca.pem -keyfile PKI/private/webca.key -notext -out PKI/certs/serveur1.pem-notext -config PKI/ca-server-cert.cnf
