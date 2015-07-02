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
from rospy.numpy_msg import numpy_msg
import numpy

from beginner_tutorials.msg import Num

import nagrywaj
import GetIntentViaSpeech
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
				'żółty',
				'podstawowy']


def witVoice():
	wit.voice_query_start("RB3ED7T4K2AU7KMI6JWL7VSXKRVU4YAC")
	time.sleep(czasMowy) 
	response = wit.voice_query_stop()

	return response

tablicaDoPublikowania = ['intent','numer','ktoreKomendy', 'kolor', 'jak', 'pewnosc', 'kierunek', 'jakaFunkcja']

if __name__ == "__main__":
	"""
	intent = tablicaDoPublikowania[0]
	numer = tablicaDoPublikowania[1]
	ktoreKomendy = tablicaDoPublikowania[2]
	kolor = tablicaDoPublikowania[3]
	jak = tablicaDoPublikowania[4]
	"""

	
	#wit.init()

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
		nagrywaj.nagraj(czasMowy)
		jsonResponse = GetIntentViaSpeech.queryAudio('src/beginner_tutorials/Dzwieki/tekst.wav').text
		print(jsonResponse)
		
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



			tablicaDoPublikowania[0] = intent
			tablicaDoPublikowania[1] = str(numer)
			tablicaDoPublikowania[2] = str(ktoreKomendy)
			tablicaDoPublikowania[3] = kolor
			tablicaDoPublikowania[4] = jak
			tablicaDoPublikowania[5] = str(pewnosc)
			tablicaDoPublikowania[6] = kierunek
			jakaFunkcja = data.some_strings[7]


		except:
			tablicaDoPublikowania[0] = "NULL"
			print('\n' "Intent: Null" '\n')





		funkcjeBezargumentowe = ['wyswietlDane' , 'Reset' , 'SkasujHistorieKomend' , 'PokazFunkcje',
								 'PokazKolory', 'Stop', 'Nic', 'KtorymSteruje' , 'WyswietlHistorieKomend']

		funkcjeDwuargumentowe = ['PowtorzKomendy(iloscKomend, ktoreKomendy)']

		funkcjeJednoargumentowe = ['ZmienKolor(nazwaKoloru)', 'Skrec(kierunek)', 'Szybciej(ilosc)',
								 'Wolniej(ilosc)', 'Zmiana_kontroli(ilosc)', 'PrzywolajZolwia(ilosc)']



		msg_to_send= Num()
		msg_to_send.some_strings = tablicaDoPublikowania
		rospy.loginfo(msg_to_send)
		print (" ")
		pub.publish(msg_to_send)
		rate.sleep()







""" KOLORY TEST

ablicaDoPublikowania[0] = 'ZmienKolor'
		tablicaDoPublikowania[3] = dostepneKolory[a]
		a += 1
		if(a >=17):
			a=0
"""



"""SKREC TEST
		tablicaDoPublikowania[0] = 'Skrec'
		if(a==0):
			tablicaDoPublikowania[6] = "prawo"
		else:
			tablicaDoPublikowania[6] = "lewo"
		a += 1
		if(a >=2):
			a=0
"""



"""
		tablicaDoPublikowania[5] = '50'
		tablicaDoPublikowania[0] = 'Jedz'
		tablicaDoPublikowania[6] = 'tył'
		tablicaDoPublikowania[1] = '3'
		tablicaDoPublikowania[4] = 'wolniej'
		msg_to_send= Num()
		msg_to_send.some_strings = tablicaDoPublikowania
		rospy.loginfo(msg_to_send)
		print (" ")
		pub.publish(msg_to_send)
		rate.sleep()
		time.sleep(1)
		i +=1
"""

""" szybciej TEST
		tablicaDoPublikowania[0] = 'Szybciej'
		if(a==0):
			tablicaDoPublikowania[1] = "2"
		else:
			tablicaDoPublikowania[1] = "4"
		a += 1
		if(a >=2):
			a=0

"""


""" WOLNIEJ TEST

		tablicaDoPublikowania[0] = 'Wolniej'
		if(a==0):
			tablicaDoPublikowania[1] = "2"
		else:
			tablicaDoPublikowania[1] = "4"
		a += 1
		if(a >=2):
			a=0


"""




"""PRZYWOLAJ ZMIANA KOTROLI SKREC
		if(i==0):

			tablicaDoPublikowania[0] = 'PrzywolajZolwia'
			tablicaDoPublikowania[1] = '4'

			msg_to_send= Num()
			msg_to_send.some_strings = tablicaDoPublikowania
			rospy.loginfo(msg_to_send)
			print (" ")
			pub.publish(msg_to_send)
			rate.sleep()
			time.sleep(1)
			i=2

		tablicaDoPublikowania[0] = 'Zmiana_kontroli'
		tablicaDoPublikowania[1] = '0'
		msg_to_send= Num()
		msg_to_send.some_strings = tablicaDoPublikowania
		rospy.loginfo(msg_to_send)
		print (" ")
		pub.publish(msg_to_send)
		rate.sleep()
		time.sleep(1)
		tablicaDoPublikowania[0] = 'KtorymSteruje'
		msg_to_send= Num()
		msg_to_send.some_strings = tablicaDoPublikowania
		rospy.loginfo(msg_to_send)
		print (" ")
		pub.publish(msg_to_send)
		rate.sleep()
		time.sleep(1)
		tablicaDoPublikowania[0] = 'Skrec'
		tablicaDoPublikowania[6] = 'lewo'
		msg_to_send= Num()
		msg_to_send.some_strings = tablicaDoPublikowania
		rospy.loginfo(msg_to_send)
		print (" ")
		pub.publish(msg_to_send)
		rate.sleep()
		time.sleep(1)


"""


""" JEDZ PRZOD TYL LEWO prawo

		tablicaDoPublikowania[0] = 'Jedz'
		tablicaDoPublikowania[6] = 'przod'


		msg_to_send= Num()
		msg_to_send.some_strings = tablicaDoPublikowania
		rospy.loginfo(msg_to_send)
		print (" ")
		pub.publish(msg_to_send)
		rate.sleep()
		time.sleep(1)
		i +=1
		while(i >=5):
			tablicaDoPublikowania[6]= 'tył'

			msg_to_send= Num()
			msg_to_send.some_strings = tablicaDoPublikowania
			rospy.loginfo(msg_to_send)
			print (" ")
			pub.publish(msg_to_send)
			rate.sleep()
			time.sleep(1)
			i += 1
			while(i >=10):
				tablicaDoPublikowania[6] = 'prawo'

				msg_to_send= Num()
				msg_to_send.some_strings = tablicaDoPublikowania
				rospy.loginfo(msg_to_send)
				print (" ")
				pub.publish(msg_to_send)
				rate.sleep()
				time.sleep(1)
				i +=1
				while (i>=15):
					tablicaDoPublikowania[6] = 'lewo'
					msg_to_send= Num()
					msg_to_send.some_strings = tablicaDoPublikowania
					rospy.loginfo(msg_to_send)
					print (" ")
					pub.publish(msg_to_send)
					rate.sleep()
					time.sleep(1)
					i +=1
					if(i >= 22):
						i=0


"""