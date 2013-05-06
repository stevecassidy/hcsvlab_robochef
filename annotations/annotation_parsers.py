from hcsvlab_robochef.annotations.annotated_text import *
from hcsvlab_robochef.annotations.annotation import *
from pyparsing import *

def slurpParser(exclusions):
  """
  Slurps up characters until it hits one of the exclusions
  >>> slurpParser("a").parseString("ccca")
  ([@(ccc,[])], {})
  
  If there are no exclusion characters, it just keeps going until the end of the string
  >>> slurpParser("a").parseString("bbbbddddeeee")
  ([@(bbbbddddeeee,[])], {})
  
  It will happily slurp up whitespace as well
  >>> slurpParser("*").parseString("I am a more likely example string, where *some text is bold*.")
  ([@(I am a more likely example string, where ,[])], {})
  """
  return CharsNotIn(exclusions).setParseAction(lambda s, loc, toks: AnnotatedText(toks[0],[]))
  
def exactParser(this):
  """
  Parses exactly this string and nothing else
  >>> exactParser("<").parseString("<")
  ([@(<,[])], {})
  >>> exactParser("<").parseString("abc")
  Traceback (most recent call last):
      ...
  ParseException: Expected "<" (at char 0), (line:1, col:1)
  """
  return Literal(this).setParseAction(lambda s, loc, toks: AnnotatedText(toks[0],[]))

def redactParser():
  return (Literal("[IDENTIFYING MATERIAL REMOVED]") | Literal("IDENTIFYING MATERIAL REMOVED")).setParseAction(lambda s, loc, toks: AnnotatedText("REDACTED",[annotation.Annotation("redacted", toks[0], 0, 8)]))
  
def aceCorrectionParser():
  """
  In the ace corpus, a correction is annotated with a * and then the correction string up to a whitespace.
  This parser will work from the * to the whitespace, returning the corrected text.

  >>> aceCorrectionParser().parseString("*abc def")
  ([@(,[correction: abc 0 -> 0])], {})
  
  There must be a * at the front of the string
  >>> aceCorrectionParser().parseString("abc def")
  Traceback (most recent call last):
      ...
  ParseException: Expected "*" (at char 0), (line:1, col:1)

  TODO: decide if there are any other characters that should terminate a correction, punctuation perhaps?
  """
  return Suppress(u"*")                   \
      + (CharsNotIn(u" ,").setParseAction(lambda s, loc, toks: AnnotatedText('', [annotation.Annotation("correction",toks[0], 0, 0)])))

def markupParser(st, a, attr=None):
  """
  Parses the pseudo-html heading annotation from the ace corpus and full xml-ish tags from other corpora
  
  st is the tag we are looking for, a is the type to give the annotation and attr is the attribute of the tag to quiz for the annotation value.
  
  >>> markupParser('h', 'heading').parseString("<h>some stuff</h>")
  ([@(some stuff,[heading:  0 -> 10])], {})
  >>> markupParser('h', 'heading').parseString("<h one='two'>some stuff</h>")
  ([@(some stuff,[heading:  0 -> 10])], {})
  >>> markupParser('h', 'heading', 'one').parseString("<h one='two'>some stuff</h>")
  ([@(some stuff,[heading: 'two' 0 -> 10])], {})
  >>> markupParser('h', 'heading', 'two').parseString("<h one='two' two='one'>some stuff</h>")
  ([@(some stuff,[heading: 'one' 0 -> 10])], {})
  >>> markupParser('h', 'heading', 'two').parseString("<h one='two' two=one>some stuff</h>")
  ([@(some stuff,[heading: one 0 -> 10])], {})
  """
  def attrParser(res):
    return (CharsNotIn("<>=") + Suppress("=") + CharsNotIn("<> ")).setParseAction(lambda s, loc, toks: res.update({toks[0].strip():toks[1]}))
 
  attrs={}
  
  def parseAction(s, loc, toks): 
    if attr:
      # 17/01/2012 SP: Added a dictionary check to make sure key lookup errors do not occur
      if attr in attrs and attrs[attr]:
        at = attrs[attr]
      else:
        at = ""
    else:
      at = ""
    return AnnotatedText(toks[0], [annotation.Annotation(a, at, 0, len(toks[0]))])
    
  return (Suppress(u"<"+st) + Suppress(ZeroOrMore(attrParser(attrs))) + Suppress(u">") + SkipTo(u"</"+st+u">") + Suppress(u"</"+st+u">")).setParseAction(parseAction)

def everythingParser():
  """
  An annotation parser which accepts whatever you give it and gives back the annotated text of the input with no annotations.
  This parser is useful as an inner parser when you don't want inner parsing to do anything.

  >>> everythingParser().parseString("something")
  ([@(something,[])], {})
  >>> everythingParser().parseString("this, that and every other thing")
  ([@(this, that and every other thing,[])], {})
  """
  return CharsNotIn(u"").setParseAction(lambda s, loc, toks: AnnotatedText(toks[0], []))

