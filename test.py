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
			word =removePrePunctuation(word)
			word =removePostPunctuation(word)
			word = filterRepeatedLetters(word)
		return word

	def removePrePunctuation(token):
		if(len(token) <= 1):
			return token
		startChar = token[0:1]
		while(startChar in PRE_PUNCTUATION_ENGLISH):
			token = token[1:]
			if(len(token) <= 1):
				return token
			startChar = token[0:1]
		return token

	def removePostPunctuation(token):
		if(len(token) <= 1):
			return token
		endChar = token[len(token) - 1:len(token)]
		while(endChar in POST_PUNCTUATION_ENGLISH):
			token = token[0:len(token) - 1]
			if(len(token) <= 1):
				return token
			endChar = token[len(token) - 1:len(token)]
		return token

	def filterRepeatedLetters(token):
		matching_chars=0
		filterWord = False
		newWord = ""
		if(token==null):
			return token
		for idx, char in enumerate(list(token)):
			if(char[idx] == char[idx+1]):
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

	def isTokenConjugation(token):
		if(token!=null):
			for conjunction in CONJUNCTIONS_ENGLISH:
				if(token == conjunction):
					return True
		return False

	def searchSentimentKeyword(word):
		first = 0
		last = UnigramModelElementList.size()-1;
		middle = (first + last)/2;
		while(first <= last):
			if(UnigramModelElementList.get(middle).Word.compareTo(word)<0):
				first = middle + 1
			elif(UnigramModelElementList.get(middle).Word.compareTo(word) == 0):
				return middle
			else:
				last = middle - 1
			middle = (first + last)/2
			if(first > last):
				return -1
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
				for token in tokens[len(tokens):SentimentWordBuffer-1:-1]:
					token = normalizeSentimentWord(token)
				for token in tokens[len(tokens):SentimentWordBuffer-1:-1]:
					if(tokens[i]!=null):
						if(isTokenConjugation(tokens[i])):
							break
						idx = searchSentimentKeyword(tokens[i])
						print "idx : ", idx
						if(idx>=0):
							probs[0] += UnigramModelElementList[idx]["negativeScore"]/1000.0
							probs[1] += UnigramModelElementList[idx]["positiveScore"]/1000.0
						if(i>0):
							previdx = searchSentimentKeyword(tokens[i-1])
							print "previdx : ", idx
							if(idx>=0 and previdx>=0):
								bigramidx = searchBigramKeyword(previdx,idx)
								print "bigramidx : ", idx
								if(bigramidx>=0):
									probs[0]+= BigramModelElementList[bigramidx]["negativeScore"]/1000.0
									probs[1]+= BigramModelElementList[bigramidx]["positiveScore"]/1000.0
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
	
result = {}
temp = SentimentAnalysis(sys.argv[1])
temp.initIntentAnalyser();
result = temp.runIntentAnalyzer()
print result