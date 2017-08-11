import re
import sys
import math

SentimentWordBuffer = 5
PRE_PUNCTUATION_ENGLISH ="\"'([{<"
POST_PUNCTUATION_ENGLISH ="\"')}]>?:;,.!"
CONJUNCTIONS_ENGLISH = ["for",  "and",  "nor", "but", "or", "yet", "so","although", "because", "since", "unless"]

class SentimentAnalysis:
	
	class UnigramModelElement:
		Word = None
		negativeScore = int()
		positiveScore = int()

	class BigramModelElement:
		Word1 = int()
		Word2 = int()
		negativeScore = int()
		positiveScore = int()

	class sentimentElement:
		posProb = 0.5
		negProb = 0.5
		Sentiment = None

	class PosTagElement:
		tag = None
		word = None

	class PosModelElement:
		wordtags = {}
		word = None

	def __init__(self, input):
		self.input = input

	def normalizeSentimentWord(self, word):
		if(len(word)>0):
			word= word.lower()
			word = self.removePrePunctuation(word)
			word = self.removePostPunctuation(word)
			word = self.filterRepeatedLetters(word)
		return word

	def removePrePunctuation(self, token):
		if(len(token) <= 1):
			return token
		startChar = token[0:1]
		while(startChar in PRE_PUNCTUATION_ENGLISH):
			token = token[1:]
			if(len(token) <= 1):
				return token
			startChar = token[0:1]
		return token

	def removePostPunctuation(self, token):
		if(len(token) <= 1):
			return token
		endChar = token[len(token) - 1:len(token)]
		while(endChar in POST_PUNCTUATION_ENGLISH):
			token = token[0:len(token) - 1]
			if(len(token) <= 1):
				return token
			endChar = token[len(token) - 1:len(token)]
		return token

	def filterRepeatedLetters(self, token):
		matching_chars=0
		filterWord = False
		newWord = ""
		if(token==None):
			return token
		for idx, char in enumerate(token[:-1]):
			if(token[idx] == token[idx+1]):
				matching_chars = matching_chars + 1
			else:
				matching_chars=0
			if(matching_chars==2):
				filterWord = True
				break
		if(filterWord):
			for idx, char in enumerate(list(token)):
				if(i>0 and i<len(token)-1 and char[idx-1]==char[idx] and char[idx]==char[idx+1]):
					continue
				elif(i>1 and char[idx-2] == char[idx-1] and char[idx-1] == char[idx]):
					continue
				else:
					newWord = newWord + token[i:i+1]
			return newWord
		return token

	def sumLogProb(self, logprobs):
	  max = 0
	  if(logprobs[0] > logprobs[1]):
		  max = logprobs[0]
	  else:
		  max = logprobs[1]
	  p = 0
	  p += math.exp(logprobs[0]-max)
	  p += math.exp(logprobs[1]-max)
	  return max + math.log(p)

	def sumPosLogProb(self, logprobs):
	  max = logprobs[0]
	  for i  in logprobs:
		  if(logprobs[i] > max):
			  max = logprobs[i]
	  p = 0
	  for i in logprobs:
		  p += math.exp(logprobs[i]-max)
	  return max + math.log(p)

	def isTokenConjugation(self, token):
		if(token != None):
			for conjunction in CONJUNCTIONS_ENGLISH:
				if(token == conjunction):
					return True
		return False

	def searchSentimentKeyword(self, word):
		first = 0
		last = len(UnigramModelElementList)-1
		middle = (first + last)/2;
		while(first <= last):
			if(UnigramModelElementList[middle]["Word"] < word):
				first = middle + 1
			elif(UnigramModelElementList[middle]["Word"] == word):
				return middle
			else:
				last = middle - 1
			middle = (first + last)/2
			if(first > last):
				return -1
		return -1

	def searchBigramKeyword(self, idx1, idx2):
		for i, elem in enumerate(BigramModelElementList):
			if(elem["Word1"] == idx1):
				if(elem["Word2"] == idx2):
					return i
		return -1

	def readUnigramDataFile(self):
		del UnigramModelElementList[:]
		with open('unigramModelFilterd.txt', 'r') as f:
			rows = f.read().splitlines()
		for row in rows:
			parts = row.split(" ")
			tempModelElement = {}
			tempModelElement["Word"] = parts[0]
			tempModelElement["negativeScore"] = parts[1]
			tempModelElement["positiveScore"] = parts[2]
			UnigramModelElementList.append(tempModelElement)

	def readBigramDataFile(self):
		del BigramModelElementList[:]
		with open('bigramModelFilterd.txt', 'r') as f:
			rows = f.read().splitlines()
		for row in rows:
			parts = row.split(" ")
			tempModelElement = {}
			tempModelElement["Word1"] = parts[0]
			tempModelElement["negativeScore"] = parts[1]
			tempModelElement["Word2"] = parts[2]
			tempModelElement["positiveScore"] = parts[3]
			BigramModelElementList.append(tempModelElement)

	def getSentimentforText(self, data):
		probs = [0,0];
		data = data.replace("\\n", ",")
		sentences = re.split('[|,|.|?]', data)
		if(len(sentences) > 0):
			tokens = sentences[len(sentences)-1].split(" ")
			for token in reversed(list(tokens[-SentimentWordBuffer:])):
				token = self.normalizeSentimentWord(token)
			trimmed_sentence = list(tokens[-SentimentWordBuffer:])
			for i, token in reversed(list(enumerate(trimmed_sentence))):
				if(token != None):
					if(self.isTokenConjugation(token)):
						break
					idx = self.searchSentimentKeyword(token)
					if(idx>=0):
						probs[0] += int(UnigramModelElementList[idx]["negativeScore"])/1000.0
						probs[1] += int(UnigramModelElementList[idx]["positiveScore"])/1000.0
					if(i>0):
						previdx = self.searchSentimentKeyword(list(reversed(tokens[-SentimentWordBuffer:]))[i-1])
						if(idx>=0 and previdx>=0):
							bigramidx = self.searchBigramKeyword(previdx,idx)
							if(bigramidx>=0):
								probs[0]+= int(BigramModelElementList[bigramidx]["negativeScore"])/1000.0
								probs[1]+= int(BigramModelElementList[bigramidx]["positiveScore"])/1000.0
			probsum = self.sumLogProb(probs)
			probnegative = math.exp(probs[0])/math.exp(probsum)
			probpositive = math.exp(probs[1])/math.exp(probsum)
			outputSentimentElement["negProb"] = probnegative
			outputSentimentElement["posProb"] = probpositive
			if(probnegative > probpositive):
				outputSentimentElement["Sentiment"] = "NEGATIVE"
			elif(probnegative<probpositive):
				outputSentimentElement["Sentiment"] = "POSITIVE"
			else:
				outputSentimentElement["Sentiment"] = "NEUTRAL"
			return probnegative
		return defaultnegativeprobability

	def initSentimentAnalyser(self):
		self.readUnigramDataFile()
		self.readBigramDataFile()

	def initIntentAnalyser(self):
		self.initSentimentAnalyser()

	def runIntentAnalyzer(self):
		self.getSentimentforText(self.input)
		return outputSentimentElement

UnigramModelElementList = []
BigramModelElementList = []
outputSentimentElement = {}
defaultnegativeprobability =  0.5
	
result = {}
temp = SentimentAnalysis(sys.argv[1])
temp.initIntentAnalyser();
result = temp.runIntentAnalyzer()
print result