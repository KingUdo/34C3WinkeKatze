#!usr/bin/python
import telnetlib
import re
from time import sleep
HOST = "telnet.dondario.de"
PORT=23
TIMEOUT=10
import zbarlight
import os
import sys
import PIL
import pygame
from playsound import playsound
import pygame.camera
from pygame.locals import *
import paho.mqtt.client as mqtt #import the client1
import time
from gtts import gTTS

pygame.init()
pygame.camera.init()
cam = pygame.camera.Camera("/dev/video0",(640,480))
cam.start()

## INPUT Number
def getQR():
    image = cam.get_image()
    filepath = "test.png"
    pygame.image.save(image, filepath)

    f = 1
    if(f):
        print ('Scanning image..')
        f = open('test.png','rb')
        qr = PIL.Image.open(f);
        qr.load()
        codes = zbarlight.scan_codes('qrcode',qr)           
    return codes

def playaudio():
    tts = gTTS(text='Hallo Dario gibt uns ein T-Shirt', lang='de',slow=True)
    tts.save("Dario.mp3")
    playsound('Dario.mp3')
    
    
###Telnet
def get_token(token_1):
        print(token_1.encode('utf-8'))
        tn = telnetlib.Telnet(HOST,PORT,TIMEOUT)
        tn.read_until(b'token:')
        time.sleep(1)
        tn.write(token_1.encode('utf-8')+b'\r\n')
        #Einblesen bis trigger
        print(tn.read_until(b'blanks):\r\n'))
        einlesen = tn.read_until(b'\r\n')
        
        umw = re.search(r'\[(.)\].*\[(.)\].*\[(.)\]',einlesen.decode('utf-8'))

        as1 = ord(umw.group(1))
        as2 = ord(umw.group(2))
        as3 = ord(umw.group(3))

        asout = '{} {} {}\r\n'.format(as1, as2, as3)
        sleep(1)
        tn.write(asout.encode('utf-8'))
        sleep(2)
        ausgabe = tn.read_all()
        token = re.search(r'\w{64}',ausgabe.decode('utf-8'))

        return token.group(0)


#### MQTT

def submitMQTT(Number, Token):
    print("MQTT")

    def on_message(client, userdata, message):
        if str(message.payload.decode("utf-8")) == "CONGRATULATIONS, you'll get a free shirt at the assembly":
            print("Made it ;-)")
        else:
            print("")

    client = mqtt.Client()          #create new instance
    client.on_message=on_message                #attach function to callback
    client.connect("mqtt.dondario.de")              #connect to broker
    client.loop_start()                         #start the loop

    client.subscribe("/#")
    client.publish("/34c3/cat/cmd",str(Number+":"+Token))

    time.sleep(4) # wait
    client.loop_stop() #stop the loop



## MAIN

Number = input("Whats the Number? :")
print("Thanks! Scanning Image")

while(True):
    QRcode = getQR()
    if(QRcode==None):
        print ('No QR code found retry in 0.5 sec')
        time.sleep(0.5)
    else:
        break
        
print("Token1:",QRcode[0].decode("utf-8"))

Token2 = get_token(QRcode[0].decode("utf-8"))

submitMQTT(Number, Token2)

playaudio()