def oneOrMoreParsers(inner):
  """
  Replicates {{OneOrMore}} from {{pyparsing}} but saves us cluttering up our code with the {{setParseAction}} everytime
  """
  return OneOrMore(inner).setParseAction(lambda s, loc, toks: concat(toks))

def zeroOrMoreParsers(inner):
    """
    Replicates {{ZeroOrMore}} from {{pyparsing}} but saves us cluttering up our code with the {{setParseAction}} everytime
    """
    return ZeroOrMore(inner).setParseAction(lambda s, loc, toks: concat(toks))

def speakerParser(innerParser):
  """
  Parses the speaker turn annotations used in the monash and griffith corpora.  Note that this annotation almost certainly contains other annotations
  within it since the speaker annotation is "around" the whole speech, which contains overlaps, etc.  Hence this parser accepts another
  parser which will parse the resulting text and the speaker annotation bounds will match the text _after_ the other annotations are 
  found.

  Speaker annotations are either all capitals and number, or "all" or "?"

  Speaker turns are separated by a linebreak in the output, but that linebreak is not contained in either annotation.  This happens
  regardless of whether or not there was a linebreak between the speaker turns in the original text.

  You can use an {{everythingParser}} as the inner parser to have only the speaker annotation detected
  >>> speakerParser(everythingParser()).parseString("MR: we have a problem hereSC: I don't believe you, just fix it")
  ([@(we have a problem here
  I don't believe you, just fix it,[speaker: MR 0 -> 22, speaker: SC 23 -> 55])], {})

  We can achieve monash speaker with monash overlap thus
  >>> speakerParser(oneOrMoreParsers(slurpParser('[') ^ monashOverlapParser())).parseString("MR: we have a problem [here]SC: [I don't] believe you, just fix it")
  ([@(we have a problem here
  I don't believe you, just fix it,[overlap: overlap 18 -> 22, speaker: MR 0 -> 22, overlap: overlap 23 -> 30, speaker: SC 23 -> 55])], {})

  This parser accepts a number of different speaker forms
  >>> speakerParser(everythingParser()).parseString("MR: we have a problem here all: We don't believe you, just fix it")
  ([@(we have a problem here
  We don't believe you, just fix it,[speaker: MR 0 -> 22, speaker: all 23 -> 56])], {})
  >>> speakerParser(everythingParser()).parseString("MR: we have a problem here?: I don't believe you, just fix it")
  ([@(we have a problem here
  I don't believe you, just fix it,[speaker: MR 0 -> 22, speaker: ? 23 -> 55])], {})
  """
  def parseInner(data, speaker):
    at = innerParser.parseString(data)[0]
    at.add_anns([annotation.Annotation('speaker', '', 0, len(at.text), properties={'speakerid': speaker})])
    return at

  speakerToken = (Word(u"ABCDEFGHIJKLMNOPQRSTUVWXYZ"+nums) ^ Literal("all") ^ Literal("?")) + Suppress(u": ")
  speakerTurn = (speakerToken + ZeroOrMore(Suppress(u" ")) + SkipTo((speakerToken ^ StringEnd()), False) \
                ).setParseAction(lambda s, loc, toks: parseInner(toks[1], toks[0]))
  return OneOrMore(speakerTurn).setParseAction(lambda s, loc, toks: concat(toks, sep="\n", extend=False))

def knownSpeakerParser(speakers, innerParser):
  """
  A version of the speaker parser which we can use when the speaker labels are known

  >>> knownSpeakerParser(["MR", "MS"], everythingParser()).parseString("MR: we have a problem here MS: We don't believe you, just fix it")
  ([@(we have a problem here
  We don't believe you, just fix it,[speaker: MR 0 -> 22, speaker: MS 23 -> 56])], {})

  We can achieve monash speaker with monash overlap thus
  >>> knownSpeakerParser(["MR", "SC"], oneOrMoreParsers(slurpParser('[') ^ monashOverlapParser())).parseString("MR: we have a problem [here]SC: [I don't] believe you, just fix it")
  ([@(we have a problem here
  I don't believe you, just fix it,[overlap: overlap 18 -> 22, speaker: MR 0 -> 22, overlap: overlap 23 -> 30, speaker: SC 23 -> 55])], {})

  >>> knownSpeakerParser(["MR", "A"], everythingParser()).parseString("MR: we have a problem here?: I don't believe you, just fix it")
  ([@(we have a problem here?: I don't believe you, just fix it,[speaker: MR 0 -> 57])], {})

  """
  def parseInner(data, speaker):
    at = innerParser.parseString(data)[0]
    at.add_anns([annotation.Annotation('speaker', speaker, 0, len(at.text))])
    return at

  speakerToken = Or([Literal(s) for s in speakers]) + Suppress(u":")
  speakerTurn = (speakerToken + ZeroOrMore(Suppress(u" ")) + SkipTo((speakerToken ^ StringEnd()), False) \
                ).setParseAction(lambda s, loc, toks: parseInner(toks[1], toks[0]))
  return OneOrMore(speakerTurn).setParseAction(lambda s, loc, toks: concat(toks, sep = "\n", extend= False))

