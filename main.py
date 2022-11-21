#!/usr/bin/python
# coding=utf8

from PIL import Image, ImageDraw, ImageFont
import segno
import os
from pyasn1.codec.der import encoder
import base64


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

def creerQRCode(prenom, nom, diplome):
	 #TODO qrcode signature =>encoder en base64
	signature = 0
	
	qr = segno.make(prenom + ' ' + nom + ' || ' + diplome + ' || ' + signature, encoding="utf-8")

	qr.save('qrcode.png',light=None, scale= 5)
	return 0

def creerTimestamp(prenom, nom, diplome):
	#TODO create time stamp
	#DONE
	os.system('openssl ts -query -data ' + prenom + '_' + nom + '_' + diplome + '.png -no_nonce -sha512 -cert -out ' + prenom + '_' + nom + '_' + diplome + '.tsq')
	os.system('curl -H "Content-Type: application/timestamp-query" --data-binary "@' + prenom + '_' + nom + '_' + diplome + '.tsq" https://freetsa.org/tsr > ' + prenom + '_' + nom + '_' + diplome + '.tsr')
	
	return 0

def creerAttestation(): #lancé par l'admin à la création d'une attestation
	#Nomdefichier = prenom_nom_diplome.png
	prenom = "Mostafa"
	nom = "Kassem"
	diplome = "ingenieur"
	if (1 != creerPass()):
		return 0
	else:
		#TODO accès signature (en attente de fichier de config)
		img = Image.open("Blank_Certif.png")
		draw = ImageDraw.Draw(img)
		font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 70)
		draw.text((470, 480),"CERTIFICAT INGENIEUR ",(0,0,0),font=font,align='left',stroke_width=2,stroke_fill="black") #draws on top line	
		draw.text((680, 600),"DÉLIVRÉ À",(0,0,0),font=font,align='left',stroke_width=2,stroke_fill="black")
		draw.text((580, 720),"Mostafa Kassem",(0,0,0),font=font,align='left',stroke_width=2,stroke_fill="black")
		creerQRCode(prenom,nom,diplome)	
		qr = Image.open("qrcode.png")
		img.paste(qr, (1430,930))
		img.save(prenom + '_' + nom + '_' + diplome +".png")
		img = steganoAdd(img,prenom,nom,diplome)
		img.save(prenom + '_' + nom + '_' + diplome +".png")
		os.remove("qrcode.png")
		return 1



def steganoAdd(img,prenom,nom,diplome):

	prenom = "Mostafa"
	nom = "Kassem"
	diplome = "ingenieur"
	timestamp = "13h09"
	#TODO append timestamp in base64 to steg and measure size
	
	
	creerTimestamp(prenom,nom,diplome)
	steg = nom + " " +  prenom + " || " + diplome + " || " + timestamp
	cacher(img, steg)
	return img 

# programme de demonstration

creerAttestation()





#openssl ca -in PKI/tempservercert.pem -cert PKI/certs/webca.pem -keyfile PKI/private/webca.key -notext -out PKI/certs/serveur1.pem-notext -config PKI/ca-server-cert.cnf
