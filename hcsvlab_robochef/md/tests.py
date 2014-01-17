import re
import unittest

from hcsvlab_robochef.md.organiser import *
from hcsvlab_robochef.md.ingest import *


def unittests():
  res = unittest.makeSuite(UnitTest)
  return res

class UnitTest(unittest.TestCase):  
  
  ingest = MDIngest()
  
  @unittest.skip("This tests were written for the MD directory transformations, it does not require testing as it is a one off")  
  def testUtilWhichRetrievesFileList(self):  
    organiser = Organiser()
    file_list = organiser.get_file_list('/Users/Shirren/var/fileserver/clt/Mitchell&Delbridge')
    
    self.assertEqual(len(file_list), 23437)
    

  @unittest.skip("This tests were written for the MD directory transformations, it does not require testing as it is a one off") 
  def testObtainDataKeysFromFileList(self):
    organiser = Organiser()
    file_list = organiser.get_file_list('/Users/Shirren/var/fileserver/clt/MD/tardis1/SndArchivePt1/Mitchell&Delbridge/tape01/')

    key_list = organiser.get_data_keys('/Users/Shirren/var/fileserver/clt/MD/tardis1mod', file_list)
    self.assertEqual(len(key_list), 4)
    
    
  @unittest.skip("This tests were written for the MD directory transformations, it does not require testing as it is a one off") 
  def testCopyOfData(self):
    organiser = Organiser()
    organiser.organise('/Users/Shirren/var/fileserver/clt/Mitchell&Delbridge',\
                      '/Users/Shirren/var/fileserver/clt/Mitchell&DelbridgeModified')
                      

  @unittest.skip("This tests were written for the MD directory transformations, it does not require testing as it is a one off") 
  def testExtractMetaData(self):
    self.ingest.setMetaData("../input/MD/flatfilesrc.txt")
    self.ingest.ingestCorpus("/Users/Shirren/Desktop/md", "../output/md")
      

  def testParseOnMissingAnnotationFile(self):
    self.assertEqual(self.ingest._MDIngest__parse_annotation('word', 'missing.fword'), None)

  
  def testParseOnASampleFlabFile(self):
    anns =  self.ingest._MDIngest__parse_annotation('phonetic', '../input/MD/S1222s1.flab')
    self.assertEqual(len(anns), 14)
    self.__text_segment_match__(r'\<start\>2.7761\<\/start\>', anns[1].to_xml_str(), '<start>2.7761</start>')
    self.__text_segment_match__(r'\<end\>2.9661\<\/end\>', anns[1].to_xml_str(), '<end>2.9661</end>')
    self.__text_segment_match__(r'\<property name="val"\>i:\<\/property\>', anns[1].to_xml_str(), '<property name="val">i:</property>')
      

  def testGetAnnotationsWhereOnlyTheFlabFileExists(self):
    anns1 = self.ingest._MDIngest__get_annotations('S1219s1.wav', '../input/MD/S1219s1.wav')
    anns2 = self.ingest._MDIngest__parse_annotation('phonetic', '../input/MD/S1219s1.flab')
    self.assertEqual(anns1, anns2)


  def testGetAnnotationsWhereTheFlabAndFWordFileExists(self):
    anns = self.ingest._MDIngest__get_annotations('S1222s1.wav', '../input/MD/S1222s1.wav')
    self.assertEqual(len(anns), 20)

  def testParseFWordFile(self):
    anns = self.ingest._MDIngest__parse_annotation('word', '../input/MD/S1221s1.fword')
    self.assertEqual(len(anns), 6)
    self.__text_segment_match__(r'\<start\>3.0364\<\/start\>', anns[0].to_xml_str(), '<start>3.0364</start>')
    self.__text_segment_match__(r'\<end\>3.6664\<\/end\>', anns[0].to_xml_str(), '<end>3.6664</end>')
    self.__text_segment_match__(r'\<property name="val"\>beat\<\/property\>', anns[0].to_xml_str(), '<property name="val">beat</property>')


  def testParseWordFile(self):
    anns =  self.ingest._MDIngest__parse_annotation('word', '../input/MD/S1221s1.word')
    self.assertEqual(len(anns), 6)
    self.__text_segment_match__(r'\<start\>3.036400\<\/start\>', anns[0].to_xml_str(), '<start>3.036400</start>')
    self.__text_segment_match__(r'\<end\>3.489062\<\/end\>', anns[0].to_xml_str(), '<end>3.489062</end>')
    self.__text_segment_match__(r'\<property name="val"\>beat\<\/property\>', anns[0].to_xml_str(), '<property name="val">beat</property>')


  def testParseAnnotationsWithBSeparator(self):
    anns =  self.ingest._MDIngest__parse_annotation('word', '../input/MD/S1229s1.word')
    self.assertEqual(len(anns), 6)
    self.__text_segment_match__(r'\<start\>3.292178\<\/start\>', anns[1].to_xml_str(), '<start>3.292178</start>')
    self.__text_segment_match__(r'\<end\>3.561900\<\/end\>', anns[1].to_xml_str(), '<end>3.561900</end>')
    self.__text_segment_match__(r'\<property name="val"\>boot\<\/property\>', anns[1].to_xml_str(), '<property name="val">boot</property>')


  def testParseAnnotationsWithBSharpAndPlusSeparator(self):
    anns =  self.ingest._MDIngest__parse_annotation('word', '../input/MD/S1262s1.word')
    self.assertEqual(len(anns), 6)
    self.__text_segment_match__(r'\<start\>5.809222\<\/start\>', anns[5].to_xml_str(), '<start>5.809222</start>')
    self.__text_segment_match__(r'\<end\>6.094200\<\/end\>', anns[5].to_xml_str(), '<end>6.094200</end>')
    self.__text_segment_match__(r'\<property name="val"\>low\<\/property\>', anns[5].to_xml_str(), '<property name="val">low</property>')
    
               
  @unittest.skip("This tests were written for the MD directory transformations, it does not require testing as it is a one off") 
  def testIngestSingleDocumentWithPhoneticAnnotations(self):
     self.ingest.ingestDocument('S1210s1.wav', '/Users/Shirren/var/fileserver/clt/Mitchell&DelbridgeModified/S12/S1210s1.wav', '../output/md')
    
    
  def __text_segment_match__(self, reg_ex, source, expectation):
    item = re.findall(reg_ex, source)
    self.assertEqual(item[0], expectation)