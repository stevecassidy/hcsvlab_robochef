import os
import shutil
import re
import xml.dom
import codecs

from hcsvlab_robochef.ingest_base import IngestBase
from hcsvlab_robochef.ingest_exception import IngestException
from hcsvlab_robochef import utils
from hcsvlab_robochef import metadata
from hcsvlab_robochef.annotations import *
from hcsvlab_robochef.utils.serialiser import *
from hcsvlab_robochef.utils.statistics import *
from hcsvlab_robochef.utils.filehandler import *

from xml.dom.minidom import parse, parseString
from xml.dom import Node
from xml.etree import ElementTree as et

from rdf import auslitMap


class AuslitIngest(IngestBase):

  META_DEFAULTS = {'language': 'eng'}

  def setMetaData(self, srcdir):
    ''' Loads the meta data for use during ingest '''
    pass
    
    
  def ingestCorpus(self, srcdir, outdir):
    ''' This function will initiate the ingest process for the Auslit corpus '''
    
    print "  converting corpus in", srcdir, "into normalised data in", outdir
    print "    clearing and creating output location"
  
    self.clear_output_dir(outdir)

    print "    processing files..."
  
    files_to_process = self.__get_files(srcdir)
    total = len(files_to_process)
    sofar = 0
  
    for f in files_to_process:
      (rawtext, meta, body, annotations) = self.ingestDocument(srcdir, f)
      source_file = f
      f = f.replace(srcdir, outdir, 1)
      try:
        os.makedirs(os.path.dirname(f))
      except:
        pass
    
      ff = os.path.splitext(os.path.abspath(f))[0]

      serialiser = Serialiser(os.path.dirname(ff))
      serialiser.serialise_single(os.path.basename(ff), 'auslit', rawtext, body, auslitMap, meta, annotations, self.identify_documents, source_file)
    
      sofar = sofar + 1
      print "\033[2K   ", sofar, "of", total, f, "\033[A"
      
    print "\033[2K   ", total, "files processed"


  def ingestDocument(self, srcdir, sourcepath):
    """ Read and process a corpus document """
    res = {}
  
    (text, xml_tree) = self.__load_xml_tree(sourcepath)
  
    meta = xml_tree.findall("teiHeader")
    if (len(meta) != 1):
      raise Exception("wrong number (" + str(len(meta)) + ") of teiHeader tags")
    
    meta = metadata.xml2dict(meta[0], ignore_root=True)
    ident = os.path.splitext(os.path.basename(sourcepath))[0]
    meta['sampleid'] = ident
    meta.update(self.META_DEFAULTS)
    
    # Check to see if there is some additional meta data, if so grab some fields from there    
    (meta_text, meta_tree) = self.__get_meta_tree(srcdir, os.path.basename(sourcepath))
    if meta_tree is not None:
      collection_elem = meta_tree.find('{http://austlit.edu.au/fulltext-metadata}collection')
      if collection_elem is not None:
        meta['collection'] = collection_elem.text
  
  
    raw = xml_tree.findall("text")
    if (len(raw) != 1):
      raise Exception("wrong number (" + str(len(raw)) + ") of text tags")
  
    cleansed_text = self.__cleanse_text(et.tostring(raw[0]).encode("utf-8"))
  
    return (text, self.__cleanse_meta(meta), cleansed_text, [])

  def identify_documents(self, documents):
    for doc in documents:
      if doc['filetype'] == 'Text':
        return (doc['uri'], doc['uri'])
    return (None, None)

  def __cleanse_text(self, raw_text):
    '''
    This function performs some further cleansing on the input text. As the text is XML it proceeds to just filter out
    some of the XML tags.
    '''
    return re.sub(r'<.*?>', ' ', raw_text) # Is this all I need to do?
  
  
  def __cleanse_meta(self, meta_dict):
    ''' 
    This function cleanses the dictionary by renaming keys and ommitting certain keys. IMPORTANT: I have chosen to remove
    keys as opposed to adding because we DO NOT want to miss additional keys that may appear when we receive the full data set.
    This approach helps pick up missing keys as it becomes apparent on close scrutiny of the RDF document.
    '''
      
    # These fields are ommitted
    lookup = ('encodingDesc_editorialDecl_p', 'fileDesc_extent', 'fileDesc_publicationStmt_availability_p', 'fileDesc_publicationStmt_availability', 'fileDesc_publicationStmt_idno', 'fileDesc_titleStmt_funder', 'fileDesc_titleStmt_respStmt_name', 'fileDesc_titleStmt_respStmt_resp', 'fileDesc_publicationStmt_date', 'profileDesc_textClass_classCode', 'profileDesc_textClass_keywords_term', 'fileDesc_sourceDesc_bibl_author', 'fileDesc_sourceDesc_bibl_imprint_date', 'fileDesc_sourceDesc_bibl_title', 'fileDesc_titleStmt_title+', 'fileDesc_sourceDesc_p', 'profileDesc_particDesc_person_p', 'fileDesc_publicationStmt_availability_p_hi', 'revisionDesc_change_item', 'revisionDesc_change_respStmt_resp', 'revisionDesc_change_date', 'revisionDesc_change_respStmt_name', 'fileDesc_titleStmt_editor', 'fileDesc_titleStmt_author+')

    # These are the supported fields
    supported_fields = ('language', 'fileDesc_publicationStmt_date', 'fileDesc_publicationStmt_pubPlace', 'fileDesc_publicationStmt_publisher', 'fileDesc_sourceDesc_p',    'fileDesc_titleStmt_author_name', 'fileDesc_titleStmt_title', 'profileDesc_creation_date', 'sampleid', 'fileDesc_sourceDesc_bibl_imprint_biblScope', 'fileDesc_profileDesc_creation_date', 'fileDesc_titleStmt_author', 'profileDesc_langUsage_language', 'collection')

    # Remove the superfluous keys from the dictionary
    for item in lookup:
      augmented_item = item + '+'
      if item in meta_dict:
        del meta_dict[item]
      if augmented_item in meta_dict:
        del meta_dict[augmented_item]
       
    # Check to make sure we have not missed a field if so throw an exception
    for key, value in meta_dict.items():
      if not key in supported_fields:
        raise IngestException('Unsupported field ' + key + ' with value ' + value)


    # I am returning a copy as the caller may want to hold onto the original
    return meta_dict.copy()


  def __get_files(self, srcdir):
    ''' This function retrieves a list of files that the Auslit ingest should actually process '''
    filehandler = FileHandler()
    
    # We have been told that we cannot process CLDR00038, brn446711, clahisn, CLDR00033, vn28178, vn98351
    # files at present
    files = filehandler.getFiles(srcdir, r'^[\w\d]+\.xml$', r'^(CLDR00038|brn446711|clahisn|CLDR00033|vn28178|vn98351).xml$')
    return_files = []
    
    # For each file check it's alm.xml file to see if it qualifies for ingesting
    for document in files:
      (org_text, org_xml) = self.__get_meta_tree(srcdir, document)
      if org_xml is not None and self.__is_includable(org_xml):
        return_files.append(os.path.join(srcdir, document))
      else:
        return_files.append(os.path.join(srcdir, document))
    
    return return_files
    
  
  def __get_meta_tree(self, srcdir, source):
    '''
    This function when given a source document to ingest will find the corresponding meta
    file if one exists and returns it as a XML document
    '''
    document = os.path.basename(source)
    meta_file_name = self.__get_alm_file_name(document)
    meta_path = os.path.join(srcdir, meta_file_name)
    
    if os.path.exists(meta_path):
      return self.__load_xml_tree(meta_path)
    
    return (None, None)


  def __is_includable(self, xml_tree):
    '''
    This function tests to see if the corresponding Auslit document can be included in the ingest
    '''
    date_elem = xml_tree.find('{http://austlit.edu.au/fulltext-metadata}date')
    if date_elem is not None:
      if int(date_elem.text) > 1954:
        return False
          
    collection_elem = xml_tree.find('{http://austlit.edu.au/fulltext-metadata}collection')
    if collection_elem is not None:
      if collection_elem.text == "Children's Literature Resources":
          return False
        
    return True


  def __get_alm_file_name(self, file_name):
    '''
    This function returns the name of the compatriot meta data file for the AusLit corpus
    '''
    return os.path.splitext(file_name)[0] + '.alm.xml'
    
    
  def __load_xml_tree(self, sourcepath):
    '''
    This function reads in a XML docment as a text file and converts it into
    an XML tree for further processing
    '''
    
    fhandle = codecs.open(sourcepath, "r", "utf-8")
    text = fhandle.read()
    fhandle.close()
  
    text = text.replace('&ndash;', u"\u2013")
    text = text.replace('&mdash;', u"\u2014")
    text = text.replace('&copy;', u"\u00A9")
    text = text.replace('&ldquo;', u"\u201C")
    text = text.replace('&rdquo;', u"\u201D")
    text = text.replace('&emsp;', u"\u2003")
    text = text.replace('&eacute;', u"\u00E9")
    text = text.replace('&lsquo;', u"\u2018")
    text = text.replace('&rsquo;', u"\u2019")
    text = text.replace('&ecirc;', u"\u00EA")
    text = text.replace('&agrave;', u"\u00E0")
    text = text.replace('&egrave;', u"\u00E8")
    text = text.replace('&oelig;', u"\u0153")
    text = text.replace('&aelig;', u"\u00E6")
    text = text.replace('&hellip;', u"\u2026")
  
    return (text, et.fromstring(text.encode("utf-8")))