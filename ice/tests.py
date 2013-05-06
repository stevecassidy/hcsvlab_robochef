import re
import unittest
import logging
import rdflib
import unittest
import os

from hcsvlab_robochef.ice.ingest import *
from hcsvlab_robochef.ice import ingest
from hcsvlab_robochef.rdf.map import *

def unittests():
  res = unittest.makeSuite(UnitTest)
  return res


def unittests():
  return unittest.makeSuite(UnitTest)

ICEDIR = "../input/ICE/"

class UnitTest(unittest.TestCase):

    ingest = ICEIngest()

    def testIngestW1A(self):
        """Test conversion of the metadata field genre_subject from the ICE written
        spreadsheet"""
        
        self.ingest.setWrittenMetaData(os.path.join(ICEDIR, "metadata"))
                        
        sourcepath = os.path.join(ICEDIR, "standoff/written/W1A/W1A-001.txt")
        (id, raw, text, meta, annotation) = self.ingest.ingestDocument(sourcepath)
        (meta_graph, ann_graph) = self.ingest._ICEIngest__serialise('/tmp', id, text, meta, annotation)
        
        self.assertEquals(id, "W1A-001")
        
        self.failUnless(text.find('Diskinetic')>0, "target text not found in W1A output text")
          
        # check that the genre property was set correctly
        for triple in  meta_graph.triples((None, AUSNC.genre, None)):
            (uri, ignore, genre) = triple
            self.assertEquals(genre, "Untimed Student Essay")
        
        # and that we got the DC.subject too
        for triple in  meta_graph.triples((None, DC.subject, None)):
            (uri, ignore, genre) = triple
            self.assertEquals(genre, "Music Honours")
            
        # what's the item uri
        for triple in  meta_graph.triples((None, RDF.type, AUSNC.AusNCObject)):
            (uri, ignore, ignore) = triple
            self.assertEquals(uri, rdflib.term.URIRef('http://ns.ausnc.org.au/corpora/ice/items/W1A-001'))
        

    @unittest.skip("This test was created to extract meta data with no corollary sub-samples in source docs") 
    def testExtractionOfIceWrittenMetaDataWithPostAlpha(self):
        self.ingest.setWrittenMetaDataFile("../input/ICE/metadata")
        
        resultSet = ()
        for key, value in filemetadata.items():
          match = re.search('[a-zA-Z]$', key)
          if match:
            resultSet = resultSet + (key,)    
        
        logging.basicConfig(filename='ice.log', level=logging.INFO)
        for value in sorted(resultSet):
          logging.info(value)
      
      
