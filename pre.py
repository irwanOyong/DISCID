import pymongo
from bson.son import SON
import pprint
import json
import requests
import re
import time
from bson.regex import Regex

def connect():
	global client
	global db
	global colUser
	global colUserValidated
	global colTweet
	global colFrequency
	global colRecapFrequency
	global colFrequencyStemmed
	global colRecapFrequencyStemmed
	global colKeywordSeed
	global colKeywordFirst
	global colKeywordSecond
	global colKeywordSeedValidated
	global colKeywordFirstValidated
	global colKeywordSecondValidated
	global colKeywordSeedValidatedStemmed
	global colKeywordFirstValidatedStemmed
	global colKeywordSecondValidatedStemmed
	from pymongo import MongoClient
	try:
		client = MongoClient('localhost',27017)
		db = client['AMIKOM-Profiling']
		colUser = db.user
		colUserValidated = db.userValidated
		colTweet = db.tweet
		colFrequency = db.frequency
		colRecapFrequency = db.recapFrequency
		colFrequencyStemmed = db.frequencyStemmed
		colRecapFrequencyStemmed = db.recapFrequencyStemmed
		colKeywordSeed = db.keywordSeed
		colKeywordFirst = db.keywordFirst
		colKeywordSecond = db.keywordSecond
		colKeywordSeedValidated = db.keywordSeedValidated
		colKeywordFirstValidated = db.keywordFirstValidated
		colKeywordSecondValidated = db.keywordSecondValidated
		colKeywordSeedValidatedStemmed = db.keywordSeedValidatedStemmed
		colKeywordFirstValidatedStemmed = db.keywordFirstValidatedStemmed
		colKeywordSecondValidatedStemmed = db.keywordSecondValidatedStemmed
		print(client)
	except:
		print("Could not connect to MongoDB.")

def run(textInput):
	twitterProc(textInput)

def twitterProc(textInput):
	doc = textInput
	doc = re.sub(r'https?:\/\/.*[\r\n]*', '', doc)
	doc = re.sub(r'pic.twitter.*[\r\n]*', '', doc)
	doc = re.sub(r'twitter.com.*[\r\n]*', '', doc)
	doc = re.sub(r':\)', ' senyum', doc)
	doc = re.sub(r': \)', ' senyum', doc)
	doc = re.sub(r':D', ' tawa', doc)
	doc = re.sub(r'XD', ' tawa', doc)
	doc = re.sub(r':\(', ' sedih', doc)
	doc = re.sub(r': \(', ' sedih', doc)
	doc = re.sub(r":'\(", ' tangis', doc)
	doc = re.sub('(?=@)[^\s]+', '', doc)
	doc = re.sub('(?=RT)[^\s]+', '', doc)
	doc = re.sub('(?=#)[^\s]+', '', doc)
	doc = re.sub('[^A-Za-z\n ]+', '', doc.lower())

	#FORMALIZER GOES HERE
	doc = {"string": doc}
	# print(doc)
	formalized_doc = InaNLP_request("formalizer", doc)
	formalized_doc = json.loads(formalized_doc.text)
	doc = formalized_doc["data"]
	doc = {"string": doc}
	# print(doc)
	#STOPWORDS REMOVAL GOES HERE
	removedDoc = InaNLP_request("stopwords", doc)
	# print(removedDoc)
	removedDoc = json.loads(removedDoc.text)
	# print(removedDoc)
	doc = removedDoc["data"]
	#TOKENIZATION GOES HERE
	doc = doc.split()
	print(doc)
	#KEYWORD MATCHING GOES HERE
	for kata in doc:
		kata = re.sub('[^A-Za-z.,?!\n ]+', '', kata)
		if kata != "":
			regex = re.compile('^'+kata+'$')
			cursor = colKeywordSeedValidated.find({"seed": regex})
			if cursor.count() == 1:
				for doc in cursor:
					print("kata : ",kata,"// correspond: ",doc["correspond"])
					addRecap(doc["correspond"])
			else:
				cursor = colKeywordFirstValidated.find({"first": regex})
				if cursor.count() == 1:
					for doc in cursor:
						print("kata : ",kata,"// correspond: ",doc["correspond"])
						addRecap(doc["correspond"])
				else:
					cursor = colKeywordSecondValidated.find({"second": regex})
					if cursor.count() == 1:
						for doc in cursor:
							print("kata : ",kata,"// correspond: ",doc["correspond"])
							addRecap(doc["correspond"])

