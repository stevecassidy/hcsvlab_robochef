from ausnc_ingest.annotations.annotated_text import *
from ausnc_ingest.annotations.annotation import *
from ausnc_ingest.annotations.annotation_parsers import *
from pyparsing import *

def unknownParser():
  return Literal(u"\xba").setParseAction(lambda s, loc, toks: AnnotatedText("", [annotation.Annotation(u"unknown", u"masculine ordinal indicator", 0, 0)]))
  
def micropauseParser():
  """
  Picks up a micropause in the CA style, ie. "(.)"
  Pauses return a space since a pause it likely to read better in the unannotated text if it is replaced with a space.
  >>> micropauseParser().parseString("(.)")
  ([@( ,[micropause:  0 -> 1])], {})
  
  The whole of the micropause must be present
  >>> micropauseParser().parseString("(.")
  Traceback (most recent call last):
      ...
  ParseException: Expected "(.)" (at char 0), (line:1, col:1)
  """
  return Literal(u"(.)").setParseAction(lambda s, loc, toks: AnnotatedText(" ",[annotation.Annotation(u"micropause", u"", 0, 1)]))

def pauseParser():
  """
  Picks up a pause in the CA style, ie. "(1.2)"
  Pauses return a space since a pause it likely to read better in the unannotated text if it is replaced with a space.
  >>> pauseParser().parseString("(1.2)")
  ([@( ,[pause: 1.2 0 -> 1])], {})
  >>> pauseParser().parseString("(1.0)")
  ([@( ,[pause: 1.0 0 -> 1])], {})
  >>> pauseParser().parseString("(1234.2345)")
  ([@( ,[pause: 1234.2345 0 -> 1])], {})
  
  Must include decimal point
  >>> pauseParser().parseString("(4)")
  Traceback (most recent call last):
      ...
  ParseException: Expected "." (at char 2), (line:1, col:3)
  """
  return (Suppress(u"(") + Word(nums) + Suppress(u".") + Word(nums) + Suppress(u")")).setParseAction(lambda s, loc, toks: AnnotatedText(" ",[annotation.Annotation(u"pause", toks[0] + "." + toks[1], 0, 1)]))

def elongationParser():
  """
  >>> elongationParser().parseString(":")
  ([@(,[elongation:  0 -> 0])], {})
  """
  return (Literal(u":").setParseAction(lambda s, loc, toks: AnnotatedText("", [annotation.Annotation(u"elongation", "", 0, 0)])))

def uncertaintyParser():
  """
  Blank space in parenthesis indicates uncertainty about the transcription.  Uncertainly can include an intonation on the end.
  
  >>> uncertaintyParser().parseString("( )")
  ([@( ,[uncertain:   0 -> 1])], {})
  >>> uncertaintyParser().parseString("(      )")
  ([@(      ,[uncertain:        0 -> 6])], {})
  >>> uncertaintyParser().parseString("(      ,)")
  ([@(      ,[uncertain:        0 -> 6, intonation: continuing 6 -> 6])], {})
  >>> uncertaintyParser().parseString("(      ?)")
  ([@(      ,[uncertain:        0 -> 6, intonation: rising 6 -> 6])], {})
  """
  return (Suppress(u"(") + Word(" ") + Optional(intonationParser(),AnnotatedText("",[])) + Suppress(u")")).leaveWhitespace().setParseAction(lambda s, loc, toks: (AnnotatedText(toks[0], [annotation.Annotation(u"uncertain", toks[0], 0, len(toks[0]))]))+toks[1])

def intonationParser():
  u"""
  ? = rising intonation
  \xc2 = falling then rising intonation
  , = continuing intonation
  . = falling or final intonation 
  \x2193 = sharp falling 
  
  >>> intonationParser().parseString(u"?")
  ([@(,[intonation: rising 0 -> 0])], {})
  >>> intonationParser().parseString(u"\xbf")
  ([@(,[intonation: rising-falling 0 -> 0])], {})
  >>> intonationParser().parseString(u",")
  ([@(,[intonation: continuing 0 -> 0])], {})
  >>> intonationParser().parseString(u".")
  ([@(,[intonation: falling 0 -> 0])], {})
  """
  return ( Literal(u"?").setParseAction(lambda s, loc, toks: AnnotatedText("", [annotation.Annotation("intonation", "rising", 0,0)])) \
         ^ Literal(u"\xbf").setParseAction(lambda s, loc, toks: AnnotatedText("", [annotation.Annotation("intonation", "rising-falling", 0,0)])) \
         ^ Literal(u",").setParseAction(lambda s, loc, toks: AnnotatedText("", [annotation.Annotation("intonation", "continuing", 0,0)])) \
         ^ Literal(u".").setParseAction(lambda s, loc, toks: AnnotatedText("", [annotation.Annotation("intonation", "falling", 0,0)])) \
         ^ Literal(unichr(8595)).setParseAction(lambda s, loc, toks: AnnotatedText("", [annotation.Annotation("intonation", "sharp-falling", 0,0)])) \
         ^ Literal(unichr(8593)).setParseAction(lambda s, loc, toks: AnnotatedText("", [annotation.Annotation("intonation", "sharp-falling", 0,0)])) \
         )

