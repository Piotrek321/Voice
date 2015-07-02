import alsaaudio, wave, numpy

def nagraj(czasMowy):
	RATE = 8000
	CHUNK = 1024
	inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE)
	inp.setchannels(1)
	inp.setrate(RATE)
	inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
	inp.setperiodsize(CHUNK)

	w = wave.open('src/beginner_tutorials/Dzwieki/tekst.wav', 'w')
	w.setnchannels(1)
	w.setsampwidth(2)
	w.setframerate(RATE)
	print "NAgrywanie"


	for x in range(int(RATE / CHUNK * czasMowy)):
	    l, data = inp.read()
	    a = numpy.fromstring(data, dtype='int16')
	    #print numpy.abs(a).mean()
	    w.writeframes(data)
	return w.writeframes(data)