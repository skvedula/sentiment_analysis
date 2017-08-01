import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.HashMap;

import org.json.simple.JSONObject;
		
public class SentimentAnalysis {
	private class UnigramModelElement{
		String Word;
		short negativeScore;
		short positiveScore;
	}
	private class BigramModelElement{
		short Word1;
		short Word2;
		short negativeScore;
		int positiveScore;
	}
	public class sentimentElement{
		public double posProb=0.5;
		public double negProb=0.5;
		public String Sentiment=null;
	}
	public class PosTagElement{
		public String tag=null;
		public String word=null; 
	}
	public class PosModelElement{
		HashMap<Integer, Integer> wordtags = new HashMap<Integer, Integer>();
		public String word=null;
	}
	public sentimentElement outputSentimentElement =  new sentimentElement() ;
	private ArrayList<UnigramModelElement> UnigramModelElementList =  new ArrayList<UnigramModelElement>();
	private ArrayList<BigramModelElement> BigramModelElementList =  new ArrayList<BigramModelElement>();
	private ArrayList<PosModelElement> PosModelElementList =  new ArrayList<PosModelElement>();
	private double defaultnegativeprobability =  0.5;
	int postags = 32;
	int SentimentWordBuffer =5;
	public static final String PRE_PUNCTUATION_ENGLISH ="\"'([{<";
	public static final String POST_PUNCTUATION_ENGLISH ="\"')}]>?:;,.!";
	public static final String[] CONJUNCTIONS_ENGLISH ={"for",  "and",  "nor", "but", "or", "yet", 
														"so","although", "because", "since", "unless"};
	public static final String[] POS_TAGS ={"BOS","CC","CD","DT","EX","IN","JJ","JJR","JJS","MD","NEW",
											"NN","NNS","PCT","PDT","POS","PRP","PRP$","RB","RBR","RBS",
											"RP","TO","VB","VBC","VBD","VBG","VBN","VBP","VBZ","WH","WP$"};
	private ArrayList<String> VERB_EXCEMPTIONS =new ArrayList<String>();
	public String intents = "";
	public String objects = "";
	public void loadVerbExcemptionsList()
	{
		VERB_EXCEMPTIONS.add("is");
		VERB_EXCEMPTIONS.add("was");
		VERB_EXCEMPTIONS.add("be");
		VERB_EXCEMPTIONS.add("had");
		VERB_EXCEMPTIONS.add("are");
		VERB_EXCEMPTIONS.add("have");
		VERB_EXCEMPTIONS.add("were");
		VERB_EXCEMPTIONS.add("has");
		VERB_EXCEMPTIONS.add("did");
	}
	public void readUnigramDataFile() 
	{
		UnigramModelElementList.clear();
		DataInputStream in;
		try {
			InputStream fileIn = getClass().getResourceAsStream("unigrammodel.dat");
			BufferedInputStream bufferIn = new BufferedInputStream(fileIn);
			in = new DataInputStream(bufferIn);			
			int aaa = 0;
			byte[] keywordlenbyte = new byte[Short.SIZE/8];
			while ((aaa = in.read(keywordlenbyte,0,Short.SIZE/8))>0) 
			{
				UnigramModelElement tempModelElement = new UnigramModelElement();
				short keywordlen = byteToShort(keywordlenbyte);
				byte[] keywordbytes = new byte[keywordlen];
				aaa = in.read(keywordbytes, 0, keywordlen);
				tempModelElement.Word = openFileToString(keywordbytes);
				tempModelElement.negativeScore = in.readShort();
				tempModelElement.positiveScore = in.readShort();
				UnigramModelElementList.add(tempModelElement);
			}
			in.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
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
	public double getSentimentforText(String data)
	{
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
				
	}
	public boolean isTokenConjugation(String token)
	{
		if(token!=null)
		{
			for(int i=0;i<CONJUNCTIONS_ENGLISH.length;i++)
			{
				if(token.equals(CONJUNCTIONS_ENGLISH[i]))
				{
					return true;
				}
			}
		}
		return false;
	}
	public int searchBigramKeyword(int idx1, int idx2)
	{
		for(int i=0;i<BigramModelElementList.size();i++)
		{
			if(BigramModelElementList.get(i).Word1==idx1)
			{
				if(BigramModelElementList.get(i).Word2==idx2)
				{
					return i;
				}
			}
		}		
		return -1;
	}
	private String normalizeSentimentWord(String word)
	{
		if(word.length()>0)
		{
			word= word.toLowerCase(); 
			word =removePrePunctuation(word);
			word =removePostPunctuation(word);
			word = filterRepeatedLetters(word);
		}
		return word;
	}
	public static String filterRepeatedLetters( String token)
	{
		int matching_chars=0;
		boolean filterWord = false;
		String newWord = "";
		if(token==null)
		{
			return token;
		}
		for(int i=0;i<token.length()-1;i++)
		{
			if(token.charAt(i)==token.charAt(i+1))
			{
				matching_chars++;
			}
			else
			{
				matching_chars=0;
			}
			if(matching_chars==2)
			{
				filterWord =true;
				break;
			}
		}
		if(filterWord)
		{
			for(int i=0,j=0;i<token.length();i++)
			{
				if(i>0 && i<token.length()-1
						&& token.charAt(i-1)==token.charAt(i)
						&& token.charAt(i)==token.charAt(i+1))
				{
				}
				else if(i>1 
						&& token.charAt(i-2)==token.charAt(i-1)
						&& token.charAt(i-1)==token.charAt(i))
				{
				
				}
				else
				{
					newWord =  newWord.concat(token.substring(i,i+1));
				}
			}
			return newWord;
		}
		return token;
	}
	double sumLogProb(double logprobs[])
	{
	  double max = 0;
	  if(logprobs[0]>logprobs[1])
	  {
		  max = logprobs[0];
	  }
	  else
	  {
		  max = logprobs[1];
	  }
	  double p = 0;
	  p += Math.exp(logprobs[0]-max);
	  p += Math.exp(logprobs[1]-max);
	  return max + Math.log(p);
	}
	double sumPosLogProb(ArrayList<Integer> logprobs)
	{
	  double max = logprobs.get(0);
	  for(int i=0;i<logprobs.size();i++)
	  {
		  if(logprobs.get(i)>max)
		  {
			  max = logprobs.get(i);
		  }
	  }
	  double p = 0;
	  for(int i=0;i<logprobs.size();i++)
	  {
		  p += Math.exp(logprobs.get(i)-max);
	  }
	  
	  return max + Math.log(p);
	}
	public int searchSentimentKeyword(String word)
	{
		 int  first, last, middle;
	    first  = 0;
	    last   =UnigramModelElementList.size()-1;
	    middle = (first + last)/2;
	 
	    while( first <= last )
	    {	   
	      if ( UnigramModelElementList.get(middle).Word.compareTo(word)<0)
	      {
	    	  first = middle + 1;  
	      }
	      else if ( UnigramModelElementList.get(middle).Word.compareTo(word)==0 ) 
	      {
	    	  return middle;
	      }
	      else
	      {
	    	  last = middle - 1;  
	      }
	      middle = (first + last)/2;
	   }
	   if ( first > last )
	   {
		   return -1;
	   }
	   return -1;
	}
	public int searchPosElement(String word)
	{
		 int  first, last, middle;
	    first  = 0;
	    last   =PosModelElementList.size()-1;
	    middle = (first + last)/2;
	 
	    while( first <= last )
	    {	   
	      if ( PosModelElementList.get(middle).word.compareTo(word)<0)
	      {
	    	  first = middle + 1;  
	      }
	      else if ( PosModelElementList.get(middle).word.compareTo(word)==0 ) 
	      {
	    	  return middle;
	      }
	      else
	      {
	    	  last = middle - 1;  
	      }
	      middle = (first + last)/2;
	   }
	   if ( first > last )
	   {
		   return -1;
	   }
	   return -1;
	}
	public static String removePrePunctuation( String token)
	{	
		if(token.length() <= 1)
		{
			return token;
		}
		String startChar = token.substring(0,1);
		while(PRE_PUNCTUATION_ENGLISH.contains(startChar))
		{
			token = token.substring(1);
			if(token.length() <= 1)
			{
				return token;
			}
			startChar = token.substring(0,1);
		}
		return token;
	}
	public static String removePostPunctuation( String token)
	{
		if(token.length() <= 1)
		{
			return token;
		}
		String endChar = token.substring(token.length() - 1,token.length());
		while(POST_PUNCTUATION_ENGLISH.contains(endChar))
		{
			token = token.substring(0,token.length() - 1);
			if(token.length()  <= 1) {
				return token;
			}
			endChar = token.substring(token.length() - 1,token.length());
			
		}
		return token;
	}
	public void initSentimentAnalyser()
	{
		readUnigramDataFile();
		readBigramDataFile();
	}
	public void initIntentAnalyser()
	{
		initSentimentAnalyser();
	}
	public void runIntentAnalyser(String text)
	{
		getSentimentforText(text);	
	}
/*	public void TexttoBin( )
	{
		ArrayList<UnigramModelElement> Unigrams =  new ArrayList<UnigramModelElement>();
		ArrayList<String> Unigramwords =  new ArrayList<String>();
		// Open unigram file
		FileInputStream fstream;
		try {
			fstream = new FileInputStream("unigramModelFilterd.txt");
			BufferedReader br = new BufferedReader(new InputStreamReader(fstream));
			String strLine;
			//Read File Line By Line
			while ((strLine = br.readLine()) != null)   {
				String words[]= strLine.split(" ");
				
				if(!Unigramwords.contains(words[0]))
				{
					UnigramModelElement tempUnigramModelElement = new UnigramModelElement();
					tempUnigramModelElement.Word = words[0];
					tempUnigramModelElement.negativeScore = Short.parseShort(words[1]);
					tempUnigramModelElement.positiveScore = Short.parseShort(words[2]);
					Unigrams.add(tempUnigramModelElement);
					Unigramwords.add(words[0]);
				}
				else
				{
					int idx = Unigramwords.indexOf(words[0]);
					UnigramModelElement tempUnigramModelElement = Unigrams.get(idx);
					if(tempUnigramModelElement.negativeScore < Short.parseShort(words[1]))
					{
						tempUnigramModelElement.negativeScore = Short.parseShort(words[1]);
					}
					if(tempUnigramModelElement.positiveScore < Short.parseShort(words[2]))
					{
						tempUnigramModelElement.positiveScore = Short.parseShort(words[2]);
					}
					Unigrams.set(idx,tempUnigramModelElement);
				}			
				
			}
			//Close the input stream
			br.close();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
		FileOutputStream fos;
		DataOutputStream dos;
		try {
			 fos = new FileOutputStream("unigrammodel.dat");
	         // create data output stream
	         dos = new DataOutputStream(fos);
			for(int i=0;i<Unigrams.size();i++)
			{
				byte[] data=Unigrams.get(i).Word.getBytes("UTF-8");
				dos.writeShort(Unigrams.get(i).Word.length());
				dos.write( data);
				dos.writeShort(Unigrams.get(i).negativeScore);
				dos.writeShort(Unigrams.get(i).positiveScore);
				//System.out.println(Unigrams.get(i).Word+" "+Unigrams.get(i).negativeScore+" "+Unigrams.get(i).positiveScore);
			}
			fos.close();
			dos.close();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		FileInputStream fstream2;
		FileOutputStream fos2;
		DataOutputStream dos2;
		try {
			fstream2 = new FileInputStream("bigramModelFilterd.txt");
			 fos2 = new FileOutputStream("bigrammodel.dat");
	         // create data output stream
	         dos2 = new DataOutputStream(fos2);
			BufferedReader br2 = new BufferedReader(new InputStreamReader(fstream2));
			String strLine2;
			//Read File Line By Line
			int j=0;
			while ((strLine2 = br2.readLine()) != null)   {
				j++;
				if(j%1000==0)
				{
					//System.out.println("procesiing "+j);
				}
				String words2[]= strLine2.split(" ");
				int idx1=-1;
				int idx2=-1;
				for(int i1=0;i1<Unigrams.size();i1++)
				{
					if(words2[0].equals(Unigrams.get(i1).Word))
					{
						idx1=i1;
						break;
					}
				}
				for(int i2=0;i2<Unigrams.size();i2++)
				{
					if(words2[2].equals(Unigrams.get(i2).Word))
					{
						idx2=i2;
						break;
					}
				}
				if(idx1>=0 && idx2>=0)
				{
					dos2.writeShort(idx1);
					dos2.writeShort(idx2);
					dos2.writeShort(Short.parseShort(words2[4]));
					dos2.writeShort(Short.parseShort(words2[5]));
					System.out.println(words2[0] +" "+idx1+" "+words2[2] +" "+idx2+
							" "+Short.parseShort(words2[4])+" "+Short.parseShort(words2[5]));
				}
				else
				{
					System.out.println("invalid "+strLine2);
				}
			}
			//Close the input stream
			fos2.close();
			dos2.close();
			br2.close();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	
	}*/
	
	public static void  main(String[] args)
	{
		SentimentAnalysis temp = new SentimentAnalysis();
		try {
			temp.initIntentAnalyser();
//			String text = args[0];
			String text = "I like to eat now";
			temp.runIntentAnalyser(text);
			JSONObject obj = new JSONObject();
			obj.put("negProb", temp.outputSentimentElement.negProb);
			obj.put("posProb", temp.outputSentimentElement.posProb);
			obj.put("sentiment", temp.outputSentimentElement.Sentiment);
			//temp.TexttoBin();
	        StringWriter out = new StringWriter();
	        try {
				obj.writeJSONString(out);
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}	        
	        String jsonText = out.toString();
	        System.out.print(jsonText);			

		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
