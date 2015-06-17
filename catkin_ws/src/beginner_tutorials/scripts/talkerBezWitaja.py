#!/usr/bin/env python
#-*- coding: utf-8 -*-

import wit
import json
import subprocess
import rospy
import wit
import re
import urllib, pycurl, os
from std_msgs.msg import String
import time
from beginner_tutorials.msg import Num

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



dostepneKolory=['czerwony',
                'niebieski',
                'zielony',
                'biały',
                'czarny',
                'fioletowy',
                'granatowy',
                'malinowy',
                'miętowy',
                'morski',
                'pomarańczowy',
                'purpurowy',
                'różowy',
                'srebrny',
                'szary',
                'żółty']




def witVoice():
    wit.voice_query_start("RB3ED7T4K2AU7KMI6JWL7VSXKRVU4YAC")
    time.sleep(4)
    response = wit.voice_query_stop()
    #print("Response: {}".format(response))
    return response

def pokaKolory():
    for i in range(0,len(dostepneKolory)):
        kolor = "ZmienKolor " + dostepneKolory[i]
        coRob(kolor)


def coRob(abc):
    rospy.loginfo(abc)
    pub.publish(abc)
    rate.sleep()
if __name__ == "__main__":
    wit.init()
    pub = rospy.Publisher('chatter', Num, queue_size=1)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(1) # 10hz

    powtorzKomendy = "powtorzKomendy 8 3"
    PrzywolajZolwia = "PrzywolajZolwia"
    ZmianaKontroli = "Zmiana_kontroli 2"
    zmienKolor = "ZmienKolor czerwony"
    zmienKolor2 = "ZmienKolor niebieski"
    zmienKolor3 = "ZmienKolor zielony"
    zmienKolor4 = "ZmienKolor biały"
    Przod = "Przod"
    Tyl = "Tyl"
    Prawo = "Prawo"
    Lewo = "Lewo"
    Szybciej = "Szybciej"
    Wolniej  = "Wolniej"
    Stop = "Stop"
    PokazKolory = "PokazKolory"
    i = 0
    tablicaDoPublikowania = ['intent','numer','ktoreKomendy', 'kolor', 'jak', 'pewnosc']
    while not rospy.is_shutdown(): 
            

        time.sleep(1.5)
        tablicaDoPublikowania[0] = Tyl
        tablicaDoPublikowania[1] = '1'
        msg_to_send= Num()
        msg_to_send.some_strings = tablicaDoPublikowania
        rospy.loginfo(msg_to_send)
        print (" ")
        pub.publish(msg_to_send)
        rate.sleep()


wit.close()



"""
    coRob(Tyl)
    coRob(Tyl)
    coRob(Tyl)
    coRob(Tyl)
    coRob(Tyl)
    time.sleep(1.5)
    coRob(Lewo)
    time.sleep(1.5)
    coRob(Przod)
    coRob(Przod)
    coRob(Przod)
    coRob(Przod)
    coRob(Przod)
    time.sleep(1.5)
    coRob(Prawo)
    time.sleep(1.5)
    coRob(PrzywolajZolwia)
    time.sleep(1.5)
    coRob(ZmianaKontroli)
    time.sleep(1.5)
    coRob(powtorzKomendy)
"""