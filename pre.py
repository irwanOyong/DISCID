import pymongo
from bson.son import SON
import pprint
import json
import nltk
import requests
import re
import time
import pandas as pd
from bson.regex import Regex
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import numpy as np

global loaded_seed
global isrecap
global KEY0
global KEY1
global KEY2
isrecap = False
KEY0=0
KEY1=0
KEY2=0

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

def tweetCount():
	vTotalUser = 0
	vTotalTweet = 0
	connect()
	query = {}
	projection = {}
	projection["username"] = 1.0
	projection["_id"] = 0.0
	sort = [ (u"username", 1) ]
	cursor = colUserValidated.find(query, projection = projection, sort = sort, no_cursor_timeout=True)
	for user in cursor:
		print(user)
		query = {"usernameTweet":user['username']}
		projection = {}
		projection["username"] = 1.0
		cursor = colTweet.find(query, projection = projection, no_cursor_timeout=True)
		if cursor.count() != 0:
			vTotalUser+=1
			for user2 in cursor:
				vTotalTweet+=1
	print(vTotalUser, vTotalTweet)

def plotCM(y_true,y_pred):
	print(len(y_true))
	print(len(y_pred))
	pdy_true = pd.Series(y_true)
	pdy_pred = pd.Series(y_pred)
	print(pd.crosstab(pdy_true, pdy_pred, rownames=['True'], colnames=['Predicted'], margins=True))
	labels = ["C", "D", "I", "S"]
	cm = confusion_matrix(y_true, y_pred, labels=labels)
	fig = plt.figure()
	ax = fig.add_subplot(111)
	cax = ax.matshow(cm)
	plt.title('Confusion matrix of the classifier')
	fig.colorbar(cax)
	ax.set_xticklabels([''] + labels)
	ax.set_yticklabels([''] + labels)
	plt.xlabel('Predicted')
	plt.ylabel('True')
	plt.show()

def compareStemmed():
	vTrue = 0
	vFalse = 0
	vTotal = 0
	y_true = []
	y_pred = []
	connect()
	query = {}
	projection = {}
	projection["username"] = 1.0
	projection["correspond"] = 1.0
	projection["_id"] = 0.0
	sort = [ (u"username", 1) ]
	cursor = colUserValidated.find(query, projection = projection, sort = sort, no_cursor_timeout=True)
	for user in cursor:
		print(user)
		query = {"username":user['username']}
		projection = {}
		projection["username"] = 1.0
		projection["correspond"] = 1.0
		cursor = colRecapFrequencyStemmed.find(query, projection = projection, no_cursor_timeout=True)
		if cursor.count() != 0:
			vTotal+=1
			hit = 0
			for user2 in cursor:
				print(user['correspond']+' // '+user2['correspond'])
				if user['correspond'] == user2['correspond']:
					hit=1
			if hit == 1:
				vTrue+=1
			else:
				vFalse+=1
			y_true.append(user['correspond'])
			y_pred.append(user2['correspond'])
	print(vTotal, vTrue, vFalse, vTrue/vTotal*100)
	plotCM(y_true,y_pred)

def compare():
	vTrue = 0
	vFalse = 0
	vTotal = 0
	y_true = []
	y_pred = []
	connect()
	query = {}
	projection = {}
	projection["username"] = 1.0
	projection["correspond"] = 1.0
	projection["_id"] = 0.0
	sort = [ (u"username", 1) ]
	cursor = colUserValidated.find(query, projection = projection, sort = sort, no_cursor_timeout=True)
	for user in cursor:
		print(user)
		query = {"username":user['username']}
		projection = {}
		projection["username"] = 1.0
		projection["correspond"] = 1.0
		cursor = colRecapFrequency.find(query, projection = projection, no_cursor_timeout=True)
		if cursor.count() != 0:
			vTotal+=1
			hit = 0
			for user2 in cursor:
				print(user['correspond']+' // '+user2['correspond'])
				if user['correspond'] == user2['correspond']:
					hit=1
			if hit == 1:
				vTrue+=1
			else:
				vFalse+=1
			y_true.append(user['correspond'])
			y_pred.append(user2['correspond'])
		else:
			print(user['username']," tidak ditemukan")
	print(vTotal, vTrue, vFalse, vTrue/vTotal*100)
	plotCM(y_true,y_pred)

