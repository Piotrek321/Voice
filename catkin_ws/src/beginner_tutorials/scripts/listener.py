#!/usr/bin/env python  
# -*- coding: utf-8 -*-
import roslib
roslib.load_manifest('beginner_tutorials')
import rospy
import math
import tf
import geometry_msgs.msg
import turtlesim.srv
from std_msgs.msg import String
import time
import re
import random
import urllib, pycurl, os
from random import randint
import std_srvs.srv 
from beginner_tutorials.msg import Num


czyCiagly = 0
stala = 1
historiaKomend =[[ 0 ]*3 for i in range(0)]

przyspieszenie = 0.5
stala_linear = stala
stala_angular = stala
linear = 0
angular = 0
rozkaz= 'Nic'
Brak = "Brak"

"""
def KolorNaRGB (nazwaKoloru):
    return {
                'czerwony': [255,0,0],
                'niebieski':[0,0,255],
                'zielony':[0,255,0],
                'biały' : [255,255,255],
                'czarny':[0,0,0],
                'fioletowy': [184,3,255],
                'granatowy': [0,0,128],
                'malinowy' : [235,1,101],
                'miętowy': [188,226,127],
                'morski': [0,128,128],
                'pomarańczowy': [255,165,0],
                'purpurowy': [128,0,128],
                'różowy': [255,192,203],
                'srebrny': [192,192,192],
                'szary': [128,128,128],
                'żółty': [255,215,0] 
        }.get(nazwaKoloru,"Nie ma takiego koloru!")

"""
def KolorNaRGB (nazwaKoloru):
    return {
                dostepneKolory[0]:  [255,0,0],
                dostepneKolory[1]:  [0,0,255],
                dostepneKolory[2]:  [0,255,0],
                dostepneKolory[3]:  [255,255,255],
                dostepneKolory[4]:  [0,0,0],
                dostepneKolory[5]:  [184,3,255],
                dostepneKolory[6]:  [0,0,128],
                dostepneKolory[7]:  [235,1,101],
                dostepneKolory[8]:  [188,226,127],
                dostepneKolory[9]:  [0,128,128],
                dostepneKolory[10]: [255,165,0],
                dostepneKolory[11]: [128,0,128],
                dostepneKolory[12]: [255,192,203],
                dostepneKolory[13]: [192,192,192],
                dostepneKolory[14]: [128,128,128],
                dostepneKolory[15]: [255,215,0] 
        }.get(nazwaKoloru,"Nie ma takiego koloru!")


def ZmienKolor(nazwaKoloru):
    kolory = KolorNaRGB(nazwaKoloru)
    rospy.set_param('background_r',kolory[0])
    rospy.set_param('background_g',kolory[1])
    rospy.set_param('background_b',kolory[2])
    rospy.wait_for_service('clear')
    fcja_clear=rospy.ServiceProxy('clear', std_srvs.srv.Empty)
    fcja_clear()



def SkasujHistorieKomend(Brak):
    global historiaKomend
    historiaKomend = [[ 0 ]*3 for i in range(0)]


def PokazFunkcje(Brak):
    print(" ")
    print("1. Przód \n 2. Tył \n 3. Lewo \n 4. Prawo \n 5. Szybciej \n 6. Wolniej \n 7. Przywołaj żółwia \n 8. Stop")
    print(" 9. Zmiana kontroli \n 10. Powtorz komendy \n 11. Zmień kolor tła \n 12. Pokaż dostępne kolory \n")

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

def PokazKolory(Brak):
    for x in range(0,len(dostepneKolory)):
        print "\t" +dostepneKolory[x]
        #print "\n"


def ruszZolwia(lin,ang):
    cmd = geometry_msgs.msg.Twist()
    cmd.linear.x = linear
    cmd.angular.z = angular
    #for x in range(0, 2):
    turtle_vel.publish(cmd)
    rate.sleep()


def wykonajFunkcje(nazwaFunkcji,argument = 'Brak'):
    nazwaFunkcji= nazwaFunkcji+'('+argument+')'
    #print nazwaFunkcji
    #nazwaFunkcji= nazwaFunkcji + '(' + ')'
    exec(nazwaFunkcji)


def Tyl(Brak):
    global linear
    global stala_linear
    linear = -stala_linear
    #print ("Linear: " + str(linear))
    ruszZolwia(linear,0)


def Przod(Brak):
    global linear
    global stala_linear
    linear = stala_linear
    #print ("Linear: " + str(linear))
    ruszZolwia(linear,0)



def Szybciej(arg= 'Brak'):
    global stala_linear
    global stala_angular
    global linear
    global angular
    stala_linear *= (przyspieszenie+1)
    stala_angular *= przyspieszenie+1


def Wolniej(arg= 'Brak'):
    global stala_linear
    global stala_angular
    global linear
    global angular
    if(linear != 0):
        stala_linear *= przyspieszenie
    if(angular != 0):
        stala_angular *= przyspieszenie



def Zmiana_kontroli(numerZolwia):
    global turtle_vel
    nazwaZolwia = 'turtle'+str(numerZolwia)+'/cmd_vel'
    #print (nazwaZolwia)
    turtle_vel = rospy.Publisher(nazwaZolwia, geometry_msgs.msg.Twist,queue_size=4)
    #print turtle_vel
    #rate = rospy.Rate(1)


