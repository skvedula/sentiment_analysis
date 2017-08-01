import sys

class SentimentAnalysis:
	def __init__(self, input): # this method creates the class object.
	    self.input = input

	def getSentimentforText(data):

		double probs[]={0.0,0.0};
		String sentences[] = data.split("[,.?\\n]");
		if(sentences.length>0)
		{
			String tokens[] = sentences[sentences.length-1].split(" ");
			for(int i=tokens.length-1;i>=tokens.length-SentimentWordBuffer && i>=0 ;i--)
			{
				tokens[i] = normalizeSentimentWord(tokens[i]);
			}
			for(int i=tokens.length-1;i>=tokens.length-SentimentWordBuffer && i>=0 ;i--)
			{
				if(tokens[i]!=null)
				{
					if(isTokenConjugation(tokens[i]))
					{
						break;
					}
					int idx = searchSentimentKeyword(tokens[i]);
					if(idx>=0)
					{
						probs[0]+= ((double)UnigramModelElementList.get(idx).negativeScore/1000.0);
						probs[1]+= ((double)UnigramModelElementList.get(idx).positiveScore/1000.0);	
					}
					if(i>0)
					{
						int previdx = searchSentimentKeyword(tokens[i-1]);
						if(idx>=0&&previdx>=0)
						{
							
							int bigramidx = searchBigramKeyword(previdx,idx);
							//System.out.println(tokens[i-1]+" "+ tokens[i]);
							//System.out.println(previdx+" "+ idx+" "+bigramidx);
							if(bigramidx>=0)
							{
								probs[0]+= ((double)BigramModelElementList.get(bigramidx).negativeScore/1000.0);
								probs[1]+= ((double)BigramModelElementList.get(bigramidx).positiveScore/1000.0);	
							}
						}
					}
				}
			}
			double probsum = sumLogProb(probs);
			double probnegative = Math.exp(probs[0])/Math.exp(probsum);
			double probpositive = Math.exp(probs[1])/Math.exp(probsum);
			outputSentimentElement.negProb = probnegative;
			outputSentimentElement.posProb = probpositive;
			if(probnegative>probpositive)
			{
				outputSentimentElement.Sentiment = "NEGATIVE";
			}
			else if(probnegative<probpositive)
			{
				outputSentimentElement.Sentiment = "POSITIVE";
			}
			else 
			{
				outputSentimentElement.Sentiment = "NEUTRAL";
			}
			return probnegative;
		}
		return defaultnegativeprobability;

	def runIntentAnalyzer(self):
		getSentimentforText(self.text)
		obj = {}
		obj["negProb"] = 0.8638921090281604
		obj["posProb"] = 0.13610789097183956
		obj["sentiment"] = "NEGATIVE"
		return obj

result = {}
temp = SentimentAnalysis(sys.argv[1])
result = temp.runIntentAnalyzer()
print result