def filter_colTweet():
	connect()
	query = {}
	projection = {}
	projection["usernameTweet"] = 1.0
	projection["_id"] = 0.0
	sort = [ (u"usernameTweet", 1) ]
	cursor = colTweet.find(query, projection = projection, no_cursor_timeout=True)
	try:
		for user in cursor:
			print("ketemu :",user)
			query = {"screen_name":user["usernameTweet"]}
			projection = {}
			projection["screen_name"] = 1.0
			sort = [ (u"screen_name", 1) ]
			cursor = colUser.find(query, projection = projection, sort = sort, no_cursor_timeout=True)
			if cursor.count() == 0:
				print("hapus")
				qFrom = { "usernameTweet":user["usernameTweet"]}
				result = colTweet.delete_many(qFrom)
				print(result.deleted_count," documents deleted")
			else:
				print("tidak hapus")
	finally:
	    client.close()	

def migrate():
	connect()
	text = open('/home/airone/AMIKOM-Profiling/UserListDone.txt','r+')
	for user in text:
		user = re.sub('[\n]+', '', user)
		print(user)
		query = {"screen_name":user}
		projection = {}
		projection["avatar"] = 1.0
		projection["name"] = 1.0
		projection["screen_name"] = 1.0
		projection["ID"] = 1.0
		projection["_id"] = 0.0
		sort = [ (u"screen_name", 1) ]
		cursor = colUser.find(query, projection = projection, sort = sort, no_cursor_timeout=True)
		try:
			for user in cursor:
				print("ketemu :",user)
				result = colUser2.insert_one({"avatar":user["avatar"],"name":user["name"],"screen_name":user["screen_name"],"ID":user["ID"]})
				query = {"usernameTweet":user["screen_name"]}
				projection = {}
				projection["user_id"] = 1.0
				projection["usernameTweet"] = 1.0
				projection["ID"] = 1.0
				projection["text"] = 1.0
				projection["is_reply"] = 1.0
				projection["datetime"] = 1.0
				sort = [ (u"ID", 1) ]
				cursor = colTweet.find(query, projection = projection, sort = sort, no_cursor_timeout=True)
				for tweet in cursor:
					print(user["screen_name"]+" / "+tweet["ID"])
					result = colTweet2.insert_one({"user_id":tweet["user_id"],"usernameTweet":tweet["usernameTweet"],"ID":tweet["ID"],"text":tweet["text"],"is_reply":tweet["is_reply"],"datetime":tweet["datetime"]})
		finally:
		    client.close()			

def migrate_tweet():
	connect()
	query = {}
	projection = {}
	projection["screen_name"] = 1.0
	projection["_id"] = 0.0
	sort = [ (u"screen_name", 1) ]
	cursor = colUser2.find(query, projection = projection, sort = sort, no_cursor_timeout=True)
	try:
		for user in cursor:
			query = {"usernameTweet":user["screen_name"]}
			projection = {}
			projection["user_id"] = 1.0
			projection["ID"] = 1.0
			projection["text"] = 1.0
			projection["is_reply"] = 1.0
			projection["datetime"] = 1.0
			# projection["_id"] = 0.0
			sort = [ (u"ID", 1) ]
			cursor = colTweet.find(query, projection = projection, sort = sort, no_cursor_timeout=True)
			for tweet in cursor:
				print(user["screen_name"]+" / "+tweet["ID"])
				result = colTweet2.insert_one({"user_id":tweet["user_id"],"ID":tweet["ID"],"text":tweet["text"],"is_reply":tweet["is_reply"],"datetime":tweet["datetime"]})

	finally:
	    client.close()			

def generate_text(): #generate raw text from ID-DepreSD.collection
	connect()
	query = {}
	projection = {}
	projection["string"] = 1.0
	projection["_id"] = 0.0
	sort = [ (u"usernameTweet", 1), (u"datetime", 1) ]
	cursor = colTweet.find(query, projection = projection, sort = sort)
	try:
		with open('/home/airone/ID-DepreSD/raw-data.txt','a') as outfile:
			for doc in cursor:
				doc = json.dumps(doc)
				loaded_doc = json.loads(doc)
				json.dump(loaded_doc['string'], outfile)
				outfile.write('\n')
	finally:
	    client.close()

