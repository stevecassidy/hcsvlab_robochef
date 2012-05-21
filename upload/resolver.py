import os
import rdflib
import re

from ausnc_ingest.rdf.map import DC, RDF, FOAF, AUSNC
from rdflib import Graph
from rdflib.term import URIRef

class Resolver(object):
  
  
  def get_document_type(self, meta_document, subject_uri):
    ''' Method retrieves the documenttype property for a particular document '''
    result = ''
  
    if not os.path.exists(meta_document):
      return result
    
    graph = self.__create_graph(meta_document)
    
    for subject in graph.subjects(predicate = RDF.type, object = FOAF.Document):
      if str(subject) == subject_uri:
        for s,p,o in graph.triples((subject, FOAF['documenttype'], None)):
          return str(o)  
    
      
  def get_identifier(self, meta_document):
    ''' Retrieves the title from the meta item dc:title '''
    result = ''
  
    if not os.path.exists(meta_document):
      return result
    
    graph = self.__create_graph(meta_document)

    for subject in graph.subjects(predicate = RDF.type, object = AUSNC.AusNCObject):
      for s,p,o in graph.triples((subject, None, None)):
        if re.search('/identifier', str(p)):
          result = str(o)

    return result
    
    
  def get_title(self, meta_document):
    ''' Retrieves the title from the meta item dc:title '''
    result = ''
  
    if not os.path.exists(meta_document):
      return result
        
    graph = self.__create_graph(meta_document)

    for subject in graph.subjects(predicate = RDF.type, object = AUSNC.AusNCObject):
      for s,p,o in graph.triples((subject, None, None)):
        # The title can appear in different namespaces so we do not predicate using the namespace 
        # i.e. DC['title] as opposed to AUSNC['title]
        if re.search('/title', str(p)):
          result = str(o)

    return result
  
  
  def get_upload_units(self, rdf_document):
    ''' Return a list of files to upload, this list is obtained from the meta data file '''
    result = []
    
    if not os.path.exists(rdf_document):
      return result
     
    graph = self.__create_graph(rdf_document)
    
    # TODO: Is there a more efficient way to query for this?
    for s,p,o in graph.triples((None, FOAF['documentname'], None)):
      result.append(str(o))
    
    return result
    

  def get_item_uri(self, rdf_document):
    ''' Returns the item level uri '''
    result = ''
    
    if not os.path.exists(rdf_document):
      return result

    graph = self.__create_graph(rdf_document)

    for s in graph.subjects(predicate = RDF.type, object = AUSNC.AusNCObject):
      result = str(s)

    return result
      
      
  def get_subject_uri(self, rdf_document, source_document_name):
    ''' Return a string representation of the subject for which we have a matching document name
    Note this will return the first match, if multiple documents with the same name exist
    this function fails '''
    if not os.path.exists(rdf_document):
      return ''
    
    graph = self.__create_graph(rdf_document)
    
    # TODO: Is there a more efficient way to query for this?
    for s,p,o in graph.triples((None, FOAF['documentname'], None)):
      if o == source_document_name:
        return str(s)
    
    # Could not find it so return empty subject string (better than none?)
    return ''
    
    
  def __create_graph(self, rdf_document):
    ''' This method only supports graphs in the N3 format '''
    graph = Graph()
    graph.parse(rdf_document, format='n3')
    return graph