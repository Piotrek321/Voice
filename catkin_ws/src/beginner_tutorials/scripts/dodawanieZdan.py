#!/usr/bin/env python
#-*- coding: utf-8 -*-
import pycurl
import cStringIO
import json



def zlicz(tablica):

    tab = []
    i = 0
    a =0
    indeks= 0
    tab.append(tablica[0])
    #print tablica
    #print tab

    for x in range(1, len(tablica)):
        
        if not(tablica[x] in tab):
            i+=1
            tab.append(tablica[x])
            #print tablica
            #print tab
            

    maksimum= 0

    for x in range(len(tab)):
        if(tablica.count(tab[x]) > maksimum):
            maksimum = tablica.count(tab[x])
        elif(tablica.count(tab[x]) == maksimum):
            print "Maksimum prawdopodobnie takie same county"
    if(maksimum == (len(tablica))):
        for x in range(len(tablica)-1):
            if(tablica[x] == tablica[x+1]):
                maksimum = 0






    indeks = maksimum
    #print "ZLICZINDEKS: " + str(indeks)
    #print "tablica[indeks: " + str(tablica[indeks])
    
    return [tablica[indeks]]


def znajdzPrawdopodobny(funkcjaPodana):
    i=0
    #print "funkcjaPodana: " + str(funkcjaPodana[i])
    liczbaPoprawnych= 0
    liczbaBlednych = 0

    tab = []
    for x in range(len(funkcjeBezNawiasow)):
        funkcja = funkcjeBezNawiasow[x].split()
        #print funkcja

        if(len(funkcja[i]) >= len(funkcjaPodana[i])):
            for z in range(len(funkcjaPodana[i])):
                if(funkcjaPodana[i][z] == funkcja[i][z]):
                    liczbaPoprawnych += 1
                else: 
                    liczbaBlednych +=1
                roznica = liczbaPoprawnych - liczbaBlednych

        else:
            for z in range(len(funkcja[i])):
                if(funkcjaPodana[i][z] == funkcja[i][z]):
                    liczbaPoprawnych += 1
                else: 
                    liczbaBlednych +=1
                roznica = liczbaPoprawnych - liczbaBlednych

        tab.append(roznica)
        liczbaPoprawnych =0
        liczbaBlednych = 0
  


                                
                               
    m = max(tab)
    iloscMaxow = tab.count(m)
    #print "Max: " + str(m)
    #print "Ilosc max: " + str(iloscMaxow)
    indeksy = zwrocIndeksyMax(tab)
    #print indeksy
    #print "Funkcja poszukiwana: " + str(funkcjeBezNawiasow[indeksy[0]])
    #print tab
    return indeksy

def zwrocIndeksyMax(tablica):
    maksimum = max(tablica)
    indeks =[]
    for x in range(len(tablica)):
        if (maksimum == tablica[x]):
            indeks.append(x)
    return indeks



def czyZawiera(tablica, doPorownania):

    indeks =[]
    #print tablica
    #print doPorownania
    for y in range(len(doPorownania)):
        for x in range(len(tablica)):
            if (doPorownania[y] in tablica[x]):
                indeks.append(x)
                #print "czyZawiera indeks: " + str(indeks)

    if(len(indeks) == 1):
        #print str(len(indeks))
        return indeks
    elif(len(indeks) == 0):
        #print "ZLE"
        
        return znajdzPrawdopodobny(doPorownania)



    else:
        #print "Else"
        indeks = zlicz(indeks)
        return indeks






def dodajNoweZdanie(jakaFunkcja, kierunek):
    i = 0
    jakaFunkcja = jakaFunkcja.title()
    jakaFunkcja = jakaFunkcja.split()

    indeks = []
    poszukiwanaFunkcja = "NULL"


    indeks = czyZawiera(funkcjeBezNawiasow, jakaFunkcja)



    if(indeks):
        #print "Poszukiwana funkcja: " + str(funkcjeBezNawiasow[indeks])
        poszukiwanaFunkcja = funkcjeBezNawiasow[indeks[0]]
        print "poszukiwanaFunkcja: " + str(poszukiwanaFunkcja)
        return poszukiwanaFunkcja








funkcjeBezNawiasow = ['Zrob Kolko', 'Wyswietl Dane' ,'Reset',
                    'Skasuj Historie Komend', 'Pokaz Funkcje','Pokaz Kolory', 
                    'Stop', 'Nic', 'Ktorym Steruje', 'Wyswietl Historie Komend',
                    'Zmien Kolor','Skrec', 'Szybciej','Wolniej', 
                    'Zmien Kontrole','Przywolaj Zolwia', 'Powtorz Komendy', 'Jedz']


z= 'Zrób kółko'
c= dodajNoweZdanie(z, 'a')


curl_header = ["Authorization: Bearer THAKYMA767MXNDXJOZXDUBGHGFIRW5ER",
                 "Content-Type: application/json"]
curl_url_0 = "https://api.wit.ai/intents/"
curl_url_1 = c
curl_url_1 = curl_url_1.replace(" ", "")
curl_url_2 = "/expressions?v=20150626"

curl_url = curl_url_0+str(curl_url_1)+curl_url_2

zdanie = "HEHEHEHEHEHE"


data = json.dumps( {"body":zdanie})
c = pycurl.Curl()
c.setopt(pycurl.URL, curl_url)
c.setopt(pycurl.HTTPHEADER,curl_header)
#c.setopt(pycurl.CUSTOMREQUEST, "PUT")
c.setopt(pycurl.POST, 1)
c.setopt(pycurl.POSTFIELDS, data)

c.perform()