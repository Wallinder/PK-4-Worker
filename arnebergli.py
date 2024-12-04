from bs4 import BeautifulSoup
import requests
import json

class arnebergli:
	url = "https://www.arnebergli.no"

	def findSection(self):
		r = requests.get(self.url + "/ansatte")
		soup = BeautifulSoup(r.content, "html.parser")
		tables = soup.findAll('div', attrs={'class': 'row'})
		return tables

	def ansatt(self):
		ansattliste = []
		ansattbilde = {}
		#person = person.lower()
		tables = self.findSection()
		for table in tables:
			h3 = table.find('h3')
			if h3 == None:
				continue
			ansatt = h3.text.split(" ")[0].lower()
			ansattliste.append(ansatt)
			img = table.find('source', attrs={'media': '(max-width: 1499px)'})
			ansattbilde[ansatt] = img["srcset"]
		return ansattliste, ansattbilde

#print(arnebergli().ansatt()[0])

