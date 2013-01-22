from ausnc_ingest.rdf.map import FOAF, DBPEDIA, BIO, SCHEMA, Namespace, DC, Literal, DADA
import rdflib
import unittest

class AusNCTest(unittest.TestCase):

  def annotation_present(self, anns, ty, valty, val, start, end):
      """
      Chases a chain of triples to check if a particular annotaion is present in the set of annotations (the RDF graph) given.
      """
      start_found = False
      end_found = False
      for t1 in anns.triples((None, DADA.type, Literal(ty))):
          for t2 in anns.triples((t1[0], valty, Literal(val))):
              for t3 in anns.triples((t1[0], DADA.annotates, None)):
                for t4 in anns.triples((t3[2], DADA.targets, None)):
                    for t5 in anns.triples((t4[2], None, None)):
                        if (   t5[1] == DADA.start  \
                           and t5[2] == Literal(start, datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#integer')) \
                           ):
                             start_found = True
                        if (   t5[1] == DADA.end  \
                           and t5[2] == Literal(end, datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#integer')) \
                           ):
                             end_found = True
      self.assertTrue(start_found and end_found, "could not find %s annotation %s: %s -> %s" % (ty, val, start, end))
