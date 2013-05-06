from hcsvlab_robochef.utils import program
from hcsvlab_robochef.utils import tests
import parsing
import ausnctest

getCorporaArgs  = program.getCorporaArgs
listFiles       = program.listFiles

parseResultsCmp      = parsing.parseResultsCmp
replaceEntitiesInStr = parsing.replaceEntitiesInStr
putLTBack            = parsing.putLTBack
tableParser          = parsing.tableParser
merge_dictionaries   = parsing.merge_dictionaries

AusNCTest = ausnctest.AusNCTest

import unittest
import doctest

class UnitTest(unittest.TestCase):
  def testCorporaArgs(self):
    self.assertEqual(getCorporaArgs(["main"]), ["cooee", "ace", "ice", "monash", "griffith", "md", "auslit", "braided"])

  standardMetaDataTop = \
    """
    |CODE:           |BH1M.A          |INTERVIEWER     |                |
    |                |                |(if relevant):  |                |
    |STUDENT'S       |JF              |SCHOOL:         |BH              |
    |INITIALS:       |                |                |                |
    |AGE:            |15              |SEX:            |M               |
    |TRANSCRIBER:    |SE              |BIRTHPLACE:     |Born in         |
    |                |                |                |Australia?      |
    |                |                |                |(Presumably, but|
    |                |                |                |the question was|
    |                |                |                |not actually    |
    |                |                |                |asked)          |
    """
  
  standardMetaDataBottom = \
    """
    |Mother's Ethnicity:               |British or German                 |
    |Father's Ethnicity:               |British or German                 |
    |Maternal Grandmother's Ethnicity: |(Mentions a grandmother who died  |
    |                                  |in Australia, but also others who |
    |                                  |are living in England and         |
    |                                  |Scotland)                         |
    |Maternal Grandfather's Ethnicity: |                                  |
    |Paternal Grandmother's Ethnicity: |                                  |
    |Paternal Grandfather's Ethnicity: |                                  |
    |Language(s) Spoken at home:       |English                           |
    """

  def testTableParser(self):
    self.assertEqual( tableParser(4).parseString(self.standardMetaDataTop).asList()[0] \
        , {"CODE:":'BH1M.A', "INTERVIEWER (if relevant):":'', "STUDENT'S INITIALS:":'JF', "SCHOOL:":'BH', "AGE:":'15', "SEX:":'M', "TRANSCRIBER:":'SE', "BIRTHPLACE:":'Born in Australia? (Presumably, but the question was not actually asked)'}
                    )
    self.maxDiff = None
    self.assertEqual( tableParser(2).parseString(self.standardMetaDataBottom).asList()[0] \
                    , {"Mother's Ethnicity:":'British or German',"Father's Ethnicity:":'British or German', "Maternal Grandmother's Ethnicity:":'(Mentions a grandmother who died in Australia, but also others who are living in England and Scotland)', "Maternal Grandfather's Ethnicity:":'', "Paternal Grandmother's Ethnicity:":'',"Paternal Grandfather's Ethnicity:":'', "Language(s) Spoken at home:":'English'}
                    )


def unittests():
  res = doctest.DocTestSuite(parsing)
  res.addTest(doctest.DocTestSuite(program))
  res.addTest(unittest.makeSuite(UnitTest))
  res.addTest(tests.unittests())
  return res
