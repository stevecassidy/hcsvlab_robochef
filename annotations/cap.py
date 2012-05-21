from ausnc_ingest.annotations.annotated_text import *
from ausnc_ingest.annotations.annotation import *
from ausnc_ingest.annotations.annotation_parsers import *
from pyparsing import *

class PartialAnnotation():
  """
  >>> PartialAnnotation("a", "type", "val").end(2)
  type: val 0 -> 2
  """
  def __init__(self, endChar, tipe, val):
    self.endChar = endChar
    self.strt = 0
    self.type = tipe
    self.val = val
    
  def start(self, loc):
    ret = PartialAnnotation(self.endChar, self.type, self.val)
    ret.strt = loc
    return ([],[ret])
  
  def end(self, loc):
    return Annotation(self.type, self.val, self.strt, loc)

class OneCharAnnotation(PartialAnnotation):
  def __init__(self, tipe, val):
    self.type = tipe
    self.val = val

  def start(self, loc):
    return ([Annotation(self.type, self.val, loc, loc)],[])

def parse(loc, data, starts, pending):
  if (len(data) == 0):
    return AnnotatedText("", [])
  elif (data[0] in map(lambda x: x.endChar, pending)):
    finished = findOwner(data[0], pending)
    ann = finished.end(loc)
    at = parse(loc, data[1:], starts, removeOwner(data[0],pending))
    at.add_anns([ann])
    return at
  elif (data[0] in starts.keys()):
    pa = starts[data[0]]
    anns, pas = pa.start(loc)
    at =  parse(loc, data[1:], starts, pending + pas)
    at.add_anns(anns)
    return at
  else:
    at = parse(loc+1, data[1:], starts, pending)
    at.prep_text(data[0])
    return at

def findOwner(char, pending):
  for pa in pending:
    if (pa.endChar == char):
      return pa

def removeOwner(char, pending):
  for pa in pending:
    if (pa.endChar == char):
      pending.remove(pa)
      return pending
      
import unittest
import doctest
from ausnc_ingest import utils

def unittests():
  res = doctest.DocTestSuite()
  res.addTest(unittest.makeSuite(UnitTest))
  return res

