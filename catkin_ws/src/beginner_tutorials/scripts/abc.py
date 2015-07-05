#!/usr/bin/env python
#-*- coding: utf-8 -*-
import requests
import urllib
import json
import codecs
import tkFileDialog
import sys



key = 'THAKYMA767MXNDXJOZXDUBGHGFIRW5ER'

def query(query):
    headers = {'Authorization': 'Bearer ' + key}
    url = 'https://api.wit.ai/message?q=' + urllib.quote(query)
    return requests.get(url, headers = headers)

def queryAudio(filename):
    wav_file = open(filename, 'rb')
    headers = {'Authorization': 'Bearer ' + key, 'Content-Type': 'audio/wav'}
    url =  'https://api.wit.ai/speech?v=20141022'
    data = wav_file
    r = requests.post(url, headers = headers, data = data)
    wav_file.close()
    return r

b = queryAudio('tekst.wav').text


a= json.loads(b,encoding = 'iso-8859-2')
print a

encoded_str = a["outcomes"][0]["_text"].encode("'iso-8859-2")
print encoded_str