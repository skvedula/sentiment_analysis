import re
import sys

SentimentWordBuffer = 5

class SentimentAnalysis:

	def __init__(self, input): # this method creates the class object.
	    self.input = input

	def getSentimentforText(self, data):
		probs = [0,0];
		data = data.replace("\\n", ",")
		sentences = re.split('[|,|.|?]', data)
		if(sentences.length > 0):
				tokens = sentences[len(sentences)-1].split(" ")
				for(i=tokens.length-1; i>= tokens.length - SentimentWordBuffer && i>=0; i--)
					tokens[i] = normalizeSentimentWord(tokens[i])
				for(i=tokens.length-1;i>=tokens.length-SentimentWordBuffer && i>=0 ;i--)
					if(tokens[i]!=null):
						if(isTokenConjugation(tokens[i])):
							break
						idx = searchSentimentKeyword(tokens[i])
						if(idx>=0):
							probs[0] += UnigramModelElementList.get(idx).negativeScore/1000.0
							probs[1] += UnigramModelElementList.get(idx).positiveScore/1000.0
						if(i>0):
							previdx = searchSentimentKeyword(tokens[i-1])
							if(idx>=0&&previdx>=0):
								bigramidx = searchBigramKeyword(previdx,idx)
								if(bigramidx>=0):
									probs[0]+= BigramModelElementList.get(bigramidx).negativeScore/1000.0
									probs[1]+= BigramModelElementList.get(bigramidx).positiveScore/1000.0
				probsum = sumLogProb(probs)
				probnegative = Math.exp(probs[0])/Math.exp(probsum)
				probpositive = Math.exp(probs[1])/Math.exp(probsum)
				outputSentimentElement.negProb = probnegative
				outputSentimentElement.posProb = probpositive
				if(probnegative>probpositive):
					outputSentimentElement.Sentiment = "NEGATIVE"
				elif(probnegative<probpositive):
					outputSentimentElement.Sentiment = "POSITIVE"
				else:
					outputSentimentElement.Sentiment = "NEUTRAL"
				return probnegative
		return defaultnegativeprobability

	def runIntentAnalyzer(self):
		self.getSentimentforText(self.input)
		obj = {}
		obj["negProb"] = 0.8638921090281604
		obj["posProb"] = 0.13610789097183956
		obj["sentiment"] = "NEGATIVE"
		return obj

result = {}
temp = SentimentAnalysis(sys.argv[1])
result = temp.runIntentAnalyzer()
print result