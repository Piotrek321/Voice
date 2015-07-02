mozliweKierunki = ['lewo' , 'prawo', 'przód', 'tył']

def zweryfikujKierunek(kierunek):
	global angular
	global linear
	global stala_linear
	if (kierunek.startswith('lew')):
		linear = 1.55
		angular = 1.55
		kierunek = mozliweKierunki[0]
		return kierunek
	elif (kierunek.startswith('praw')):
		linear = 1.55
		angular = 1.55
		kierunek = mozliweKierunki[1]
		return kierunek
	elif (kierunek.startswith('prz')):
		linear = stala_linear
		kierunek = mozliweKierunki[2]
		return kierunek
	elif (kierunek.startswith('ty')):
		linear = stala_linear
		kierunek = mozliweKierunki[3]
		return kierunek



def Jedz(ilosc, kierunek, jak):
		global linear
		global angular
		print ("jedź kierunek: " + str(kierunek))
		print "jedz linear: " + str(linear)
		zweryfikujKierunek(kierunek)
		jak = jakJechac(jak)

		print("jedz jak: " +str(jak))
		print ("Jedz ilosc: " + str(ilosc))
		if(jak == 1):
			if not ilosc:
				ilosc = 2
			angular *= int(ilosc)
			linear *= int(ilosc)
			print("Jedz ifjak linear: " + str(linear))
		elif (jak == -1):
			if not ilosc:
				ilosc = 2
			angular /= float(ilosc)
			linear /= float(ilosc)

		if kierunek == 'tył' :
			linear = - linear
		if kierunek == 'prawo' :
			angular = - angular

		print "Jedz angular: " + str(angular)
		print "Jedz linear: " + str(linear)
		ruszZolwia(linear,angular)
		linear = 0
		angular = 0