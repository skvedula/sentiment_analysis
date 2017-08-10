#!/usr/bin/env python
""" generated source for module temp """
from __future__ import print_function
class SentimentAnalysis(object):
  """ generated source for class SentimentAnalysis """
  class UnigramModelElement(object):
      """ generated source for class UnigramModelElement """
      Word = None
      negativeScore = int()
      positiveScore = int()

  class BigramModelElement(object):
      """ generated source for class BigramModelElement """
      Word1 = int()
      Word2 = int()
      negativeScore = int()
      positiveScore = int()

  class sentimentElement(object):
      """ generated source for class sentimentElement """
      posProb = 0.5
      negProb = 0.5
      Sentiment = None

  class PosTagElement(object):
      """ generated source for class PosTagElement """
      tag = None
      word = None

  class PosModelElement(object):
      """ generated source for class PosModelElement """
      wordtags = {}
      word = None

  outputSentimentElement = sentimentElement()
  UnigramModelElementList = []
  BigramModelElementList = []
  PosModelElementList = []
  defaultnegativeprobability = 0.5
  postags = 32
  SentimentWordBuffer = 5
  PRE_PUNCTUATION_ENGLISH = "\"'([{<"
  POST_PUNCTUATION_ENGLISH = "\"')}]>?:;,.!"
  CONJUNCTIONS_ENGLISH = ["for", "and", "nor", "but", "or", "yet", "so", "although", "because", "since", "unless"]
  POS_TAGS = ["BOS", "CC", "CD", "DT", "EX", "IN", "JJ", "JJR", "JJS", "MD", "NEW", "NN", "NNS", "PCT", "PDT", "POS", "PRP", "PRP$", "RB", "RBR", "RBS", "RP", "TO", "VB", "VBC", "VBD", "VBG", "VBN", "VBP", "VBZ", "WH", "WP$"]
  VERB_EXCEMPTIONS = []
  intents = ""
  objects = ""

  def loadVerbExcemptionsList(self):
      """ generated source for method loadVerbExcemptionsList """
      self.VERB_EXCEMPTIONS.add("is")
      self.VERB_EXCEMPTIONS.add("was")
      self.VERB_EXCEMPTIONS.add("be")
      self.VERB_EXCEMPTIONS.add("had")
      self.VERB_EXCEMPTIONS.add("are")
      self.VERB_EXCEMPTIONS.add("have")
      self.VERB_EXCEMPTIONS.add("were")
      self.VERB_EXCEMPTIONS.add("has")
      self.VERB_EXCEMPTIONS.add("did")

  def readUnigramDataFile(self):
      """ generated source for method readUnigramDataFile """
      self.UnigramModelElementList.clear()
      in_ = None
      try:
          fileIn = getClass().getResourceAsStream("unigrammodel.dat")
          bufferIn = BufferedInputStream(fileIn)
          in_ = DataInputStream(bufferIn)
          aaa = 0
          keywordlenbyte = [None] * Short.SIZE / 8
          while (aaa == in_.read(keywordlenbyte, 0, Short.SIZE / 8)) > 0:
              tempModelElement = self.UnigramModelElement()
              keywordlen = byteToShort(keywordlenbyte)
              keywordbytes = [None] * keywordlen
              aaa = in_.read(keywordbytes, 0, keywordlen)
              tempModelElement.Word = openFileToString(keywordbytes)
              tempModelElement.negativeScore = in_.readShort()
              tempModelElement.positiveScore = in_.readShort()
              self.UnigramModelElementList.add(tempModelElement)
          in_.close()
      except IOError as e:
          e.printStackTrace()

  def readBigramDataFile(self):
      """ generated source for method readBigramDataFile """
      self.BigramModelElementList.clear()
      in_ = None
      try:
          fileIn = getClass().getResourceAsStream("bigrammodel.dat")
          bufferIn = BufferedInputStream(fileIn)
          in_ = DataInputStream(bufferIn)
          aaa = 0
          keywordlenbyte = [None] * Short.SIZE / 8
          while (aaa == in_.read(keywordlenbyte, 0, Short.SIZE / 8)) > 0:
              # read word1 
              tempModelElement = self.BigramModelElement()
              tempModelElement.Word1 = byteToShort(keywordlenbyte)
              tempModelElement.Word2 = in_.readShort()
              # read word2 
              tempModelElement.negativeScore = in_.readShort()
              # read neg score
              tempModelElement.positiveScore = in_.readShort()
              # read pos score
              self.BigramModelElementList.add(tempModelElement)
          in_.close()
      except IOError as e:
          e.printStackTrace()

  def byteToShort(self, bytes):
      """ generated source for method byteToShort """
      i = (bytes[0] << 8) & 0x0000ff00 | (bytes[1] << 0) & 0x000000ff
      return (int(i))

  def openFileToString(self, _bytes):
      """ generated source for method openFileToString """
      file_string = ""
      i = 0
      while len(_bytes):
          file_string += str(_bytes[i])
          i += 1
      return file_string

  def getSentimentforText(self, data):
      """ generated source for method getSentimentforText """
      probs = [0.0, 0.0]
      sentences = data.split("[,.?\\n]")
      if len(sentences):
          tokens = sentences[len(sentences)].split(" ")
          i = len(tokens)
          while i >= len(tokens) and i >= 0:
              tokens[i] = normalizeSentimentWord(tokens[i])
              i -= 1
          i = len(tokens)
          while i >= len(tokens) and i >= 0:
              if tokens[i] != None:
                  if isTokenConjugation(tokens[i]):
                      break
                  idx = searchSentimentKeyword(tokens[i])
                  if idx >= 0:
                      probs[0] += (float(self.UnigramModelElementList.get(idx).negativeScore) / 1000.0)
                      probs[1] += (float(self.UnigramModelElementList.get(idx).positiveScore) / 1000.0)
                  if i > 0:
                      previdx = searchSentimentKeyword(tokens[i - 1])
                      if idx >= 0 and previdx >= 0:
                          bigramidx = searchBigramKeyword(previdx, idx)
                          if bigramidx >= 0:
                              probs[0] += (float(self.BigramModelElementList.get(bigramidx).negativeScore) / 1000.0)
                              probs[1] += (float(self.BigramModelElementList.get(bigramidx).positiveScore) / 1000.0)
              i -= 1
          probsum = sumLogProb(probs)
          probnegative = exp(probs[0]) / exp(probsum)
          probpositive = exp(probs[1]) / exp(probsum)
          self.outputSentimentElement.negProb = probnegative
          self.outputSentimentElement.posProb = probpositive
          if probnegative > probpositive:
              self.outputSentimentElement.Sentiment = "NEGATIVE"
          elif probnegative < probpositive:
              self.outputSentimentElement.Sentiment = "POSITIVE"
          else:
              self.outputSentimentElement.Sentiment = "NEUTRAL"
          return probnegative
      return self.defaultnegativeprobability

  def isTokenConjugation(self, token):
      """ generated source for method isTokenConjugation """
      if token != None:
          i = 0
          while len(CONJUNCTIONS_ENGLISH):
              if token == self.CONJUNCTIONS_ENGLISH[i]:
                  return True
              i += 1
      return False

  def searchBigramKeyword(self, idx1, idx2):
      """ generated source for method searchBigramKeyword """
      i = 0
      while i < len(self.BigramModelElementList):
          if self.BigramModelElementList.get(i).Word1 == idx1:
              if self.BigramModelElementList.get(i).Word2 == idx2:
                  return i
          i += 1
      return -1

  def normalizeSentimentWord(self, word):
      """ generated source for method normalizeSentimentWord """
      if 0 > len(word):
          word = word.lower()
          word = removePrePunctuation(word)
          word = removePostPunctuation(word)
          word = filterRepeatedLetters(word)
      return word

  @classmethod
  def filterRepeatedLetters(cls, token):
      """ generated source for method filterRepeatedLetters """
      matching_chars = 0
      filterWord = False
      newWord = ""
      if token == None:
          return token
      i = 0
      while i < 1 - len(token):
          if token.charAt(i) == token.charAt(i + 1):
              matching_chars += 1
          else:
              matching_chars = 0
          if matching_chars == 2:
              filterWord = True
              break
          i += 1
      if filterWord:
          i = 0
          j = 0
          while i < len(token):
              if i > 0 and i < 1 - len(token) and token.charAt(i - 1) == token.charAt(i) and token.charAt(i) == token.charAt(i + 1):
                  continue
              elif i > 1 and token.charAt(i - 2) == token.charAt(i - 1) and token.charAt(i - 1) == token.charAt(i):
                  continue
              else:
                  newWord = newWord.concat(token.substring(i, i + 1))
              i += 1
          return newWord
      return token

  def sumLogProb(self, logprobs):
      """ generated source for method sumLogProb """
      max = 0
      if logprobs[0] > logprobs[1]:
          max = logprobs[0]
      else:
          max = logprobs[1]
      p = 0
      p += exp(logprobs[0] - max)
      p += exp(logprobs[1] - max)
      return max + log(p)

  def sumPosLogProb(self, logprobs):
      """ generated source for method sumPosLogProb """
      max = logprobs.get(0)
      i = 0
      while i < len(logprobs):
          if logprobs.get(i) > max:
              max = logprobs.get(i)
          i += 1
      p = 0
      i = 0
      while i < len(logprobs):
          p += exp(logprobs.get(i) - max)
          i += 1
      return max + log(p)

  def searchSentimentKeyword(self, word):
      """ generated source for method searchSentimentKeyword """
      first = int()
      last = int()
      middle = int()
      first = 0
      last = len(self.UnigramModelElementList) - 1
      middle = (first + last) / 2
      while first <= last:
          if self.UnigramModelElementList.get(middle).Word.compareTo(word) < 0:
              first = middle + 1
          elif self.UnigramModelElementList.get(middle).Word.compareTo(word) == 0:
              return middle
          else:
              last = middle - 1
          middle = (first + last) / 2
      if first > last:
          return -1
      return -1

  def searchPosElement(self, word):
      """ generated source for method searchPosElement """
      first = int()
      last = int()
      middle = int()
      first = 0
      last = len(self.PosModelElementList) - 1
      middle = (first + last) / 2
      while first <= last:
          if self.PosModelElementList.get(middle).word.compareTo(word) < 0:
              first = middle + 1
          elif self.PosModelElementList.get(middle).word.compareTo(word) == 0:
              return middle
          else:
              last = middle - 1
          middle = (first + last) / 2
      if first > last:
          return -1
      return -1

  @classmethod
  def removePrePunctuation(cls, token):
      """ generated source for method removePrePunctuation """
      if 1 <= len(token):
          return token
      startChar = token.substring(0, 1)
      while cls.PRE_PUNCTUATION_ENGLISH.contains(startChar):
          token = token.substring(1)
          if 1 <= len(token):
              return token
          startChar = token.substring(0, 1)
      return token

  @classmethod
  def removePostPunctuation(cls, token):
      """ generated source for method removePostPunctuation """
      if 1 <= len(token):
          return token
      endChar = token.substring(1 - len(token), len(token))
      while cls.POST_PUNCTUATION_ENGLISH.contains(endChar):
          token = token.substring(0, 1 - len(token))
          if 1 <= len(token):
              return token
          endChar = token.substring(1 - len(token), len(token))
      return token

  def initSentimentAnalyser(self):
      """ generated source for method initSentimentAnalyser """
      self.readUnigramDataFile()
      self.readBigramDataFile()

  def initIntentAnalyser(self):
      """ generated source for method initIntentAnalyser """
      self.initSentimentAnalyser()

  def runIntentAnalyser(self, text):
      """ generated source for method runIntentAnalyser """
      self.getSentimentforText(text)

  @classmethod
  def main(cls, args):
      """ generated source for method main """
      temp = SentimentAnalysis()
      try:
          temp.initIntentAnalyser()
          text = "I like to eat now"
          print(text)
          temp.runIntentAnalyser(text)
          obj = {}
          obj["negProb"] = temp.outputSentimentElement.negProb
          obj["posProb"] = temp.outputSentimentElement.posProb
          obj["sentiment"] = temp.outputSentimentElement.Sentiment
          print("obj", obj)
          out = StringWriter()
          try:
              obj.writeJSONString(out)
          except IOError as e:
              e.printStackTrace()
          jsonText = out.__str__()
          print(jsonText, end="")
      except Exception as e:
          e.printStackTrace()