def monashOverlapParser():
  return (Suppress(u'[') + CharsNotIn(u"]") + Suppress(u']')).setParseAction(lambda s, loc, toks: AnnotatedText(toks[0], [annotation.Annotation('overlap', 'overlap', 0, len(toks[0]))]))

def monashLaughterParser():
  """
  >>> monashLaughterParser().parseString("@")
  ([@(,[laughter: laughter 0 -> 0])], {})
  """
  return (Suppress(u"@")).setParseAction(lambda s, loc, toks: AnnotatedText("", [annotation.Annotation('laughter', 'laughter', 0, 0)]))

def cooeeParagraphParser():
  """
  Parses out these things which are page numbers in cooee
  >>> cooeeParagraphParser().parseString("[1] two")
  ([@(,[pageno: 1 0 -> 0])], {})

  # we also see dots, which might mean elided text but can't find a reference
  >>> cooeeParagraphParser().parseString("[...] two")
  ([@(,[pageno: ... 0 -> 0])], {})
    
  Only works when page ids are numbers
  >>> cooeeParagraphParser().parseString("[one] two")
  Traceback (most recent call last):
      ...
  ParseException: Expected W:(0123...) (at char 1), (line:1, col:2)
  """
  return (Suppress(u'[') + Word(u"0123456789.") + Suppress(u"]")).setParseAction(lambda s, loc, toks: AnnotatedText('', [annotation.Annotation('pageno', toks[0], 0, 0)]))

import unittest
import doctest
from hcsvlab_robochef import utils

if __name__ == "__main__":
  doctext.testmod()

def unittests():
  res = doctest.DocTestSuite()
  res.addTest(unittest.makeSuite(UnitTest))
  return res

class UnitTest(unittest.TestCase):
  
  def testSlurpParser(self):
    
    self.assertEqual(utils.parseResultsCmp(slurpParser("a").parseString("bbbb"), slurpParser("c").parseString("bbbb")) \
                    , 0                                                                                                \
                    )

  def testSlurpOnEmptyText(self):
    """
    This test should fail. The parse is on an empty string. The match expression is irrelevant
    """
    self.assertRaises(ParseException, slurpParser("a").parseString, "")

  def testSlurpWithAceCorrection(self):
    self.assertEqual(utils.parseResultsCmp((slurpParser("*") + aceCorrectionParser()).parseString('hi thre*there we are') \
                                          , ParseResults([AnnotatedText('hi thre', []), AnnotatedText('', [Annotation('correction','there',0,0)])]) \
                                          ) \
                    , 0 \
                    )
                    
  def testExactWithMarkupParser(self):
    self.assertEqual(utils.parseResultsCmp((markupParser('a', 'anchor') ^ exactParser("<")).parseString("<a>what</a>") \
                                          , ParseResults([AnnotatedText('what',[Annotation('anchor', '', 0,4)])]) \
                                          ) \
                    , 0 \
                    )
    self.assertEqual(utils.parseResultsCmp((markupParser('a', 'anchor') ^ exactParser("<")).parseString("< what") \
                                          , ParseResults([AnnotatedText('<',[])]) \
                                          ) \
                    , 0 \
                    )
                    
  def testExactOnEmptyText(self):
    """
    This test should fail. The parse is on an empty string. The match expression is irrelevant
    """
    self.assertRaises(ParseException, exactParser("a").parseString, "")  
      
  def testExactOnMismatchingText(self):
    """
    This test should fail. The parse is on mis-matching strings using the exact parser
    """
    self.assertRaises(ParseException, exactParser("a").parseString, "b")
    
  def testAceCorrectionWithIllegalFirstCharacter(self):
    """
    This test should fail. The parse is on text with content preceeding the * marker which should raise
    a ParseException
    """
    self.assertRaises(ParseException, aceCorrectionParser().parseString, "abc*cba")
    
  def testMarkupParserWithMismatchingTagsOnCase(self):
    """
    This test should fail. The parse is on text surrounded with tag with mis-matching casing.
    """
    self.assertRaises(ParseException, markupParser("h", "heading").parseString, "<h>Some Test</H>")
    
  def testMarkupParserWithMissingAttribute(self):
    """
    This test makes sure that misspelled attributes do not result in unhandled exceptions
    """
    self.assertEqual(utils.parseResultsCmp(markupParser('h', 'heading', 'two').parseString("<h one='two' wo='one'>some stuff</h>") \
                                          , ParseResults(([AnnotatedText('some stuff',[annotation.Annotation('heading','',0,10)])])) \
                                          )
                                          , 0 \
                    )
                    
  def testEverythingParserWithNothingToParse(self):
    """
    The everythingParser should fail if it is handed nothing to parse
    """
    self.assertRaises(ParseException, everythingParser().parseString, "")
