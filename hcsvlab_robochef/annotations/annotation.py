from UserDict import DictMixin
from xml.etree import ElementTree
from uuid import uuid4
from rdflib import Namespace, Graph, Literal, XSD
from hcsvlab_robochef.rdf.namespaces import *
 
from hcsvlab_robochef.annotations.annotation_names import NAMEMAP

def _subnode_(node, name, text, attr={}):
    """Utility fn to create a child node called 'name'
    with text content 'text' as a child of 'node'"""
    
    sn = ElementTree.Element(name)
    sn.text = str(text)
    sn.attrib = attr
    node.append(sn)
 

class AnnotationCollection:
    """All the annotations on an item"""

    
    def __init__(self, annotationList, itemid, metadataMap):
        
        self.annotations = annotationList
        self.metaMap = metadataMap
        self.itemid = itemid
        self.id = str(uuid4())   # random unique identifier
        
    
    def uri(self):
        """Return an identifier URI for this annotation collection"""
        
        return corpus_annotation_uri(self.metaMap.corpusID, self.id)
        
        
    def to_rdf(self):
        """Add RDF for all of the annotations in the collection
        in an RDF graph"""
        
        graph = Graph()
        graph = bind_graph(graph)
        
        for a in self.annotations:
            a.to_rdf(graph, self.metaMap, self.uri())
            
        graph.add((self.uri(), RDF.type, DADA.AnnotationCollection))
        graph.add((self.uri(), DADA.annotates, self.metaMap.item_uri(self.itemid)))
        
        return graph

class Annotation(DictMixin):
  """
  An annotation on a region of a source document with the position
  of the source region defined by start and end offsets.
  By default (this class) these are interpreted as UTF8 character
  offsets from the start of the file. Subclasses define alternate
  interpretations, eg. second times in an audio file.
  """
  
  uniqueid = 0

  def __init__(self, tipe, val, start, end, id=None, properties=None):
    # generate an id unless we're given one
    if id:
        self.id = str(id)
    else:
        self.id = str(Annotation.uniqueid)
        Annotation.uniqueid = Annotation.uniqueid + 1
    
    # here we map the string type onto a URI 

    if NAMEMAP.has_key(tipe):    
       self.tipe = NAMEMAP[tipe]
    else:
        raise Exception("Annotation name '%s' not in the list in annotation_names.py" % tipe )
       
    self.start = start
    self.end = end
    
    # dictionary for properties
    if properties:
        self.properties = properties
    else:
        self.properties = dict()
    # val is a special property
    if val:
        self.properties['val'] = val
    else:
        self.properties['val'] = ""

    
  # define the dictionary interface
  def __getitem__(self, key):
      return self.properties[key]
  
  def __setitem__(self, key, value):
      self.properties[key] = value
      
  def __delitem__(self, key):
      self.properties.__delitem__(key)
      
  def keys(self):
      return self.properties.keys()

  def __repr__(self):
    return (self.tipe + ': ' + self['val'] + ' ' + str(self.start) + ' -> ' + str(self.end))

  def __cmp__(self, other):
    if (cmp(self.tipe, other.tipe) == 0):
      if (cmp(self["val"], other["val"]) == 0):
        if (cmp(self.start, other.start) == 0):
          return cmp(self.end, other.end)
        else:
          return cmp(self.start, other.start)
      else:
        return cmp(self["val"], other["val"])
    else:
      return cmp(self.tipe, other.tipe)

         
  def grow(self, by):
    self.end += by

  def shrink(self, by):
    self.end -= by

  def forward(self, by):
    self.start += by
    self.end   += by

  def backwards(self, by):
    self.start -= by
    self.end   -= by

  def to_rdf(self, g, metaMap, collectionUri):
      """Add triples to this rdf graph to represent this
      annotation. Nodes go into the given namespace 
      and are part of the collectionUri"""
    
      
      # some identifiers 
      property_namespace = corpus_property_namespace(metaMap.corpusID)
      annoturi = corpus_annotation_uri(metaMap.corpusID, self.id )
      locatoruri = corpus_annotation_uri(metaMap.corpusID, self.id + "L")


      # annotation
      g.add((annoturi, RDF.type, DADA.Annotation))
      g.add((annoturi, DADA.partof, collectionUri))
      
      # locator info depends on the type of annotation
      locatoruri = self.locator_rdf(locatoruri, g)
      g.add((annoturi, DADA.targets, locatoruri))
      
      g.add((annoturi, DADA.type, self.tipe)) 
      
      for key in self.keys():
          if self[key] != '':
              if key == "speakerid":
                  g.add((annoturi, AUSNC.speakerid, metaMap.speaker_uri(self[key])))
              elif key == 'val':
                  g.add((annoturi, DADA.label, Literal(unicode(self[key])))) 
              else:
                  g.add((annoturi, property_namespace[key], Literal(unicode(self[key]))))  
      
  def locator_rdf(self, locatoruri, graph):
        """Add RDF triples to the graph to represent the locator information
        for this annotation"""
           
        graph.add((locatoruri, RDF.type, DADA.UTF8Region))
        graph.add((locatoruri, DADA.start, Literal(int(self.start), datatype=XSD.integer)))
        graph.add((locatoruri, DADA.end, Literal(int(self.end), datatype=XSD.integer)))
        
        return locatoruri



class SecondAnnotation(Annotation):
    """An annotation on a audio/video document with endpoints defined by offsets in seconds, 
    defines the serialisation of the locator"""
  
  
    def locator_rdf(self, locatoruri, graph):
        """Add RDF triples to the graph to represent the locator information
        for this annotation"""
          
        
        graph.add((locatoruri, RDF.type, DADA.SecondRegion))
        graph.add((locatoruri, DADA.start, Literal(float(self.start), datatype=XSD.float)))
        graph.add((locatoruri, DADA.end, Literal(float(self.end), datatype=XSD.float)))
        return locatoruri

class HMSAnnotation(Annotation):
    """An annotation on a audio/video document with endpoints defined by offsets in HH:MM:SS
    defines the serialisation of the locator"""
  
    def locator_rdf(self, locatoruri, graph):
        """Add RDF triples to the graph to represent the locator information
        for this annotation"""
          
        graph.add((locatoruri, RDF.type, DADA.HMSRegion))
        graph.add((locatoruri, DADA.start, Literal(self.start)))
        graph.add((locatoruri, DADA.end, Literal(self.end)))
        return locatoruri
        