def recapWeighted():
	connect()
	pipe = [
    {
        u"$group": {
            u"_id": {
                u"username": u"$username",
                u"correspond": u"$correspond"
            },
            u"total": {
                u"$sum": u"$terbobot"
            }
        }
    }, 
    {
        u"$project": {
            u"_id": 0,
            u"username": u"$_id.username",
            u"correspond": u"$_id.correspond",
            u"total": u"$total"
        }
    }, 
    {
        u"$sort": SON([ (u"username", 1),(u"total", -1) ])
    }
	]
	result = colRecapFrequency.delete_many({})
	cursor = colFrequency.aggregate(pipeline=pipe)
	for user in cursor:
		print(user)
		query = {}
		query = {"username":user['username']}
		cursor = colRecapFrequency.find(query)
		# if cursor.count() < 2:
		if cursor.count() == 0:
			result = colRecapFrequency.insert_one({"username":user['username'],"total":user['total'],"correspond":user['correspond']})
			print("Simpan - ",user)

def recap():
	connect()
	pipe = [
    {
        u"$group": {
            u"_id": {
                u"username": u"$username",
                u"correspond": u"$correspond"
            },
            u"total": {
                u"$sum": u"$jumlah"
            }
        }
    }, 
    {
        u"$project": {
            u"_id": 0,
            u"username": u"$_id.username",
            u"correspond": u"$_id.correspond",
            u"total": u"$total"
        }
    }, 
    {
        u"$sort": SON([ (u"username", 1),(u"total", -1) ])
    }
	]
	result = colRecapFrequency.delete_many({})
	cursor = colFrequency.aggregate(pipeline=pipe)
	for user in cursor:
		print(user)
		query = {}
		query = {"username":user['username']}
		cursor = colRecapFrequency.find(query)
		# if cursor.count() < 2:
		if cursor.count() == 0:
			result = colRecapFrequency.insert_one({"username":user['username'],"total":user['total'],"correspond":user['correspond']})
			print("Simpan - ",user)

def weight():
	connect()
	query = {}
	projection = {}
	projection["username"] = 1.0
	projection["kata"] = 1.0
	projection["level"] = 1.0
	projection["jumlah"] = 1.0
	projection["_id"] = 1.0
	sort = [ (u"username", 1), (u"jumlah", 1) ]
	cursor = colFrequency.find(query, projection = projection, sort = sort)
	for user in cursor:
		print(user)
		if user['level'] == "seed":
			terbobot = user['jumlah'] * 1
		elif user['level'] == "first":
			terbobot = user['jumlah'] * 0.85
		elif user['level'] == "second":
			terbobot = user['jumlah'] * 0.35
		else:
			print('Not a valid level')
			quit()
		result = colFrequency.update({
				'_id': user['_id']
				},{'$set': {'terbobot': terbobot}
				}, upsert=False)

def run():
	start_time = time.time()
	urut = 1
	connect()
	# with open('/home/airone/ID-DepreSD/scoring-result.txt','w') as outfile:
	# 	outfile.write("uname,depressed,stdscore,stdcount,stdcount0,stdscorecount,stdscorecount0,twtscore,twtcount,twtcount0,"+
	# 		"twtscorecount,twtscorecount0")
	# 	outfile.write('\n')
	query = {}
	projection = {}
	projection["screen_name"] = 1.0
	projection["_id"] = 0.0
	sort = [ (u"screen_name", 1) ]
	cursor = colUser.find(query, projection = projection, sort = sort, no_cursor_timeout=True)
	print(cursor.count())
	try:
		for user in cursor:
			uname = "user"+str(urut)
			user = json.dumps(user["screen_name"])
			loaded_user = json.loads(user)
			print(loaded_user)
			print("User ke-",urut)
			query = {"username":loaded_user}
			projection["username"] = 1.0
			projection["_id"] = 0.0
			sort = [ (u"username", 1) ]
			cursor = colFrequency.find(query, projection = projection, sort = sort, no_cursor_timeout=True)
			if cursor.count() == 0:		
				twitterProc(loaded_user)
				urut = urut + 1
			else:
				print("skip ",loaded_user)
				urut = urut + 1
				continue
			# if urut == 2:
			# 	quit()
	finally:
	    client.close()
	cursor.close()
	print("--- %s seconds ---" % (time.time() - start_time))

