import unittest

from hcsvlab_robochef.cooee.ingest import *
from rdflib import Namespace, Graph, Literal
from hcsvlab_robochef.rdf.map import FOAF, DBPEDIA, BIO, SCHEMA

COOEE = Namespace(u"http://ns.ausnc.org.au/corpora/cooee/")
COOEENS = Namespace(u"http://ns.ausnc.org.au/schemas/cooee/")


def get_uris(sample):
  itemuri = COOEE[u"items/%s" % sample]
  authoruri = COOEE[u"person/%sauthor" % sample]
  addresseeuri = COOEE[u"person/%saddressee" % sample]
  sourceuri = COOEE[u"items/%s_source" % sample]
  return {"item": itemuri, "author": authoruri, "addressee": addresseeuri, "source": sourceuri}

def unittests():
  res = unittest.makeSuite(UnitTest)
  return res 
   

class UnitTest(unittest.TestCase):
  
  ingest = CooeeIngest()
  
  def one_of(self, metadata, i, ty, val):
    sofar = 0
    found = metadata.triples((i, ty, None))
    for triple in found:
      self.assertEqual(triple[2], val, "found %s in triple, expecting %s" % (triple[2], val))
      sofar = sofar + 1
 
    self.assertEqual(sofar,1, "found %d triples matching (%s, %s, None), expected 1" % (sofar, i, ty))


  def with_and_without(self, tst):
    self.ingest.filemetadata = {}
    tst(self)
    self.ingest.setMetaData("../input/COOEE/COOEE.XLS")
    tst(self)    


  def test25(self):
    
    filename = "../input/COOEE/data/1-025.txt"
    
    (sampleid, raw, text, metadata, anns) = self.ingest.ingestDocument(filename)
    
    # text should not contain any markup, eg. no angle brackets
    self.assertTrue(text.find('<')==-1, "Found markup in plain text of COOEE doc:" + text)
    
    (meta_graph, ann_graph) = self.ingest._CooeeIngest__serialise('/tmp', sampleid, raw, text, metadata, anns, filename)
                                                               
    self.assertEqual(raw, open(filename, 'r').read())

    self.one_of(meta_graph, get_uris("1-025")['author'], FOAF.age, Literal(u'53'))
    self.one_of(meta_graph, get_uris('1-025')['author'], FOAF.gender, Literal(u'male'))
    self.one_of(meta_graph, get_uris('1-025')['author'], COOEENS.abode, Literal(u'3'))
    self.one_of(meta_graph, get_uris('1-025')['item'],   SCHEMA.localityName, DBPEDIA.New_South_Wales)
    self.one_of(meta_graph, get_uris('1-025')['item'],   COOEENS.texttype, Literal(u'Legal English'))
    self.one_of(meta_graph, get_uris('1-025')['item'],   COOEENS.register, Literal(u'Government English'))
    
    # self.with_and_without(run)

    
  def test244(self):
    
    filename = "../input/COOEE/data/1-244.txt"
    
    (sampleid, raw, text, metadata, anns) = self.ingest.ingestDocument(filename)
    (meta_graph, ann_graph) = self.ingest._CooeeIngest__serialise('/tmp', sampleid, raw, text, metadata, anns, filename)
    
    self.assertEqual(raw, open(filename, 'r').read())

    self.one_of(meta_graph, get_uris("1-244")['author'], FOAF.age, Literal(u'52'))
    self.one_of(meta_graph, get_uris('1-244')['author'], FOAF.gender, Literal(u'male'))
    self.one_of(meta_graph, get_uris('1-244')['author'], COOEENS.abode, Literal(u'4'))
    self.one_of(meta_graph, get_uris('1-244')['item'],   SCHEMA.localityName, DBPEDIA.New_South_Wales)
    self.one_of(meta_graph, get_uris('1-244')['item'],   COOEENS.texttype, Literal(u'Imperial Correspondence'))
    self.one_of(meta_graph, get_uris('1-244')['item'],   COOEENS.register, Literal(u'Government English'))
    
    # self.with_and_without(run)
    