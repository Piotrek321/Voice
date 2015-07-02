#!/usr/bin/env python
#-*- coding: utf-8 -*-

import wit
import json
import subprocess
import rospy

import re
import urllib, pycurl, os
from std_msgs.msg import String
import time
from rospy.numpy_msg import numpy_msg
import numpy

from beginner_tutorials.msg import Num

czasMowy = 4

def czyKoncoweKomendy (arg):
    return {
        'poprzednią': -1,
        'ostatnią': -1,
        'ostatnia': -1,
        'ostatnio': -1,
        'ostatnich' : -1,
        'ostatni' : -1,
        'pierwsze': 0,
        'pierwszych': 0,
        'ostatnie': 3,
        'ostatnich':3,
        'pierwszą': 4

    }.get(arg,False)




def konwertujLiczbe (liczba):
    return {
        'jeden': 1,
        'pierwszy': 1,
        'pierwszym': 1,
        'pierwszego': 1,
        'drugi': 2,
        'drugim': 2,
        'drugiego': 2,
        'dwa': 2,
        'dwie':2,
        'trzy': 3,
        'trzeci': 3,
        'trzecim': 3,
        'trzeciego': 3,
        'cztery': 4,
        'czwarty': 4,
        'czwartym': 4,
        'czwartego': 4,
        'pięć': 5,
        'piąty': 5,
        'piątym': 5,
        'piątego': 5,
        'sześć': 6,
        'szósty': 6,
        'szóstym': 6,
        'szóstego': 6,
        'siedem': 7,
        'siódmy': 7,
        'siódmym': 7,
        'siódmego': 7,
        'ósmy': 8,
        'ósmym': 8,
        'osiem': 8,
        'ósmego': 8,
        'dziewięć': 9,
        'dziewiąty': 9,
        'dziewiątym': 9,
        'dziewiątego': 9,
        'dziesięć': 10,
        'dziesiąty': 10,
        'dziesiątym': 10,
        'dziesiątego': 10,

    }.get(liczba,False)




def witVoice():
    wit.voice_query_start("RB3ED7T4K2AU7KMI6JWL7VSXKRVU4YAC")
    time.sleep(czasMowy) 
    response = wit.voice_query_stop()

    return response

tablicaDoPublikowania = ['intent','numer','ktoreKomendy', 'kolor', 'jak', 'pewnosc', 'kierunek', 'jakaFunkcja', 'tekst']

if __name__ == "__main__":
    """
    intent = tablicaDoPublikowania[0]
    numer = tablicaDoPublikowania[1]
    ktoreKomendy = tablicaDoPublikowania[2]
    kolor = tablicaDoPublikowania[3]
    jak = tablicaDoPublikowania[4]
    """

    
    wit.init()

    pub = rospy.Publisher('chatter', Num)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(10) # 10hz



    """
        rospy.loginfo("Przod")
        pub.publish("Przod")
        rate.sleep()
        rate.sleep()
    """

    #print(konwertujLiczbe('pierwszy'))

    while not rospy.is_shutdown(): #While(True)

        jsonResponse = witVoice()
        if not jsonResponse:
            continue;
        dataDict = json.loads(jsonResponse)

        try: 
            intent= dataDict["outcomes"][0]["intent"]
            print ("Try intent")

            try:
                numer=dataDict["outcomes"][0]["entities"]['numer'][0]['value']
                print ("Try numer")
                if(numer):
                    if not(numer.isdigit()):
                        numer = konwertujLiczbe(numer)
                        print ("Konwersja numer")
            
            except: 
                print ("Except numer")
                if(str(intent) == 'Zmiana_kontroli'):
                    print("Zmiana kontroli ale brak numeru")
                    numer = 0
                else:
                    numer = 1

            try:
                ktoreKomendy = dataDict["outcomes"][0]["entities"]['ktore'][0]['value']
                if (ktoreKomendy):
                    print("Ktore komendy: " + str(ktoreKomendy))
                    ktoreKomendy = czyKoncoweKomendy(str(ktoreKomendy))
                else:
                    ktoreKomendy = 3 #ostatnie
                    
            except:
                ktoreKomendy = 3
                print ("Bląd przy ktoreKomendy")



            try:
                jak = dataDict["outcomes"][0]["entities"]['jak'][0]['value']                    
            except:
                jak = 'normalnie'

            try:
                kolor = dataDict["outcomes"][0]["entities"]['kolor'][0]['value']
            except:
                kolor = 'Brak koloru'
                if(intent == 'ZmienKolor'):
                    kolor = 'kolejny'
            try:
                pewnosc= dataDict["outcomes"][0]["confidence"]
                pewnosc = pewnosc * 100
            except:
                pewnosc = 'Null'

            try:
                kierunek= dataDict["outcomes"][0]["entities"]['kierunek'][0]['value']
            except:
                kierunek = 'Null'

            try:
                jakaFunkcja= dataDict["outcomes"][0]["entities"]['jakaFunkcja'][0]['value']
            except:
                jakaFunkcja = 'Null'

            try:
                "Print text"
                tekst= dataDict["outcomes"][0]["_text"]
                print tekst
            except:
                tekst = 'Null'



            tablicaDoPublikowania[0] = intent
            tablicaDoPublikowania[1] = str(numer)
            tablicaDoPublikowania[2] = str(ktoreKomendy)
            tablicaDoPublikowania[3] = kolor
            tablicaDoPublikowania[4] = jak
            tablicaDoPublikowania[5] = str(pewnosc)
            tablicaDoPublikowania[6] = kierunek
            tablicaDoPublikowania[7] = jakaFunkcja
            tablicaDoPublikowania[8] = tekst
            print "intent: " + intent




        except:
            tablicaDoPublikowania[0] = "NULL"
            print('\n' "Intent: Null" '\n')


        msg_to_send= Num()
        msg_to_send.some_strings = tablicaDoPublikowania
        rospy.loginfo(msg_to_send)
        print (" ")
        pub.publish(msg_to_send)
        rate.sleep()



    wit.close()
