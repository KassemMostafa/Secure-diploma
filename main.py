#!/usr/bin/python
# coding=utf8


from PIL import Image, ImageDraw, ImageFont
import segno
import time
import cv2
import os
import base64

# pip install segno
# pip install qrcode
# pip install cv2
# pip install opencv-python


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


def getQRcode():
    # ToDo correct error libpng warning: iCCP: known incorrect sRGB profile
    img = cv2.imread("diplome.png")
    crop_img = img[940:1105, 1430:1600]
    cv2.imwrite("qrcode2.png", crop_img)
    img = cv2.imread("qrcode2.png")
    det = cv2.QRCodeDetector()
    val, pts, st_code = det.detectAndDecode(img)
    return val


def extrairePreuve():  # à afficher lors de la verification du qrcode
    return 0


def creerQRCode(prenom, nom, diplome):
    # TODO qrcode signature =>encoder en base64
    signature = "qfoqinoi"

    qr = segno.make(prenom + ' ' + nom + ' || ' + diplome +
                    ' || ' + signature, encoding="utf-8")

    qr.save('qrcode.png', light=None, scale=5)
    return 0


def creerTimestamp():
    # TODO create time stamp
    # DONE
    os.system(
        'openssl ts -query -data diplome.png -no_nonce -sha512 -cert -out diplome.tsq')
    os.system('curl -H "Content-Type: application/timestamp-query" --data-binary "@diplome.tsq" https://freetsa.org/tsr > diplome.tsr')
    data = open("diplome.tsr", "rb").read()
    timestamp = base64.b64encode(data).decode()
    return timestamp


def steganoAdd(img, prenom, nom, diplome):

    prenom = "Mostafa"
    nom = "Kassem"
    diplome = "ingenieur"

    # TODO append timestamp in base64 to steg and measure size
    timestamp = creerTimestamp()
    steg = nom + " " + prenom + " || " + diplome + " "
    n = len(steg)
    if (n < 60):
        y = 60 - n
        while (y > 0):
            steg += "0"
            y -= 1
    result = steg + ' || ' + timestamp
    print(len(result))
    cacher(img, result)
    return img


def creerAttestation():  # lancé par l'admin à la création d'une attestation
    query = "Object { prenom: "", nom: "", diplome: "" }"

    # Nomdefichier = prenom_nom_diplome.png
    prenom = "Kassem"
    nom = "Mostafa"
    diplome = "ingenieur"
    # TODO accès signature (en attente de fichier de config)
    img = Image.open("Blank_Certif.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/freefont/FreeMono.ttf", 70)
    draw.text((470, 480), "CERTIFICAT INGENIEUR ", (0, 0, 0), font=font,
              align='left', stroke_width=2, stroke_fill="black")  # draws on top line
    draw.text((680, 600), "DÉLIVRÉ À", (0, 0, 0), font=font,
              align='left', stroke_width=2, stroke_fill="black")
    draw.text((580, 720), "Kassem Mostafa", (0, 0, 0), font=font,
              align='left', stroke_width=2, stroke_fill="black")
    creerQRCode(prenom, nom, diplome)
    qr = Image.open("qrcode.png")
    img.paste(qr, (1430, 930))
    img.save("diplome.png")
    img = steganoAdd(img, prenom, nom, diplome)
    img.save("diplome.png")
    os.remove("qrcode.png")
    return 1


# programme de demonstration


def verifAttestation():
    message_retrouve = recuperer(Image.open("diplome.png"), 7392)
    listStega = decodeMessage(message_retrouve)
    listStega[1] = listStega[1].replace('0', '')
    print("donné de l'image: " +
          listStega[0] + " || " + listStega[1] + " || " + "listStega[2] ")
    val = getQRcode()
    listQrcode = decodeMessage(val)
    print("donné du Qrcode: " +
          listQrcode[0] + " || " + listQrcode[1] + " || " + listQrcode[2])

    with open("doc.tsr", "wb") as file:
        file.write(base64.b64decode(listStega[2].encode()))
    os.system("openssl ts -verify -in doc.tsr -queryfile diplome.tsq -CAfile cacert.pem -untrusted tsa.crt")
    # Je récupére le code:
    # tsr =
    # with open("file.tsr", "wb") as f:
    # f.write(encoder.encode(tsr))
    #print("vérification fini")
    return 1


creerAttestation()
print("attestation cree")
# Extraire le code d'une image:
print(verifAttestation())


# https://gist.github.com/void-elf/0ed0e136d6d342974257c93f571e28b5


# openssl ca -in PKI/tempservercert.pem -cert PKI/certs/webca.pem -keyfile PKI/private/webca.key -notext -out PKI/certs/serveur1.pem-notext -config PKI/ca-server-cert.cnf