def twitterProc(uname):
	#connect()
	global twtcount
	global prnlist
	global KEY0
	global KEY1
	global KEY2
	query = {"usernameTweet":uname}
	projection = {}
	projection["text"] = 1.0
	projection["date"] = 1.0
	projection["_id"] = 1.0
	sort = [ (u"date", 1) ]
	tweet = 0
	twtcount = 0
	cursor = colTweet.find(query, projection = projection, sort = sort, no_cursor_timeout=True)
	try:
		for doc in cursor:
			tweetID = doc["_id"]
			# print(tweetID)
			# print(doc['text'])
			doc = re.sub(r'https?:\/\/.*[\r\n]*', '', doc['text'])
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
			twtcount+=1
			tweet=tweet+1
			# print("Tweet : "+str(tweet))
			recapinc = 0
			tweetDepreSD = 0
			phrase = 0
			prnlist = {"prn":""}			
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
						KEY0=KEY0+1
						# save_frequency(kata)
						# print("  found KEY0: ",kata)
						for doc in cursor:
							# print("correspond: ",doc["correspond"])
							saveFrequency(uname,kata,doc["correspond"],level="seed")
					else:
						cursor = colKeywordFirstValidated.find({"first": regex})
						if cursor.count() == 1:
							KEY1=KEY1+1
							# print("  found KEY1: ",kata)
							for doc in cursor:
								# print("correspond: ",doc["correspond"])
								saveFrequency(uname,kata,doc["correspond"],level="first")
						else:
							cursor = colKeywordSecondValidated.find({"second": regex})
							if cursor.count() == 1:
								KEY2=KEY2+1
								# print("  found KEY2: ",kata)
								for doc in cursor:
									# print("correspond: ",doc["correspond"])
									saveFrequency(uname,kata,doc["correspond"],level="second")
	finally:
	    client.close()

def saveFrequency(uname,kata,correspond,level): #save first-degree synonym from Kateglo
	query = {}
	# query["kata"] = Regex(u".*"+kata+".*", "i")
	query = {"$and":[{"kata": {"$regex" : kata}},{"username": {"$regex" : uname}}]}
	cursor = colFrequency.find(query)
	if cursor.count() == 0:
		result = colFrequency.insert_one({"username":uname,"kata":kata,"correspond":correspond,"jumlah":1,"level":level})
	else:
		result = colFrequency.update_one({"$and":[{"kata": {"$regex" : kata}},{"username": {"$regex" : uname}}]}, {'$inc': {'jumlah': 1}})

def recapStemmedWeighted():
	connect()
	pipe = [
    {
        u"$group": {
            u"_id": {
                u"username": u"$username",
                u"correspond": u"$correspond"
            },
            u"total": {
                u"$sum": u"$terbobot"
            }
        }
    }, 
    {
        u"$project": {
            u"_id": 0,
            u"username": u"$_id.username",
            u"correspond": u"$_id.correspond",
            u"total": u"$total"
        }
    }, 
    {
        u"$sort": SON([ (u"username", 1),(u"total", -1) ])
    }
	]
	result = colRecapFrequencyStemmed.delete_many({})
	cursor = colFrequencyStemmed.aggregate(pipeline=pipe)
	for user in cursor:
		print(user)
		query = {}
		query = {"username":user['username']}
		cursor = colRecapFrequencyStemmed.find(query)
		# if cursor.count() < 2:
		if cursor.count() == 0:
			result = colRecapFrequencyStemmed.insert_one({"username":user['username'],"total":user['total'],"correspond":user['correspond']})
			print("Simpan - ",user)

def recapStemmed():
	connect()
	pipe = [
    {
        u"$group": {
            u"_id": {
                u"username": u"$username",
                u"correspond": u"$correspond"
            },
            u"total": {
                u"$sum": u"$jumlah"
            }
        }
    }, 
    {
        u"$project": {
            u"_id": 0,
            u"username": u"$_id.username",
            u"correspond": u"$_id.correspond",
            u"total": u"$total"
        }
    }, 
    {
        u"$sort": SON([ (u"username", 1),(u"total", -1) ])
    }
	]
	result = colRecapFrequencyStemmed.delete_many({})
	cursor = colFrequencyStemmed.aggregate(pipeline=pipe)
	for user in cursor:
		print(user)
		query = {}
		query = {"username":user['username']}
		cursor = colRecapFrequencyStemmed.find(query)
		# if cursor.count() < 2:
		if cursor.count() == 0:
			result = colRecapFrequencyStemmed.insert_one({"username":user['username'],"total":user['total'],"correspond":user['correspond']})
			print("Simpan - ",user)

