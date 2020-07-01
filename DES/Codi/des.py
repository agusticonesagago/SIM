"""
Simulació de l'Entrada d'una discoteca

Escenari:
  L'entrada de gent VIP i no VIP està determinada de forma aleatòria, amb els paràmetres
  TEMPS_ENTRE_ARRIBADES_VIP i TEMPS_ENTRE_ARRIBADES_NO_VIP. En aquest escenari els clients VIP 
  tindran prioritat a l'hora d'entrar. La simulació durarà un temps determinat per la
  variable TEMPS_SIMULACIO, durant la simulació els clients es generaran amb 2 variables
  aleatories, alcohol_en_sang i ganes_de_ballar.

  - alcohol_en_sang : determina si el client pot entrar i el temps que es tarda a atendre'l.
  - ganes_de_ballar : determina el temps que el client està disposat a esperar abans de marxar
  					  de la cua.

  Aquest client serà admès si alcohol_en_sang és menor a TASA_ADMISSIÓ (alcohol màxim permès en sang).

Recursos:
  - Cobradors
  - Porter

Entitats:
  - Clients VIP
  - Clients no VIP

"""

import itertools
import random

import simpy

TEMPS_SIMULACIO = 2000   					# temps en simulació en segons
TEMPS_ENTRE_ARRIBADES_NO_VIP = [30, 90] 	# temps entre arribades de clients no vip
TEMPS_ENTRE_ARRIBADES_VIP = [120, 240] 		# temps entre arribades de clients vip
TEMPS_PAGAR_ENTRADA = [60, 90] 				# interval de temps per pagar l'entrada
LLAVOR = 14 								# llavor per generar randoms aleatoris
NUMERO_PORTERS = 1 							# número de recursos porter
NUMERO_COBRADORS = 2 						# número de recursos cobrador
TASA_ADMISSIÓ = 0.75						# tasa d'acceptació d'alcohol en els clients 
TEMPS_ABANS_MARXAR = 300					# temps màxim d'espera a la cua

NUMERO_BORRATXOS = 0
NUMERO_PERSONES_DINS_DISCOTECA = 0
TEMPS_ESPERA = 0
TEMPS_ESPERA_VIP = 0
TEMPS_ESPERA_NO_VIP = 0
NUMERO_PERSONES_ATESES = 0
NUMERO_PERSONES_ATESES_VIP = 0
NUMERO_PERSONES_ATESES_NO_VIP = 0
NUMERO_PERSONES_CANSADES_ESPERAR = 0

def persona_no_vip(name, env, porter, cobrador, alcohol_en_sang, ganes_de_ballar):
	
	"""
	 El client arriba a l'entrada de la discoteca i es posa a la fila per esperar
	 el seu torn per ser atès pel porter i així poder entrar i pagar la seva entrada
	 a la discoteca.
	"""
	arxiu_traces.write("%s arriba a l'entrada de la discoteca a l'instant: %.1f \n" % (name, env.now))
	print("%s arriba a l'entrada de la discoteca a l'instant: %.1f" % (name, env.now))

	with porter.request(0, False) as req:
		
		arribada = env.now

		yield req

		cansat = False
		comença_atendre = env.now

		if((TEMPS_ABANS_MARXAR+ganes_de_ballar*150)<=comença_atendre-arribada):
			arxiu_traces.write("%s s'ha cansat d'esperar i s'en va a l'instant: %.1f \n" % (name, env.now))
			print("%s s'ha cansat d'esperar i s'en va a l'instant: %.1f" % (name, env.now))
			global NUMERO_PERSONES_CANSADES_ESPERAR
			NUMERO_PERSONES_CANSADES_ESPERAR += 1
			cansat = True
		else:
			global TEMPS_ESPERA
			TEMPS_ESPERA += comença_atendre-arribada

			global TEMPS_ESPERA_NO_VIP
			TEMPS_ESPERA_NO_VIP += comença_atendre-arribada

			global NUMERO_PERSONES_ATESES
			NUMERO_PERSONES_ATESES += 1

			global NUMERO_PERSONES_ATESES_NO_VIP
			NUMERO_PERSONES_ATESES_NO_VIP += 1

			if(alcohol_en_sang >= TASA_ADMISSIÓ):
				yield env.timeout(30+60*alcohol_en_sang)
				print("%s està massa borratxa i no pot entrar" % name)
				arxiu_traces.write("%s està massa borratxa i no pot entrar \n" % name)
				global NUMERO_BORRATXOS
				NUMERO_BORRATXOS += 1
			else:
				yield env.timeout(60+60*alcohol_en_sang)

				print("%s tarda %.1f segons en rebre revisat el DNI" % (name, env.now - comença_atendre))
				arxiu_traces.write("%s tarda %.1f segons en revisar el DNI \n" % (name, env.now - comença_atendre))

		if(alcohol_en_sang < TASA_ADMISSIÓ and not cansat):
			with cobrador.request() as req:
				comença_atendre = env.now
				
				yield req
				yield env.timeout(random.randint(*TEMPS_PAGAR_ENTRADA))
				print("%s tarda %.1f segons en pagar l'entrada" % (name, env.now - comença_atendre))
				arxiu_traces.write("%s tarda %.1f segons en pagar l'entrada \n" % (name, env.now - comença_atendre))

				global NUMERO_PERSONES_DINS_DISCOTECA
				NUMERO_PERSONES_DINS_DISCOTECA += 1

