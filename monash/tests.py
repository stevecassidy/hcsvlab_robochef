import rdflib
import unittest

from ausnc_ingest.monash.ingest import *
from ausnc_ingest.rdf.map import FOAF, DBPEDIA, BIO, SCHEMA, Namespace, DC, Literal
from ausnc_ingest.utils import AusNCTest


# Define namespaces
from ausnc_ingest.rdf.namespaces import *

MONASHNS = Namespace(u"http://ns.ausnc.org.au/schemas/monash/")
MONASHCORPUS = Namespace(u"http://ns.ausnc.org.au/corpora/monash/")

def unittests():
  res = unittest.makeSuite(UnitTest)
  return res
  
class UnitTest(AusNCTest):
    
  def one_of(self, metadata, i, ty, val):
    sofar = 0
    found = metadata.triples((i, ty, None))
    for triple in found:
      self.assertEqual(triple[2], val, "found %s in triple, expecting %s" % (triple[2], val))
      sofar = sofar + 1
 
    self.assertEqual(sofar,1, "found %d triples matching (%s, %s, None), expected 1" % (sofar, i, ty))


  def testMEBH1M1(self):
      filename = "../input/Monash Corpus of Australian English/Transcripts-sanitised/MEBH1M1_Sanitised.doc"
      
      ingest = MonashIngest()
      (sampleid, raw, text, metadata, anns) = ingest.ingestDocument(filename)
      
      #__serialise(self, srcdir, outdir, source_file, basename, name, rawtext, body, meta, annotations):
      (meta_graph, ann_graph) = ingest._MonashIngest__serialise('../input/Monash Corpus of Australian English/Transcripts-sanitised/', \
                                                                '/tmp', filename, sampleid, 'MEBH1M1_Sanitised.doc', raw, text, metadata, anns)
      
      itemuri = MONASHCORPUS[u"items/MEBH1M1_Sanitised"]

      # test some select metadata
      self.one_of(meta_graph, itemuri, AUSNC.TRANSCRIBER, Literal(u'SE'))
      self.one_of(meta_graph, itemuri, AUSNC.MothersEthnicity, Literal(u'British or German'))
      self.one_of(meta_graph, itemuri, AUSNC.FathersEthnicity, Literal(u'British or German'))
      self.one_of(meta_graph, itemuri, AUSNC.MaternalGrandmothersEthnicity, Literal(u'(Mentions a grandmother who died in Australia, but also others who are living in England and Scotland)'))
      self.one_of(meta_graph, itemuri, AUSNC.LanguagesSpokenathome, Literal(u'English'))  
      self.one_of(meta_graph, itemuri, AUSNC.notes, Literal(u'Doesn\u2019t know where his parents were born - says that one was born in\nGermany and one in England, or maybe both in England. Mentions grandparents\nin England and Scotland'))

      # test that the annotations come through the way we want
      first_part = u"Now, REDACTED. Could you tell me your name\n         please.\nMy name\u2019s REDACTED. I\u2019m -\nOkay"
      self.assertEqual(text[:90], first_part)
      # speaker turns
      self.annotation_present(ann_graph, u"speaker", MONASHNS.val, u"RF3", u"0", u"59")
      self.annotation_present(ann_graph, u"speaker", MONASHNS.val, u"BH1M", u"60", u"85")
      self.annotation_present(ann_graph, u"speaker", MONASHNS.val, u"RF3", u"86", u"90")
      # redacted
      self.annotation_present(ann_graph, u"redacted", MONASHNS.val, u"[IDENTIFYING MATERIAL REMOVED]", u"5", u"13")
      self.annotation_present(ann_graph, u"redacted", MONASHNS.val, u"[IDENTIFYING MATERIAL REMOVED]", u"70", u"78")
      # overlaps
      self.annotation_present(ann_graph, u"overlap", MONASHNS.val, u"overlap", u"86", u"90")


  def testMEP6(self):
      filename = "../input/Monash Corpus of Australian English/Transcripts-sanitised/MEP6_Sanitised.doc"
      
      ingest = MonashIngest()
      (sampleid, raw, text, metadata, anns) = ingest.ingestDocument(filename)
      
      (meta_graph, ann_graph) = ingest._MonashIngest__serialise('../input/Monash Corpus of Australian English/Transcripts-sanitised/', \
                                                                 '/tmp', filename, sampleid, 'MEP6_Sanitised.doc', raw, text, metadata, anns)
                                                                 
      itemuri = MONASHCORPUS[u"items/MEP6_Sanitised"]

      # test some select metadata
      self.one_of(meta_graph, itemuri, AUSNC.TRANSCRIBER, Literal(u'BL'))
      self.one_of(meta_graph, itemuri, AUSNC.MothersEthnicity, Literal(u'Born in Australia'))
      self.one_of(meta_graph, itemuri, AUSNC.FathersEthnicity, Literal(u'Born in Italy'))
      self.one_of(meta_graph, itemuri, AUSNC.MaternalGrandmothersEthnicity, Literal(u'Italian'))
      self.one_of(meta_graph, itemuri, AUSNC.MaternalGrandfathersEthnicity, Literal(u'Italian'))
      self.one_of(meta_graph, itemuri, AUSNC.PaternalGrandmothersEthnicity, Literal(u'Italian'))
      self.one_of(meta_graph, itemuri, AUSNC.PaternalGrandfathersEthnicity, Literal(u'Italian'))
      self.one_of(meta_graph, itemuri, AUSNC.LanguagesSpokenathome, Literal(u'English, Italian'))  
      self.one_of(meta_graph, itemuri, AUSNC.notes, Literal(u'The informant was born in Australia, as was his mother. His father came\nfrom Italy about 20 years ago, and all of his grandparents were born in\nItaly. His paternal grandmother still lives in Italy, but he hasn\u2019t visited\nand hasn\u2019t met her. His maternal grandparents are in Australia. His parents\nspeak Italian to each other, his father speaks Italian to him, and he\nusually answers in English. He speaks English with his mother. His\ngrandparents speak Italian to him, and, once again, he usually answers in\nEnglish. He learns Italian at school.'))

      first_part = u"Alright. So. What is your name?\nREDACTED\nYep - and - where do you live?\nUh \u2013 REDACTED.\nMm - mm. And how long have you lived there?"
      self.assertEqual(text[:130], first_part)
      # speaker turns
      self.annotation_present(ann_graph, u"speaker", MONASHNS.val, u"RM", u"0", u"31")
      self.annotation_present(ann_graph, u"speaker", MONASHNS.val, u"P6M", u"32", u"40")
      self.annotation_present(ann_graph, u"speaker", MONASHNS.val, u"RM", u"41", u"71")
      self.annotation_present(ann_graph, u"speaker", MONASHNS.val, u"P6M", u"72", u"86")
      self.annotation_present(ann_graph, u"speaker", MONASHNS.val, u"RM", u"87", u"130")
      # redacted
      self.annotation_present(ann_graph, u"redacted", MONASHNS.val, u"[IDENTIFYING MATERIAL REMOVED]", u"32", u"40")
      self.annotation_present(ann_graph, u"redacted", MONASHNS.val, u"[IDENTIFYING MATERIAL REMOVED]", u"77", u"85")


  def testParticipantDescriptions(self):
      """Do participants get the right descriptive fields"""
      
      filename = "../input/Monash Corpus of Australian English/Transcripts-sanitised/MECG1MA_Sanitised.doc"
      ingest = MonashIngest()
      (sampleid, raw, text, metadata, anns) = ingest.ingestDocument(filename)
      
      (meta_graph, ann_graph) = ingest._MonashIngest__serialise('../input/Monash Corpus of Australian English/Transcripts-sanitised/', \
                                                                 '/tmp', filename, sampleid, 'MECG1MA_Sanitised.doc', raw, text, metadata, anns)
                                                                 
      # should have one Object
      obj = meta_graph.value(None, RDF.type, AUSNC.Object)
      
      # with two speakers
      spkrs = list(meta_graph.objects(obj, OLAC.speaker))
      self.assertEquals(len(spkrs), 2, "Wrong number of speakers: %s" % spkrs)

      # one of them should be primary speaker and have various other attributes
      primary = meta_graph.value(None, AUSNC.role, Literal('primary'))
      self.failUnless(any([s==primary for s in spkrs]), "Primary speaker (%s) not in speakers list (%s)" % (str(primary), str(spkrs)))
      
      # and check some primary properties
      age = meta_graph.value(primary, FOAF.age)
      self.assertEquals(age, Literal("16"), "Wrong value for age: %s" % age)
      
      gender = meta_graph.value(primary, FOAF.gender)
      self.assertEquals(gender, Literal("male"), "Wrong value for gender: %s" % gender)
      
  def testParsingOfMEBHFB(self):
    raw = """
                              MONASH UNIVERSITY
                          Department of Linguistics


                   Australian English Project (1996-1998)
                    The Talk of Young People in Melbourne


    |CODE:           |BH5F.B          |INTERVIEWER     |JC (RF3)        |
|                |                |(if relevant):  |                |
|STUDENT'S       |LM              |SCHOOL:         |BH              |
|INITIALS:       |                |                |                |
|AGE:            |16              |SEX:            |F               |
|TRANSCRIBER:    |BL              |BIRTHPLACE:     |Born in         |
|                |                |                |Australia?      |
|                |                |                |(presumably,    |
|                |                |                |although the    |
|                |                |                |question was not|
|                |                |                |asked)          |
|Mother's Ethnicity:               |Born in Scotland                  |
|Father's Ethnicity:               |Born in Australia (in the local   |
|                                  |area)                             |
|Maternal Grandmother's Ethnicity: |                                  |
|Maternal Grandfather's Ethnicity: |                                  |
|Paternal Grandmother's Ethnicity: |                                  |
|Paternal Grandfather's Ethnicity: |                                  |
|Language(s) Spoken at home:       |English                           |

{The informant's mother was born in the north east of Scotland and came to
Australia when she was about twelve. The informant is making plans to visit
Scotland with her mother at the end of Year twelve, and also to live in
England with a friend as she has relatives there as well as some friends
(it doesn't appear that she has travelled to England or Scotland before)}

Note: this recording was made at school in a noisy, echoing environment.
Comprehensible transcription is minimal as participants talk simultaneously
throughout the recording. Speaker identification is difficult.

Participants:
BH5F
BH5FPf1
BH5FPm1
BH5FPm2
?



BH5FPm1:    ??zero.three kilograms??
BH5F: this is.my interview.with my friends.at school
???
BH5F: yes.ok then ??
???
BH5FPm1:    ok.go
BH5F: ??? about anything
???
BH5FPm2:    I play basketball
BH5F: ??? basketbal
BH5FPm2:    I do
BH5F: ??? play basketball
???
BH5FPm2:    except ??? on  Friday
???
BH5FPm1:    hello!
BH5F: @@ ??
BH5FPm1:    when's the recording
@@@
Farting noise
???
          """
    obj = MonashIngest()
    res, bodyres = obj._MonashIngest__parseData(raw)
    self.assertEqual("BH5F", res["participants"][0])
    self.assertEqual("BH5FPf1", res["participants"][1])
    self.assertEqual("BH5FPm1", res["participants"][2])
    self.assertEqual("BH5FPm2", res["participants"][3])
    self.assertEqual("?", res["participants"][4])

    body, anns = obj._MonashIngest__extractAnnotations(bodyres["body"], res["participants"])