def weightStemmed():
	connect()
	query = {}
	projection = {}
	projection["username"] = 1.0
	projection["kata"] = 1.0
	projection["level"] = 1.0
	projection["jumlah"] = 1.0
	projection["_id"] = 1.0
	sort = [ (u"username", 1), (u"jumlah", 1) ]
	cursor = colFrequencyStemmed.find(query, projection = projection, sort = sort)
	for user in cursor:
		print(user)
		if user['level'] == "seed":
			terbobot = user['jumlah'] * 1
		elif user['level'] == "first":
			terbobot = user['jumlah'] * 0.85
		elif user['level'] == "second":
			terbobot = user['jumlah'] * 0.35
		else:
			print('Not a valid level')
			quit()
		result = colFrequencyStemmed.update({
				'_id': user['_id']
				},{'$set': {'terbobot': terbobot}
				}, upsert=False)

def runStemmed():
	start_time = time.time()
	urut = 1
	connect()
	# with open('/home/airone/ID-DepreSD/scoring-result.txt','w') as outfile:
	# 	outfile.write("uname,depressed,stdscore,stdcount,stdcount0,stdscorecount,stdscorecount0,twtscore,twtcount,twtcount0,"+
	# 		"twtscorecount,twtscorecount0")
	# 	outfile.write('\n')
	query = {}
	projection = {}
	projection["screen_name"] = 1.0
	projection["_id"] = 0.0
	sort = [ (u"screen_name", 1) ]
	cursor = colUser.find(query, projection = projection, sort = sort, no_cursor_timeout=True)
	print(cursor.count())
	try:
		for user in cursor:
			uname = "user"+str(urut)
			user = json.dumps(user["screen_name"])
			loaded_user = json.loads(user)
			print(loaded_user)
			print("User ke-",urut)
			query = {"username":loaded_user}
			projection["username"] = 1.0
			projection["_id"] = 0.0
			sort = [ (u"username", 1) ]
			cursor = colFrequencyStemmed.find(query, projection = projection, sort = sort, no_cursor_timeout=True)
			if cursor.count() == 0:		
				twitterProcStemmed(loaded_user)
				urut = urut + 1
			else:
				print("skip ",loaded_user)
				urut = urut + 1
				continue
			# if urut == 2:
			# 	quit()
	finally:
	    client.close()
	cursor.close()
	print("--- %s seconds ---" % (time.time() - start_time))

def twitterProcStemmed(uname):
	#connect()
	global twtcount
	global prnlist
	global KEY0
	global KEY1
	global KEY2
	query = {"usernameTweet":uname}
	projection = {}
	projection["text"] = 1.0
	projection["date"] = 1.0
	projection["_id"] = 1.0
	sort = [ (u"date", 1) ]
	tweet = 0
	twtcount = 0
	cursor = colTweet.find(query, projection = projection, sort = sort, no_cursor_timeout=True)
	try:
		for doc in cursor:
			tweetID = doc["_id"]
			# print(tweetID)
			# print(doc['text'])
			doc = re.sub(r'https?:\/\/.*[\r\n]*', '', doc['text'])
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
			doc = re.sub('[^A-Za-z.,?!\n ]+', '', doc.lower())
			twtcount+=1
			tweet=tweet+1
			# print("Tweet : "+str(tweet))
			recapinc = 0
			tweetDepreSD = 0
			phrase = 0
			prnlist = {"prn":""}			
			#FORMALIZER GOES HERE
			doc = {"string": doc}
			# print(doc)
			formalized_doc = InaNLP_request("formalizer", doc)
			formalized_doc = json.loads(formalized_doc.text)
			doc = formalized_doc["data"]
			doc = {"string": doc}
			# print(doc)
			#STEMMING GOES HERE
			stemmed_doc = InaNLP_request("stemmer", doc)
			stemmed_doc = json.loads(stemmed_doc.text)
			doc = stemmed_doc["data"]
			doc = {"string": doc}
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
					cursor = colKeywordSeedValidatedStemmed.find({"seed": regex})
					if cursor.count() == 1:
						KEY0=KEY0+1
						# save_frequency(kata)
						# print("  found KEY0: ",kata)
						for doc in cursor:
							# print("correspond: ",doc["correspond"])
							saveFrequencyStemmed(uname,kata,doc["correspond"],level="seed")
					else:
						cursor = colKeywordFirstValidatedStemmed.find({"first": regex})
						if cursor.count() == 1:
							KEY1=KEY1+1
							# print("  found KEY1: ",kata)
							for doc in cursor:
								# print("correspond: ",doc["correspond"])
								saveFrequencyStemmed(uname,kata,doc["correspond"],level="first")
						else:
							cursor = colKeywordSecondValidatedStemmed.find({"second": regex})
							if cursor.count() == 1:
								KEY2=KEY2+1
								# print("  found KEY2: ",kata)
								for doc in cursor:
									# print("correspond: ",doc["correspond"])
									saveFrequencyStemmed(uname,kata,doc["correspond"],level="second")
	finally:
	    client.close()