def persona_vip(name, env, porter, cobrador, alcohol_en_sang, ganes_de_ballar):
	
	"""
	 El client arriba a l'entrada de la discoteca i es posa a la fila per esperar
	 el seu torn per ser atès pel porter, aquest tindrà prioritat davant els no VIP, 
	 i així poder entrar i pagar la seva entrada a la discoteca.
	"""
	arxiu_traces.write("%s arriba a l'entrada de la discoteca a l'instant: %.1f \n" % (name, env.now))
	print("%s arriba a l'entrada de la discoteca a l'instant: %.1f" % (name, env.now))

	with porter.request(-1, False) as req:
		
		arribada = env.now

		yield req

		cansat = False
		comença_atendre = env.now
		if((TEMPS_ABANS_MARXAR+ganes_de_ballar*150)<=comença_atendre-arribada):

			arxiu_traces.write("%s s'ha cansat d'esperar i s'en va a l'instant: %.1f \n" % (name, env.now))
			print("%s s'ha cansat d'esperar i s'en va a l'instant: %.1f" % (name, env.now))
			global NUMERO_PERSONES_CANSADES_ESPERAR
			NUMERO_PERSONES_CANSADES_ESPERAR += 1
			cansat = True

		else:
			global TEMPS_ESPERA
			TEMPS_ESPERA += comença_atendre-arribada

			global TEMPS_ESPERA_VIP
			TEMPS_ESPERA_VIP += comença_atendre-arribada

			global NUMERO_PERSONES_ATESES
			NUMERO_PERSONES_ATESES += 1

			global NUMERO_PERSONES_ATESES_VIP
			NUMERO_PERSONES_ATESES_VIP += 1

			if(alcohol_en_sang >= TASA_ADMISSIÓ):
				yield env.timeout(30+60*alcohol_en_sang)
				print("%s està massa borratxa i no pot entrar" % name)
				arxiu_traces.write("%s està massa borratxa i no pot entrar \n" % name)
				global NUMERO_BORRATXOS
				NUMERO_BORRATXOS += 1
			else:
				yield env.timeout(60+60*alcohol_en_sang)

				print("%s tarda %.1f segons en revisar el DNI" % (name, env.now - comença_atendre))
				arxiu_traces.write("%s tarda %.1f segons en revisar el DNI \n" % (name, env.now - comença_atendre))

	if(alcohol_en_sang < TASA_ADMISSIÓ and not cansat):
		with cobrador.request() as req:
			comença_atendre = env.now
			
			yield req
			yield env.timeout(random.randint(*TEMPS_PAGAR_ENTRADA))
			print("%s tarda %.1f segons en pagar l'entrada" % (name, env.now - comença_atendre))
			arxiu_traces.write("%s tarda %.1f segons en pagar l'entrada \n" % (name, env.now - comença_atendre))

			global NUMERO_PERSONES_DINS_DISCOTECA
			NUMERO_PERSONES_DINS_DISCOTECA += 1