def addRecap(correspond):
	if correspond in recap:
		recap[correspond] += 1
	else:
		recap[correspond] = 1

def InaNLP_request(endpoint, payload):
	url = "http://localhost:9000/"+endpoint
	headers = {'content-type': 'application/json'}
	r = requests.post(url, data=json.dumps(payload), headers=headers)
	return r

def test_regex():
	loaded_doc = ":( : ( :) : ) :D XD :'( yang aku #hestek RT @adswdda rep ini boleh?  https:// twitter.com/sasasasa/sta tus/961978794851557376 aaa"
	print(loaded_doc)
	loaded_doc = re.sub(r':\)', ' senyum', loaded_doc)
	loaded_doc = re.sub(r': \)', ' senyum', loaded_doc)
	loaded_doc = re.sub(r':D', ' tawa', loaded_doc)
	loaded_doc = re.sub(r'XD', ' tawa', loaded_doc)
	loaded_doc = re.sub(r':\(', ' sedih', loaded_doc)
	loaded_doc = re.sub(r': \(', ' sedih', loaded_doc)
	loaded_doc = re.sub(r":'\(", ' tangis', loaded_doc)
	loaded_doc = re.sub('(?=@)[^\s]+', '', loaded_doc)
	loaded_doc = re.sub('(?=RT)[^\s]+', '', loaded_doc)
	loaded_doc = re.sub('(?=#)[^\s]+', '', loaded_doc)
	loaded_doc = re.sub(r'https?:\/\/.*[\r\n]*', '', loaded_doc)
	print(loaded_doc)

print("DISCID adalah bagian dari program profiling kepribadian DISC dalam bahasa Indonesia yang dikembangkan oleh tim AMIKOM-Profiling dari Universitas AMIKOM Yogyakarta.")
lanjut = True
while lanjut:
	textInput = input("Masukkan teks yang ingin diperiksa korespondensi DISC-nya : ")
	recap = {'D':0, 'I':0, 'S':0, 'C':0}
	connect()
	run(textInput)
	print(recap)
	if recap['D']+recap['I']+recap['S']+recap['C'] != 0:
		print("Korespondensi dengan kepribadian Dominance =","{:.2f}".format(recap['D']/(recap['D']+recap['I']+recap['S']+recap['C'])))
		print("Korespondensi dengan kepribadian Influence =","{:.2f}".format(recap['I']/(recap['D']+recap['I']+recap['S']+recap['C'])))
		print("Korespondensi dengan kepribadian Stability =","{:.2f}".format(recap['S']/(recap['D']+recap['I']+recap['S']+recap['C'])))
		print("Korespondensi dengan kepribadian Conscientious =","{:.2f}".format(recap['C']/(recap['D']+recap['I']+recap['S']+recap['C'])))
	else:
		print("Mohon periksa kembali teks yang dimasukkan.")
	if input("Lanjut gunakan program? y/n : ") == 'y':
		lanjut = True
	else:
		lanjut = False
# Calon presiden nomor urut 02 Prabowo Subianto menegaskan bahwa dirinya dan calon wakil presiden Sandiaga Uno telah memutuskan untuk menempuh jalur hukum terkait sengketa hasil Pemilu Presiden dan Wakil Presiden (Pilpres) 2019 yang diumumkan Komisi Pemilihan Umum (KPU) beberapa waktu lalu. Prabowo pun meminta para pendukungnya bersikap dewasa dan tenang dalam menyikapi apapun keputusan Mahkamah Konstitusi ( MK) atas sengketa tersebut. "Kita percaya pada hakim MK, apapun keputusannya kita sikapi dengan dewasa, tenang, berpikir untuk kepentingan bangsa dan negara. Itu sikap kami dan permohonan kami. Percayalah niat kami untuk kepentingan bangsa negara, umat dan rakyat," ujar Prabowo melalui video yang diterima Kompas.com, Selasa (11/6/2019).