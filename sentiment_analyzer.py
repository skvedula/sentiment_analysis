import re
import sys

SentimentWordBuffer = 5
PRE_PUNCTUATION_ENGLISH ="\"'([{<"
POST_PUNCTUATION_ENGLISH ="\"')}]>?:;,.!"
CONJUNCTIONS_ENGLISH = ["for",  "and",  "nor", "but", "or", "yet", "so","although", "because", "since", "unless"]

class SentimentAnalysis:

	def __init__(self, input): # this method creates the class object.
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
		filterWord = false
		newWord = ""
		if(token==null):
			return token
		for idx, char in enumerate(list(token)):
			if(char[idx] == char[idx+1]):
				matching_chars = matching_chars + 1
			elif:
				matching_chars=0
			if(matching_chars==2):
				filterWord = true
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

	def isTokenConjugation(token):
		if(token!=null):
			for conjunction in CONJUNCTIONS_ENGLISH
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

###############################################

	def readUnigramDataFile():
		del UnigramModelElementList[:]
		DataInputStream in
		try:
			with open('unigrammodel.dat', 'r') as fileIn:
				bufferIn = BufferedInputStream(fileIn)
				in = DataInputStream(bufferIn)
			aaa = 0
			byte[] keywordlenbyte = new byte[Short.SIZE/8]
			while((aaa = in.read(keywordlenbyte,0,Short.SIZE/8))>0):
				tempModelElement = UnigramModelElement()
				short keywordlen = byteToShort(keywordlenbyte)
				byte[] keywordbytes = new byte[keywordlen]
				aaa = in.read(keywordbytes, 0, keywordlen)
				tempModelElement.Word = openFileToString(keywordbytes)
				tempModelElement.negativeScore = in.readShort()
				tempModelElement.positiveScore = in.readShort()
				UnigramModelElementList.add(tempModelElement)
			in.close(); 
		except IOError as e:
			e.printStackTrace()

#########################################

	public void readBigramDataFile() 
	{
		BigramModelElementList.clear();
		DataInputStream in;
		try {
			InputStream fileIn = getClass().getResourceAsStream("bigrammodel.dat");
			BufferedInputStream bufferIn = new BufferedInputStream(fileIn);
			in = new DataInputStream(bufferIn);			
			int aaa = 0;
			byte[] keywordlenbyte = new byte[Short.SIZE/8];
			while ((aaa = in.read(keywordlenbyte,0,Short.SIZE/8))>0) //read word1 
			{
				BigramModelElement tempModelElement = new BigramModelElement();
				tempModelElement.Word1 = byteToShort(keywordlenbyte);;
				tempModelElement.Word2 = in.readShort();//read word2 
				tempModelElement.negativeScore = in.readShort();//read neg score
				tempModelElement.positiveScore = in.readShort();//read pos score
				BigramModelElementList.add(tempModelElement);
			}
			in.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	private short byteToShort(byte[] bytes)
	{
		int i=	(bytes[0]<< 8)&0x0000ff00|
			       (bytes[1]<< 0)&0x000000ff;
		return ((short)i);
		
	}

	private String openFileToString(byte[] _bytes)
	{
	    String file_string = "";

	    for(int i = 0; i < _bytes.length; i++)
	    {
	        file_string += (char)_bytes[i];
	    }
	    return file_string;    
	}

#########################################

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
		# 		probsum = sumLogProb(probs)
		# 		probnegative = Math.exp(probs[0])/Math.exp(probsum)
		# 		probpositive = Math.exp(probs[1])/Math.exp(probsum)
		# 		outputSentimentElement.negProb = probnegative
		# 		outputSentimentElement.posProb = probpositive
		# 		if(probnegative>probpositive):
		# 			outputSentimentElement.Sentiment = "NEGATIVE"
		# 		elif(probnegative<probpositive):
		# 			outputSentimentElement.Sentiment = "POSITIVE"
		# 		else:
		# 			outputSentimentElement.Sentiment = "NEUTRAL"
		# 		return probnegative
		# return defaultnegativeprobability

	def initSentimentAnalyser():
		readUnigramDataFile()
		readBigramDataFile()

	def initIntentAnalyser(self):
		initSentimentAnalyser()

	def runIntentAnalyzer(self):
		self.getSentimentforText(self.input)
		obj = {}
		obj["negProb"] = 0.8638921090281604
		obj["posProb"] = 0.13610789097183956
		obj["sentiment"] = "NEGATIVE"
		return obj

result = {}
temp = SentimentAnalysis(sys.argv[1])
temp.initIntentAnalyser();
result = temp.runIntentAnalyzer()
print result