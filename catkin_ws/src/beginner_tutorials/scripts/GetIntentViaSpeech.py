# -*- coding: utf-8 -*-
import pycurl
import cStringIO
import json

import os
import wave

import urllib
import cStringIO
import alsaaudio



key = 'THAKYMA767MXNDXJOZXDUBGHGFIRW5ER'

curl_header = ["Authorization: Bearer THAKYMA767MXNDXJOZXDUBGHGFIRW5ER",
                 "Content-Type: audio/wav"]
curl_url = 'https://api.wit.ai/speech?v=20150626'

postdict = [ ('userfile', open('tekst.wav', 'rb').read()) ]

c = pycurl.Curl()
c.setopt(pycurl.URL, curl_url)
c.setopt(pycurl.HTTPHEADER,curl_header)
print"ABC"
c.setopt(c.HTTPPOST,postdict)

#c.setopt(c.WRITEDATA, )
c.perform()
c.close()











"""



#c.setopt(c.HTTPPOST,[("data-binary", (c.FORM_FILE, "tekst.wav"))])
c.setopt(c.POSTFIELDS, '@tekst.wav')
c.setopt(c.VERBOSE, 1)
#c.setopt(c.WRITEFUNCTION, response.write)
c.perform()
c.close()

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