def saveFrequencyStemmed(uname,kata,correspond,level): #save first-degree synonym from Kateglo
	query = {}
	# query["kata"] = Regex(u".*"+kata+".*", "i")
	query = {"$and":[{"kata": {"$regex" : kata}},{"username": {"$regex" : uname}}]}
	cursor = colFrequencyStemmed.find(query)
	if cursor.count() == 0:
		result = colFrequencyStemmed.insert_one({"username":uname,"kata":kata,"correspond":correspond,"jumlah":1,"level":level})
	else:
		result = colFrequencyStemmed.update_one({"$and":[{"kata": {"$regex" : kata}},{"username": {"$regex" : uname}}]}, {'$inc': {'jumlah': 1}})

def InaNLP_request(endpoint, payload):
	url = "http://localhost:9000/"+endpoint
	headers = {'content-type': 'application/json'}
	r = requests.post(url, data=json.dumps(payload), headers=headers)
	return r

def test_regex():
	loaded_doc = ":( : ( :) : ) :D XD :'( yang aku #hestek RT @AaFelicKs rep ini boleh?  https:// twitter.com/WeGotLoves/sta tus/961978794851557376 aaa"
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

def recap_hour():
	connect()
	global tweetID
	global recap
	global recapinc
	global isrecap

	recap = {0 : 0, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0, 8 : 0, 9 : 0, 10 : 0, 11 : 0, 12 : 0,
			13 : 0, 14 : 0, 15 : 0, 16 : 0, 17 : 0, 18 : 0, 19 : 0, 20 : 0, 21 : 0, 22 : 0, 23 : 0}

	isrecap = True
	cursoruser = colUser.find({"depressed":"true"})
	for user in cursoruser:
		fetch_user(user["screen_name"])
	print(recap)

def prepare_FreqDist(n):
	a=0
	fdist = nltk.FreqDist()
	with open('/home/airone/ID-DepreSD/raw-data.txt','r+') as fin:
		doc = {"string" : fin.read()}
		doc = re.sub(r'https?:\/\/.*[\r\n]*', '', doc["string"])
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

		outfile = open('/home/airone/ID-DepreSD/tokenized-data.txt','r+')
		for sentence in nltk.tokenize.sent_tokenize(doc):
			for word in nltk.tokenize.word_tokenize(sentence):
				fdist[word] += 1
				a=a+1
				json.dump(word, outfile)
		print(fdist)
		print(fdist.most_common(n))
		print(a)

def print_FreqDist(n):
	a=0
	fdist = nltk.FreqDist()
	with open('/home/airone/ID-DepreSD/raw-data.txt','r+') as fin:
		outfile = open('/home/airone/ID-DepreSD/tokenized-data.txt','r+')
		for sentence in nltk.tokenize.sent_tokenize(fin.read()):
			for word in nltk.tokenize.word_tokenize(sentence):
				a=a+1
				fdist[word] += 1
				# json.dump(word, outfile)
		print(fdist)
		print(fdist.most_common(n))
		print(a)

def generate_model(cfdist, word, num=15):
	for i in range(num):
		#print(word),
		#word = cfdist[word].max()
		print(word),
		word = cfdist[word].max()

def print_cfdist_kjv(word):
	text = nltk.corpus.genesis.words('english-kjv.txt')
	bigrams = nltk.bigrams(text)
	cfd = nltk.ConditionalFreqDist(bigrams)
	print(cfd)
	print(cfd[word])
	# cfd.plot()
	generate_model(cfd, word)

def print_cfdist(word):
	with open('/home/airone/ID-DepreSD/raw-data.txt','r+') as text:
		bigrams = nltk.bigrams(text.read().split())
		cfd = nltk.ConditionalFreqDist(bigrams)
		print(cfd)
		print(cfd[word])
		#cfd.tabulate()
		generate_model(cfd, word)