def dubiousOrNonsenseParser(inner):
  """
  (text) represents either dubious designation (if text is a word) or nonsense syllables
  
  >>> dubiousOrNonsenseParser(slurpParser(")")).parseString("(what)")         
  ([@(what,[dubious-nonsense: what 0 -> 4])], {})
  """
  return (Suppress(u"(") + inner + Suppress(")")).setParseAction(lambda s, loc, toks: toks[0].add_anns_chain([annotation.Annotation("dubious-nonsense", toks[0].text, 0, len(toks[0].text))]))

def softParser(inner):
  """
  unichr(9702) and \u00B0 delimited text indicates markedly soft speach
  
  >>> softParser(slurpParser(unichr(9702)+u"\u00B0")).parseString(unichr(9702)+u"what"+unichr(9702))
  ([@(what,[volume: soft 0 -> 4])], {})

  >>> softParser(slurpParser(u"()\u00B0"+unichr(9702)) ^ dubiousOrNonsenseParser(slurpParser(u"()\u00B0"+unichr(9702)))).parseString(unichr(9702)+u"(what)"+unichr(9702))
  ([@(what,[dubious-nonsense: what 0 -> 4, volume: soft 0 -> 4])], {})

  >>> softParser(slurpParser(unichr(9702)+u"\u00B0")).parseString(u"\u00B0what\u00B0")
  ([@(what,[volume: soft 0 -> 4])], {})

  >>> softParser(slurpParser(u"()\u00B0"+unichr(9702)) ^ dubiousOrNonsenseParser(slurpParser(u"()\u00B0"+unichr(9702)))).parseString(u"\u00B0(what)"+unichr(9702))
  ([@(what,[dubious-nonsense: what 0 -> 4, volume: soft 0 -> 4])], {})
  """
  return ((Suppress(unichr(9702)) ^ Suppress(u"\u00B0")) + inner + (Suppress(unichr(9702)) ^ Suppress(u"\u00B0"))).setParseAction(lambda s, loc, toks: toks[0].add_anns_chain([annotation.Annotation("volume", "soft", 0, len(toks[0].text))]))

def speedParser(innerParser):
  """
  >>> speedParser(slurpParser(">")).parseString("<abc>")
  ([@(abc,[speed: slow 0 -> 3])], {})
  >>> speedParser(slurpParser("<")).parseString(">abc<")
  ([@(abc,[speed: compressed 0 -> 3])], {})

  It is best to exclude all start and end tags in the inner parser
  >>> speedParser(slurpParser("<>")).parseString(">abc<")
  ([@(abc,[speed: compressed 0 -> 3])], {})
  
  Inner parser works recusrively
  >>> speedParser(speedParser(slurpParser("<>"))).parseString(">>abc<<")
  ([@(abc,[speed: compressed 0 -> 3, speed: compressed 0 -> 3])], {})
  >>> speedParser(speedParser(slurpParser("<>"))).parseString("<>abc<>")
  ([@(abc,[speed: compressed 0 -> 3, speed: slow 0 -> 3])], {})
  
  Speed can also be annotated with a single open <.  In this case it represents a hurried start or hurried end to a word.
  Note that there must always be enough after the open < for the inner parse to tackle, even if there is no closing >
  >>> speedParser(slurpParser("<>")).parseString("<what")
  ([@(what,[speed: left push 0 -> 0])], {})
  >>> speedParser(slurpParser("<>")).parseString("< ")
  ([@( ,[speed: left push 0 -> 0])], {})
  >>> speedParser(Empty().setParseAction(lambda s, loc, toks: AnnotatedText("",[]))).parseString("<")
  ([@(,[speed: left push 0 -> 0])], {})
  
  Note that a left-push token within a slow compressed section of speech will confuse the parser, but that would confuse the human too
  I think.  I.e. even if it is possible to determine taht the mark after "there" is a left-push, it is not reasonable to expect the parser
  to work this out.
  >>> speedParser(slurpParser("<>")).parseString(">hi there< chap<")
  ([@(hi there,[speed: compressed 0 -> 8])], {})
  """
  def checkLast(s, loc, toks):
    if (len(toks) > 1): # I must have picked up the literal >
      return toks[0].add_anns_chain([annotation.Annotation("speed", "slow",       0, len(toks[0].text))])
    else:
      return toks[0].add_anns_chain([annotation.Annotation("speed", "left push", 0, 0)])
  return ( (Suppress(u">") + innerParser + Suppress("<")).setParseAction(lambda s, loc, toks: toks[0].add_anns_chain([annotation.Annotation("speed", "compressed", 0, len(toks[0].text))])) \
         ^ (Suppress(u"<") + innerParser + (StringEnd() | Literal(">"))).setParseAction(checkLast) \
         )

def latchedParser():
  return Literal(u"=").leaveWhitespace().setParseAction(lambda s, loc, toks: AnnotatedText("", [annotation.Annotation("latched-utterance", "", 0,0)]))

import unittest
import doctest
from ausnc_ingest import utils

def unittests():
  res = doctest.DocTestSuite()
  res.addTest(unittest.makeSuite(UnitTest))
  return res

class UnitTest(unittest.TestCase):
  def testEmpty(self):
    self.assertTrue