def Prawo(arg= 'Brak'):
    global angular
    global linear
    linear = 0
    angular = -1.55
    ruszZolwia(0,angular)
    angular = 0




def Lewo(Brak):
    global angular
    global linear
    linear = 0
    angular = 1.55
    ruszZolwia(0,angular)
    angular = 0


iloscZolwi = 1
def PrzywolajZolwia(arg= 'Brak'):
    global iloscZolwi
    iloscZolwi += 1
    rospy.wait_for_service('spawn')
    spawner = rospy.ServiceProxy('spawn', turtlesim.srv.Spawn)
    imieZolwia = 'turtle' + str(iloscZolwi)
    print(imieZolwia)
    spawner(random.uniform(0,12), random.uniform(0,12), random.uniform(0,12), imieZolwia)

    

def Stop(arg= 'Brak'):
    global linear
    global angular
    global stala_linear
    global stala_angular
    linear = 0
    angular = 0
    stala_linear = stala
    stala_angular = stala


def Nic(Brak):
    return 0

def Blad(arg= 'Brak'):
    return 0


def callback(data):
    global rozkaz
    global angular
    global linear
    global stala_linear
    global stala_angular
    print "Jestxvxvxcvcxxcvem"
    #rospy.loginfo("%s", data.data)
    #print(data.some_strings)
    a = data.some_strings[1]
    print(a)
"""
    if not(data.some_strings == "NULL"):
        rozkaz = data.some_strings
        if not((rozkaz=="Nic")or(rozkaz.startswith("powtorzKomendy"))or(rozkaz.startswith("Zmiana_kontroli"))or(rozkaz=="SkasujHistorieKomend")):
            historiaKomend.append([ rozkaz , stala_linear,stala_angular ])
        print historiaKomend
        print "        "
        if (rozkaz.startswith('Zmiana_kontroli')):
            pozycja= rozkaz.find(" ")
            ilosc = rozkaz[pozycja+1:len(rozkaz)]
            rozkaz= rozkaz[0:pozycja]
            wykonajFunkcje(rozkaz,str(ilosc))
        elif (rozkaz.startswith('powtorzKomendy')):
                pozycja = rozkaz.find(" ")
                pozycja2 = rozkaz.find(" ", pozycja+1, len(rozkaz))
                ilosc = rozkaz[pozycja+1:pozycja2]
                ktoreKomendy = rozkaz[pozycja2+1:len(rozkaz)]
                powtorzKomendy(ilosc, ktoreKomendy)

        elif(rozkaz.startswith('ZmienKolor')):
                pozycja= rozkaz.find(" ")
                nazwaKoloru = rozkaz[pozycja+1:len(rozkaz)]
                print nazwaKoloru
                rozkaz= rozkaz[0:pozycja]
                ZmienKolor(nazwaKoloru)
        else:
            wykonajFunkcje(rozkaz)

    else:
        if(czyCiagly == 1):
            wykonajFunkcje(rozkaz)
"""

    



#ZROBIC ZABEZPIECZENIE PRZED UJEMNYMI INDEKSAMI PRZY ZBYT DUZEJ ILSOC KOMEND ZADANYCH
def powtorzKomendy(iloscKomend, ktoreKomendy):
    global stala_linear
    global stala_angular
    poczatek = 0
    zabezpieczenie = len(historiaKomend)-int(iloscKomend)
    print "Zabezpieczenie: " + str(zabezpieczenie)
    if (str(zabezpieczenie) >=0):   
        if (ktoreKomendy == '3'):
            poczatek = zabezpieczenie
        elif(ktoreKomendy == '0'):
            poczatek = 0
        elif(ktoreKomendy == '4'):
            poczatek = 0
            iloscKomend = 1
        elif(ktoreKomendy == '-1'):
            poczatek = len(historiaKomend) -1
            iloscKomend = 1

        #int(iloscKomend)
        print("Ktore komendy: " + str(ktoreKomendy))
        print("poczatek: " + str(poczatek))
        print ("Suma: " + str((int(iloscKomend)+poczatek)))
        for NrKomenda in range(poczatek,(int(iloscKomend)+poczatek) ):
            rozkaz = str(historiaKomend[NrKomenda][0])
            print("Wykonuję funkcję: " + rozkaz )
            stala_linear = historiaKomend[NrKomenda][1] 
            stala_angular = historiaKomend[NrKomenda][2]
            if(rozkaz.startswith("ZmienKolor")):
                pozycja= rozkaz.find(" ")
                nazwaKoloru = rozkaz[pozycja+1:len(rozkaz)]
                rozkaz= rozkaz[0:pozycja]
                ZmienKolor(nazwaKoloru)

            else:
                wykonajFunkcje(rozkaz)
            rate.sleep()

    else:
        print ("Nie było tylu komend!")



if __name__ == '__main__':
    
    rospy.init_node('listener', anonymous=True)
    listener = tf.TransformListener()
    turtle_vel = rospy.Publisher('turtle1/cmd_vel', geometry_msgs.msg.Twist,queue_size=4)
    rate = rospy.Rate(1)

    #PrzywolajZolwia(2)

    while not rospy.is_shutdown():
        try:

            rospy.Subscriber("chatter", Num, callback)

            
        except:
            print "COs nie tak"
        rospy.spin()




