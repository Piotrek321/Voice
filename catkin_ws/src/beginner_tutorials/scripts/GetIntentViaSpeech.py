# -*- coding: utf-8 -*-
import pycurl
import cStringIO
import json



import requests
import urllib

key = 'THAKYMA767MXNDXJOZXDUBGHGFIRW5ER'

def query(query):
    headers = {'Authorization': 'Bearer ' + key}
    url = 'https://api.wit.ai/message?q=' + urllib.quote(query)
    return requests.get(url, headers = headers)

def queryAudio(filename):
    wav_file = open(filename, 'rb')
    headers = {'Authorization': 'Bearer ' + key, 'Content-Type': 'audio/wav'}
    url =  'https://api.wit.ai/speech'
    data = wav_file
    r = requests.post(url, headers = headers, data = data)
    wav_file.close()
    return r



jsonResponse = queryAudio('tekst.wav').text
dataDict = json.loads(jsonResponse)
print (dataDict)
intent= dataDict["outcomes"][0]["intent"]
print (intent)

"""
key = 'THAKYMA767MXNDXJOZXDUBGHGFIRW5ER'

def query(query):
    headers = {'Authorization': 'Bearer ' + key}
    url = 'https://api.wit.ai/message?q=' + urllib.quote(query)
    return requests.get(url, headers = headers)

def queryAudio(filename):
    wav_file = open(filename, 'rb')
    headers = {'Authorization': 'Bearer ' + key, 'Content-Type': 'audio/wav'}
    url =  'https://api.wit.ai/speech'
    data = wav_file
    r = requests.post(url, headers = headers, data = data)
    wav_file.close()
    return r


"""