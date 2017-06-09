import requests
from bs4 import BeautifulSoup 

#-=-=-=-=-=-=-=-=-=-=-=-=-=-
# CONSTANTS
#-=-=-=-=-=-=-=-=-=-=-=-=-=-

DRUG_LIST = ['Methamphetamine', 'Cocaine', 'Codeine']
EROWID_BASE_URI = 'https://erowid.org/experiences/'
EROWID_EXPERIENCE_ENDPOINT = 'https://erowid.org/'
VAULT_ENDPOINT = 'exp_list.shtml'


#-=-=-=-=-=-=-=-=-=-=-=-=-=-
# SCRAPE
#-=-=-=-=-=-=-=-=-=-=-=-=-=-

VAULT_URI = EROWID_BASE_URI + VAULT_ENDPOINT
req = requests.get(VAULT_URI)
soup = BeautifulSoup(req.text, 'html5lib')

#iterate over links to "First Times" pages
#thoguht process was that "First Times" would hold terms more indicative of drug effects 
#rather than long-term stories and experiences 
linkDict = {}
for link in soup.findAll('a', href= True, text= "First Times"):
	linkText = link['href']
	print linkText
	#Pull drug name from URL
	splitLinks = linkText.split('_')
	drug = ' '.join(linkText.split('_')[1:-2])
	linkDict[drug] = EROWID_BASE_URI + linkText 

#@KEY: drug name 
#@VALUE: list of URIs linking to experiences
experienceLinkDict = {}
for drug, uri in linkDict.iteritems(): 
	req = requests.get(uri)
	soup = BeautifulSoup(req.text)

	experienceTable = soup.find("table", {"class": "exp-list-table"})
	#scrape rows in table
	#First 2 rows are useless
	for index, tableRow in enumerate(experienceTable.findAll('tr')):
		if index > 1:
			linkList = []
			columns = tableRow.findAll('td')
			linkColumn = columns[1]
			experienceLink = linkColumn.find('a', href= True)
			experienceLink = EROWID_EXPERIENCE_ENDPOINT + experienceLink['href'][1:] 
			print experienceLink
			linkList.append(experienceLink)

	experienceLinkDict[drug] = linkList

print experienceLinkDict
