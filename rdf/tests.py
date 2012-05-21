import unittest
#import os
#import subprocess
#import sys

from ausnc_ingest.rdf.map import *
from ausnc_ingest.rdf.serialiser import *

NS = Namespace("http://example.org/")

def unittests():
    res = unittest.makeSuite(UnitTest)
    return res

class UnitTest(unittest.TestCase):
  
    def test_simple_mapping(self):
      
        iceM = FieldMapper(NS)
        iceM.add('table_category', mapto=AUSNC.genre)
        iceM.add('table_date_of_recording', mapto=DC.created)
        
        self.assertEqual(iceM('table_category', 'one'), ((AUSNC.genre, Literal('one')),))
        self.assertEqual(iceM('table_date_of_recording', 'two'), ((DC.created, Literal('two')),))                
        self.assertEqual(iceM('table_something_else', 'three'), ((AUSNC['something_else'], Literal('three')),))
        self.assertEqual(iceM('whatever', 'four'), ((AUSNC['whatever'], Literal('four')),))
        
    
    def test_dict_mapping_no_sampleid(self):
        """Test mapping of metadata dictionary where there is no
        sampleid field set, result is an exception"""
        
        iceM = FieldMapper(NS)
        iceM.add('table_category', mapto=AUSNC.genre)
        iceM.add('table_date_of_recording', mapto=DC.created)
    
        md = {'table_category': "one",
              'table_date_of_recording': "two",
              'table_something_else': 'three'}
        
        try:
            iceM.mapdict(md)
            self.fail("No exception raised for metadata with no sampleid")
        except Exception:
            pass
        
        
    def test_dict_mapping(self):
        """Test mapping of metadata dictionary where everything works ok"""
        
        iceM = MetadataMapper(NS)
        iceM.add('table_category', mapto=AUSNC.genre)
        iceM.add('table_date_of_recording', mapto=DC.created)
    
        md = {'sampleid': 'mysample',
              'table_category': "one",
              'table_date_of_recording': "two",
              'table_something_else': 'three'}
        

        # check that the triples are present
        itemuri = iceM.item_uri(md['sampleid'])
        corpusuri = iceM.corpus_uri()
        g = iceM.mapdict(md)
        
        self.assertTrue((itemuri, AUSNC.genre, Literal("one")) in g)
        self.assertTrue((itemuri, DC.created, Literal("two")) in g)
        self.assertTrue((itemuri, AUSNC.something_else, Literal("three")) in g)
        self.assertFalse((itemuri, AUSNC.sampleid, Literal("mysample")) in g)
        self.assertTrue((itemuri, RDF.type, FOAF.Document))
        self.assertTrue((itemuri, DC.identifier, Literal("mysample")) in g)
        self.assertTrue((itemuri, DC.isPartOf, corpusuri) in g)
        
        # size should be the number of properties (3) plus the 2 statements about the item (isPartOf and Subject Uri)
        turtle_ser = g.serialize(format="turtle")
        #print turtle_ser
        
        self.assertEqual(len(g), 2+4)

        
        
    def test_ignored_mapping(self):
        """Test mapping of metadata dictionary where a field is ignored"""
        
        iceM = FieldMapper(NS)
        iceM.add('table_category', ignore=True, mapto=AUSNC.genre)
        iceM.add('table_date_of_recording', mapto=DC.created)
    
        md = {'sampleid': 'mysample',
              'table_category': "one",
              'table_date_of_recording': "two",
              'table_something_else': 'three'}
        

        # check that the triples are present
        itemuri = iceM.item_uri(md['sampleid'])
        g = iceM.mapdict(md)
        
        # should be no triple with value "one" in the graph (from table_category)
        self.assertFalse((itemuri, None, Literal("one")) in g)
        
        self.assertTrue((itemuri, DC.created, Literal("two")) in g)
        self.assertTrue((itemuri, AUSNC.something_else, Literal("three")) in g)
        self.assertFalse((itemuri, DC.isPartOf, iceM.corpus_uri()) in g)
        
                
    def test_mapping_function(self):
        """Test mapping of metadata fields using a mapping
        function"""
        
        def uppercase(key, value):
            return (key, Literal(value.upper()))
        
        iceM = FieldMapper(NS)
        iceM.add('table_category', mapto=AUSNC.genre, mapper=uppercase)
        iceM.add('table_size', mapper=uppercase)  # without mapto
        iceM.add('table_date_of_recording', mapto=DC.created)
    
        
        self.assertEqual(iceM('table_category', 'one'), (AUSNC.genre, Literal('ONE')))
        self.assertEqual(iceM('table_size', 'six'), (AUSNC.size, Literal('SIX')))
 
        
    def test_mapping_person(self):
        """Test mapping with a person description in 
        the metadata"""
    
        iceSpeakerM = FieldMapper(AUSNC)
        iceSpeakerM.add('name', mapto=FOAF.name)
        iceSpeakerM.add('occupation', mapto=AUSNC.occupation)
        iceSpeakerM.add('age', mapto=FOAF.age)    
        
        
            
        iceM = MetadataMapper(NS, iceSpeakerM)
        iceM.add('table_category', mapto=AUSNC.genre)
        iceM.add('table_date_of_recording', mapto=DC.created)
    
        speakerA = {'id': "James",
                    'age': 73,
                    'occupation': 'Godfather of Soul',
                    'name': "James Brown",
                    'role': 'speaker'}
        
        speakerB = {'id': "Ray",
                    'age': 72,
                    'occupation': 'Being Ray Charles',
                    'name': "Ray Charles",
                    'role': 'speaker'}
            
        md = {'sampleid': 'mysample',
              'table_category': "one",
              'table_date_of_recording': "two",
              'table_person_A': speakerA,
              'table_person_B': speakerB,
              }
        
        # check that the triples are present
        itemuri = iceM.item_uri(md['sampleid'])
        speakerAid = iceM.speaker_uri(speakerA['id'])
        speakerBid = iceM.speaker_uri(speakerB['id'])
        
        g = iceM.mapdict(md)
        self.assertTrue((itemuri, AUSNC.genre, Literal("one")) in g)
        self.assertTrue((itemuri, DC.created, Literal("two")) in g)
        self.assertTrue((itemuri, DC.isPartOf, iceM.corpus_uri()) in g)

        # check speaker A properties
        self.assertTrue((speakerAid, FOAF.name, Literal("James Brown")) in g)
        self.assertTrue((speakerAid, AUSNC.occupation, Literal("Godfather of Soul")) in g)
        self.assertTrue((speakerAid, FOAF.age, Literal(73)) in g)
        self.assertFalse((speakerAid, DC.isPartOf, iceM.corpus_uri()) in g)
        
        # check speaker B properties
        self.assertTrue((speakerBid, FOAF.name, Literal("Ray Charles")) in g)
        self.assertTrue((speakerBid, AUSNC.occupation, Literal("Being Ray Charles")) in g)
        self.assertTrue((speakerBid, FOAF.age, Literal(72)) in g)        
        self.assertFalse((speakerBid, DC.isPartOf, iceM.corpus_uri()) in g)
        
        turtle_ser = g.serialize(format="turtle")
        # print turtle_ser
        

    def test_serialise_person(self):
      
        iceSpeakerM = FieldMapper(AUSNC)
        iceSpeakerM.add('name', mapto=FOAF.name)
        iceSpeakerM.add('occupation', mapto=AUSNC.occupation)
        iceSpeakerM.add('age', mapto=FOAF.age)
          
        iceM = MetadataMapper(NS, iceSpeakerM)
        iceM.add('table_category', mapto=AUSNC.genre)
        iceM.add('table_date_of_recording', mapto=DC.created)
  
        speakerA = {'id': "James",
                  'age': 73,
                  'occupation': 'Godfather of Soul',
                  'name': "James Brown",
                  'role': 'speaker'}
                  
        md = {'sampleid': 'GCSAusE01',
              'table_category': "one",
              'table_date_of_recording': "two",
              'table_person_A': speakerA
        }
                        
        serialiser = MetaSerialiser()
        g = serialiser.serialise('/tmp', 'GCSAusE01', iceM, md)
  
        speakerAid = iceM.speaker_uri(speakerA['id'])
      
        self.assertTrue((speakerAid, FOAF.name, Literal("James Brown")) in g)
        self.assertTrue((speakerAid, AUSNC.occupation, Literal("Godfather of Soul")) in g)
        self.assertTrue((speakerAid, FOAF.age, Literal(73)) in g)
        self.assertFalse((speakerAid, DC.isPartOf, iceM.corpus_uri()) in g)
        
        # print g.serialize(format="turtle")

      


if __name__=='__main__':
    unittest.main()