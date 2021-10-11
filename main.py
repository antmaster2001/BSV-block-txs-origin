import requests
import time
from itertools import zip_longest
from tqdm import tqdm
import pymongo

# inits
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["BSV_BlockTags"]
BSV_BlockTags = mydb["BSV_BlockTags"]
big_stats = mydb["big_stats"]
knownOrigins = {}
knownBig_stats = big_stats.find_one()

print("Give the block height of the block you want to check:")
blockHeight = int(input())

def convertSeconds(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
      
    return "%d:%02d:%02d" % (hour, minutes, seconds)

def addToDict(key):
	if(key in knownOrigins):
		knownOrigins[key] = knownOrigins[key] + 1
	else:
		knownOrigins[key] = 1

def group_elements(n, iterable, padvalue='x'):
    return zip_longest(*[iter(iterable)]*n, fillvalue=padvalue)

def getBlockPage(blockHash, pageId):
	return requests.get("https://api.whatsonchain.com/v1/bsv/main//block/hash/" + str(blockHash) + "/page/" + str(pageId)).json()

def getTxData(txHash):
	return requests.get("https://api.whatsonchain.com/v1/bsv/main/tx/hash/" + str(txHash)).json()

def bigStatsBlockHandler(blockData):
	print("knownBig_stats")
	print(knownBig_stats)
	if (knownBig_stats["mostTXblock"]["amount"] < blockData["txcount"]):
		big_stats.update_one({"_id": knownBig_stats["_id"]}, {"$set":{"mostTXblock":{
		"amount": blockData["txcount"],
		"blockID": blockData["height"]
	}}})
	if (knownBig_stats["largestBlock"]["amount"] < blockData["size"]):
		big_stats.update_one({"_id": knownBig_stats["_id"]}, {"$set":{"largestBlock":{
		"amount": blockData["size"],
		"blockID": blockData["height"]
	}}})

def txHandler(txHash):
	allTransactionsData = requests.post("https://api.whatsonchain.com/v1/bsv/main/txs", json={"txids": txHash}).json()
	for x in allTransactionsData:
		if(x["vout"][0]["scriptPubKey"]["opReturn"] != None):
			addToDict(x["vout"][0]["scriptPubKey"]["opReturn"]["type"])
		else: 
			addToDict("None")

def InitBlockCheck(blockData):
	allTransactionsHashes = []
	if(blockData["txcount"] < 1000 ): 
		allTransactionsHashes = blockData["tx"]
	else:
		allTransactionsHashes = blockData["tx"]
		allTransactionsHashes.extend(getBlockPage(blockData["hash"], 1))

	print("Found transactions: " + str(len(allTransactionsHashes)))
	print("Estimated time: " + str(convertSeconds(len(allTransactionsHashes) / 20 / 2.5)))
	lastFrameTime = time.time()
	for x in tqdm(group_elements(20, allTransactionsHashes)):
		# A delta time sleep time out for the 3 queries per second WhatsOnChain rate limit
		dt = time.time() - lastFrameTime
		if(dt < 0.34):
			# print("Sleep time: " + str(0.34 - dt))
			time.sleep(0.34 - dt)
		currentTime = time.time()
		lastFrameTime = currentTime
		txHandler(x)

	bigStatsBlockHandler(blockData)
	print(knownOrigins)

	totalFound = 0
	knownPercentages = 0
	for key, value in knownOrigins.items():
		totalFound += value
		knownPercentages += value / len(allTransactionsHashes)
		print(str(key) + ": " + "{:.2f}".format(value / len(allTransactionsHashes) * 100) + "%")

	print("totalFound: "+ str(totalFound) + " total tx found: " + str(len(allTransactionsHashes)))
	print("knownPercentages" + str(knownPercentages))

if(requests.get("https://api.whatsonchain.com/v1/bsv/main/chain/info").json()["blocks"] >= blockHeight):
	print("Block Found :) \n \n")
	InitBlockCheck(requests.get("https://api.whatsonchain.com/v1/bsv/main/block/height/" + str(blockHeight)).json())
else:
	print("Block doesn't exist")