class UnitTest(unittest.TestCase):
  def testVerySimpleStrings(self):
    self.assertEqual( parse(0, "Hi There", {}, [])
                    , AnnotatedText("Hi There", [])
                    )
    self.assertEqual( parse(0, "Hi There", {"_": PartialAnnotation("_", "emph", "emph")}, [])
                    , AnnotatedText("Hi There", [])
                    )
    self.assertEqual( parse(0, "Hi _There", {"_": PartialAnnotation("_", "emph", "emph")}, [])
                    , AnnotatedText("Hi There", [])
                    )
    self.assertEqual( parse(0, "Hi _There_", {"_": PartialAnnotation("_", "emph", "emph")}, [])
                    , AnnotatedText("Hi There", [Annotation("emph", "emph", 3, 8)])
                    )                                        
    self.assertEqual( parse(0, "Hi _Th_e_re_", {"_": PartialAnnotation("_", "emph", "emph")}, [])
                    , AnnotatedText("Hi There", [Annotation("emph", "emph", 6, 8),Annotation("emph", "emph", 3, 5)])
                    )                                        
  def testTwoAnnotationTypes(self):
    self.assertEqual( parse(0, "Hi There", {"_": PartialAnnotation("_", "emph", "emph"), "^": PartialAnnotation("^", "voice", "high")}, [])
                    , AnnotatedText("Hi There", [])
                    )
    self.assertEqual( parse(0, "Hi There", {"_": PartialAnnotation("_", "emph", "emph"), "^": PartialAnnotation("^", "voice", "high")}, [])
                    , AnnotatedText("Hi There", [])
                    )
    self.assertEqual( parse(0, "Hi _There", {"_": PartialAnnotation("_", "emph", "emph"), "^": PartialAnnotation("^", "voice", "high")}, [])
                    , AnnotatedText("Hi There", [])
                    )
    self.assertEqual( parse(0, "Hi _There_", {"_": PartialAnnotation("_", "emph", "emph"), "^": PartialAnnotation("^", "voice", "high")}, [])
                    , AnnotatedText("Hi There", [Annotation("emph", "emph", 3, 8)])
                    )                                        
    self.assertEqual( parse(0, "Hi _Th_e_re_", {"_": PartialAnnotation("_", "emph", "emph"), "^": PartialAnnotation("^", "voice", "high")}, [])
                    , AnnotatedText("Hi There", [Annotation("emph", "emph", 6, 8),Annotation("emph", "emph", 3, 5)])
                    )                                                            
    self.assertEqual( parse(0, "H^i The^re", {"_": PartialAnnotation("_", "emph", "emph"), "^": PartialAnnotation("^", "voice", "high")}, [])
                    , AnnotatedText("Hi There", [Annotation("voice", "high", 1, 6)])
                    )
    self.assertEqual( parse(0, "H^i^ Th^e^re", {"_": PartialAnnotation("_", "emph", "emph"), "^": PartialAnnotation("^", "voice", "high")}, [])
                    , AnnotatedText("Hi There", [Annotation("voice", "high", 5, 6), Annotation("voice", "high", 1, 2)])
                    )
    self.assertEqual( parse(0, "H^i _The^re", {"_": PartialAnnotation("_", "emph", "emph"), "^": PartialAnnotation("^", "voice", "high")}, [])
                    , AnnotatedText("Hi There", [Annotation("voice", "high", 1, 6)])
                    )
    self.assertEqual( parse(0, "H^i _The^re_", {"_": PartialAnnotation("_", "emph", "emph"), "^": PartialAnnotation("^", "voice", "high")}, [])
                    , AnnotatedText("Hi There", [Annotation("emph", "emph", 3, 8),Annotation("voice", "high", 1, 6)])
                    )                                        
    self.assertEqual( parse(0, "H^i _Th_e_^re_", {"_": PartialAnnotation("_", "emph", "emph"), "^": PartialAnnotation("^", "voice", "high")}, [])
                    , AnnotatedText("Hi There", [Annotation("emph", "emph", 6, 8),Annotation("voice", "high", 1, 6),Annotation("emph", "emph", 3, 5)])
                    )   

  def testOneCharAnnotations(self):
    self.assertEqual( parse(0, "Hi There", {":": OneCharAnnotation("some", "thing"), "^": PartialAnnotation("^", "voice", "high")}, [])
                    , AnnotatedText("Hi There", [])
                    )
    self.assertEqual( parse(0, "Hi There:", {":": OneCharAnnotation("some", "thing"), "^": PartialAnnotation("^", "voice", "high")}, [])
                    , AnnotatedText("Hi There", [Annotation("some", "thing", 8,8)])
                    )
    self.assertEqual( parse(0, "H:i T::here:", {":": OneCharAnnotation("some", "thing"), "^": PartialAnnotation("^", "voice", "high")}, [])
                    , AnnotatedText("Hi There", [Annotation("some", "thing", 8,8),Annotation("some", "thing", 4,4),Annotation("some", "thing", 4,4),Annotation("some", "thing", 1,1)])
                    )
  def testOneCharWithOverlapping(self):
    self.assertEqual( parse(0, "Hi The^re:^", {":": OneCharAnnotation("some", "thing"), "^": PartialAnnotation("^", "voice", "high")}, [])
                    , AnnotatedText("Hi There", [Annotation("voice", "high", 6, 8),Annotation("some", "thing", 8,8)])
                    )
    self.assertEqual( parse(0, "H:i ^T::her^e:", {":": OneCharAnnotation("some", "thing"), "^": PartialAnnotation("^", "voice", "high")}, [])
                    , AnnotatedText("Hi There", [Annotation("some", "thing", 8,8),Annotation("voice", "high", 3, 7),Annotation("some", "thing", 4,4),Annotation("some", "thing", 4,4),Annotation("some", "thing", 1,1)])
                    )
                                                                                                     