def generador_persona_no_vip(env, porter, cobrador):
	for i in itertools.count():
		yield env.timeout(random.randint(*TEMPS_ENTRE_ARRIBADES_NO_VIP))
		env.process(persona_no_vip('Persona No VIP %d' % i, env, porter, cobrador, random.random(), random.random()))


def generador_persona_vip(env, porter, cobrador):
	for i in itertools.count():
		yield env.timeout(random.randint(*TEMPS_ENTRE_ARRIBADES_VIP))
		env.process(persona_vip('Persona VIP %d' % i, env, porter, cobrador, random.random(), random.random()))

# Setup and start the simulation
print('Entrada a la discoteca')

informacio=[]
with open("variables.txt", 'r') as fileobj:
    for row in fileobj:
        informacio.append(row.rstrip('\n'))

if(len(informacio)>0):
	TEMPS_SIMULACIO = int(informacio[0])
	TEMPS_ENTRE_ARRIBADES_NO_VIP = [int(informacio[1]),int(informacio[2])]
	TEMPS_ENTRE_ARRIBADES_VIP = [int(informacio[3]),int(informacio[4])]
	TEMPS_PAGAR_ENTRADA = [int(informacio[5]),int(informacio[6])]
	TEMPS_ABANS_MARXAR = int(informacio[7])
	LLAVOR = int(informacio[8])
	NUMERO_PORTERS = int(informacio[9])
	NUMERO_COBRADORS = int(informacio[10])
	TASA_ADMISSIÓ = float(informacio[11])



random.seed(LLAVOR)

arxiu_traces = open("traces.txt", 'w') 

# Create environment and start processes
env = simpy.Environment()
porter = simpy.PriorityResource(env, NUMERO_PORTERS)
cobrador = simpy.Resource(env, NUMERO_COBRADORS)
env.process(generador_persona_no_vip(env, porter, cobrador))
env.process(generador_persona_vip(env, porter, cobrador))

env.run(until=TEMPS_SIMULACIO)

arxiu = open("estadístics.txt", 'w') 
arxiu.write("Temps mig d'espera en la cua: %d \n" % (TEMPS_ESPERA/NUMERO_PERSONES_ATESES))
arxiu.write("Temps mig d'espera VIP en la cua: %d \n" % (TEMPS_ESPERA_VIP/NUMERO_PERSONES_ATESES_VIP))
arxiu.write("Temps mig d'espera NO VIP en la cua: %d \n" % (TEMPS_ESPERA_NO_VIP/NUMERO_PERSONES_ATESES_NO_VIP))
arxiu.write("Número de persones que no les han deixat entrar: %d \n" % NUMERO_BORRATXOS)
arxiu.write("Número de persones que s'han cansat d'esperar: %d \n" % NUMERO_PERSONES_CANSADES_ESPERAR)
arxiu.write("Número de persones que han entrat a la discoteca: %d \n" % NUMERO_PERSONES_DINS_DISCOTECA)
arxiu.write("Número de persones ateses: %d \n" % NUMERO_PERSONES_ATESES)
arxiu.write("Número de persones VIP ateses: %d \n" % NUMERO_PERSONES_ATESES_VIP)
arxiu.write("Número de persones NO VIP ateses: %d \n" % NUMERO_PERSONES_ATESES_NO_VIP)
arxiu.close() 

print("")
print("Temps mig d'espera en la cua: %d" % (TEMPS_ESPERA/NUMERO_PERSONES_ATESES))
print("Temps mig d'espera VIP en la cua: %d" % (TEMPS_ESPERA_VIP/NUMERO_PERSONES_ATESES_VIP))
print("Temps mig d'espera NO VIP en la cua: %d" % (TEMPS_ESPERA_NO_VIP/NUMERO_PERSONES_ATESES_NO_VIP))
print("Número de persones que no les han deixat entrar: %d" % NUMERO_BORRATXOS)
print("Número de persones que s'han cansat d'esperar: %d" % NUMERO_PERSONES_CANSADES_ESPERAR)
print("Número de persones que han entrat a la discoteca: %d" % NUMERO_PERSONES_DINS_DISCOTECA)
print("Número de persones ateses: %d" % NUMERO_PERSONES_ATESES)
print("Número de persones VIP ateses: %d" % NUMERO_PERSONES_ATESES_VIP)
print("Número de persones NO VIP ateses: %d" % NUMERO_PERSONES_ATESES_NO_VIP)
