from pyparsing import *

from hcsvlab_robochef.annotations import annotation

class AnnotatedText:
  def __init__(self, text, anns):
    self.text = text
    self.anns  = anns

  def __repr__(self):
    return ('@(' + self.text + ',' + str(self.anns) + ')')

  def __cmp__(self, other):
    if (cmp(self.text, other.text) == 0):
      return cmp(self.anns, other.anns)
    else:
      return cmp(self.text, other.text)

  def __add__(self, other):
    txt = self.text + other.text
    ans = other.anns
    for a in ans:
      a.forward(len(self.text))
    ans = self.anns + ans
    return AnnotatedText(txt,ans)
  
  def plus_str(self,st,extend):
    old_len = len(self.text)
    self.text = self.text + st
    for a in self.anns:
      if ((a.end == old_len) & extend):
        a.end = a.end + len(st)
    return self

  def on_annotations(self,f):
    self.anns = map(f, self.anns)

  def add_anns(self, anns):
    self.anns = self.anns + anns
    
  def prep_text(self, txt):
    self.text = txt + self.text

  def add_anns_chain(self, anns):
    self.add_anns(anns)
    return self

def concat(list_of_ats, sep="", extend=False):
  """
  Concatenate a list of {{AnnotatedText}}'s.  {{spaces}} tells you if you need spaces added at the join
  and if so, {{extend}} tells you whether annotations that reach the end of the annotated text should be
  extended to include the space.
  """
  return reduce(lambda x, y: x.plus_str(sep,extend) + y, list_of_ats)

import unittest

class UnitTest(unittest.TestCase):
  def testPlusOperator(self):
    self.assertEqual((AnnotatedText('hi', [annotation.Annotation('a','ho',1,1)]) + AnnotatedText(' there', [annotation.Annotation('a','  ',0,0)])) \
                    , AnnotatedText('hi there', [annotation.Annotation('a','ho',1,1), annotation.Annotation('a','  ',2,2)])                       \
                    )
    self.assertEqual((AnnotatedText('hi', [annotation.Annotation('a','ho',1,1)]) + AnnotatedText(' there', [annotation.Annotation('a','ch',0,0)]) + AnnotatedText(' old chap', [annotation.Annotation('a','  ',4,4)])) \
                    , AnnotatedText('hi there old chap', [annotation.Annotation('a','ho',1,1), annotation.Annotation('a','ch',2,2), annotation.Annotation('a','  ',12,12)])                       \
                    )

  def testConcatFunction(self):
    self.assertEqual(concat([AnnotatedText('hi', [annotation.Annotation('a','ho',1,1)]), AnnotatedText(' there', [annotation.Annotation('a','ch',0,0)])]) \
                    , AnnotatedText('hi there', [annotation.Annotation('a','ho',1,1), annotation.Annotation('a','ch',2,2)])                       \
                    )
    self.assertEqual(concat([AnnotatedText('hi', [annotation.Annotation('a','ho',1,1)]), AnnotatedText(' there', [annotation.Annotation('a','  ',0,0)]), AnnotatedText(' old chap', [annotation.Annotation('a','ch',4,4)])]) \
                    , AnnotatedText('hi there old chap', [annotation.Annotation('a','ho',1,1), annotation.Annotation('a','  ',2,2), annotation.Annotation('a','ch',12,12)])                       \
                    )

def unittests():
  return unittest.makeSuite(UnitTest)
