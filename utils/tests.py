import unittest
import os

from hcsvlab_robochef.utils.parsing import *
from hcsvlab_robochef.utils.program import *
from hcsvlab_robochef.utils.filehandler import *
from hcsvlab_robochef.utils.serialiser import *
from hcsvlab_robochef.utils.statistics import *


def unittests():
  return unittest.makeSuite(UnitTest)  

class UnitTest(unittest.TestCase):
  

  fileHandler = FileHandler()


  def testEntityConversion(self):
    self.assertEqual(replaceEntitiesInStr("what <is> going </is> on"), u"what <is> going </is> on")
    self.assertEqual(replaceEntitiesInStr("what <is> go&para;ing </is> on"), u"what <is> go\u00b6ing </is> on")
    self.assertEqual(putLTBack(replaceEntitiesInStr("what does <= mean?")), "what does <= mean?")


  def testFileHandlerOnDirectoryWithDataAndValidExtension(self):    
    resultSet = self.fileHandler.getFiles('../input/ace', inclusionPredicate = r'^ace_.\.txt')
    self.assertEqual(len(resultSet), 17)

    
  def testFileHandlerOnDirectoryWithDataAndInvalidExtension(self):   
    resultSet = self.fileHandler.getFiles('../input/ace', inclusionPredicate = r'\w+.rdf')
    self.assertEqual(len(resultSet), 0)

    
  def testFileHandlerOnInvalidDirectory(self):   
    resultSet = self.fileHandler.getFiles('../input/nonexistentfolder', inclusionPredicate = r'\w+.rdf')    
    self.assertEqual(len(resultSet), 0)
    

  def testSuccessfulFilePatternMatch(self):   
    result = self.fileHandler.isMatch("testFile.rdf", r"\w+.rdf", r"\w+-raw.txt")
    self.assertTrue(result)

    
  def testUnsuccessfulFilePatternMatch(self):
    result = self.fileHandler.isMatch("testFile-raw.rdf", r"\w+.rdf", r"\w+-raw.rdf")
    self.assertFalse(result)
    
    
  def testSizeOfMissingFile(self):
    self.assertEqual(self.fileHandler.getFileSize('missingFile.rdf'), 0)
    
    
  def testSizeOfDirectory(self):
    self.assertEqual(self.fileHandler.getFileSize('../input'), 0)
    
    
  def testSizeOfKnownFile(self):
    self.assertEqual(self.fileHandler.getFileSize('../input/ace/ace_a.txt'), 579959)
    
  
  def testSizeOfAudioFile(self):
    self.assertEqual(self.fileHandler.getFileSize('../input/md/S1219s1.wav'), 135752)


  def testSizeOfSourceString(self):
    stats = Statistics()
    lines = open('../input/ace/ace_a.txt', 'r').read()
    meta_dict = {}
    stats.append_item_stats(lines, meta_dict)
    self.assertEqual(self.fileHandler.getFileSize('../input/ace/ace_a.txt'), meta_dict['filesize'])
    
    
  def testWordCountOnMissingFile(self):
    stats = Statistics()
    self.assertEqual(stats.get_word_count('missingFile.txt'), 0)
    
    
  def testWordCountOnAudioFile(self):
    stats = Statistics()
    self.assertEqual(stats.get_word_count('../input/md/S1219s1.wav'), 0)
    
  
  def testWordCountOnTxtFile(self):
    stats = Statistics()
    self.assertEqual(stats.get_word_count('../input/ace/ace_a.txt'), 92466)
    
    
  def testWordCountOnEmptyString(self):
    stats = Statistics()
    self.assertEqual(stats.get_sample_wordcount(''), 0)
    

  def testWordCountOnSingleLetter(self):
    stats = Statistics()
    self.assertEqual(stats.get_sample_wordcount('A'), 1)
    

  def testWordCountOnWordSeparatedByHyphens(self):
    stats = Statistics()
    self.assertEqual(stats.get_sample_wordcount('One-World-Alliance'), 1)
    
 
  def testWordCountOnWordWithNestedTags(self):
    stats = Statistics()
    self.assertEqual(stats.get_sample_wordcount('One-<World>World</World>-Alliance'), 3)
    
  
  def testWordCountOnWordWithNestedTagsAndNoHyphens(self):
    stats = Statistics()
    self.assertEqual(stats.get_sample_wordcount('One <World>World</World> Alliance'), 3)
    
  
  def testWordCountOnWordWithNestedMalformedTagsAndNoHyphens(self):
    stats = Statistics()
    self.assertEqual(stats.get_sample_wordcount('One <World>World Alliance'), 3)
    
    
  def testWordCountOnWordWithMultipleTagsAndNoSpaces(self):
    stats = Statistics()
    self.assertEqual(stats.get_sample_wordcount('One<World>World</World><Alliance>Alliance</Alliance>'), 3)
    
    
  def testToFindExistingCompatriotFile(self):
    compatriot = self.fileHandler.findCompatriot('../input/griffith', 'GCSAusE06.doc', '^[\w\d-]+.mp3', '^[\w\d-]+.doc')
    self.assertEqual('../input/griffith/aa323c84-7483-10a3-d8b6-603a7f5d852a_1/GCSAusE06.mp3', compatriot)
    
  
  def testToFindNonExistingCompatriotFile(self):
    compatriot = self.fileHandler.findCompatriot('../input/griffith', 'GCSAusE99.doc', '^[\w\d-]+.mp3', '^[\w\d-]+.doc')
    self.assertEqual(None, compatriot)
    
    
  def testGenerateOfMetaDict(self):
    serialiser = Serialiser('/tmp')
    res = serialiser._Serialiser__gen_text_document_metadata('GCSAusE01', 'Text', 'http://www.google.com/')
    
    self.assertEqual(res, {'documenttitle': 'GCSAusE01#Text', 'filetype': 'Text', 'filename': 'GCSAusE01-plain.txt', 'id': 'GCSAusE01#Text', 'filesize': 22})
    
    
  def testAddToDictionariesWithNonExistingKey(self):
    dict1 = {'1': 1, '2': 2}
    dict2 = { '3': 3}
    
    res = add_to_dictionary('3', dict1, dict2)
    self.assertEqual(res, { '1': 1, '2': 2, '3': {'3': 3}})
    
    
  def testAddDictionariesWithExistingKey(self):
     dict1 = {'1': 1, '2': 2}
     dict2 = { '2': {'3': 3}}

     res = add_to_dictionary('2', dict1, dict2)
     self.assertEqual(res, {'1': 1, '2': {'3': 3}})
     
 
  def testAddDictionariesWithExistingKey1(self):
    dict1 = {'1': 1, '2': {'a': 'a', 'b': 'b'}}
    dict2 = { 'c' : 'c'}

    dict1 = add_to_dictionary('2', dict1, dict2)
    self.assertEqual(dict1, {'1': 1, '2': {'a': 'a', 'b': 'b', 'c': 'c'}})