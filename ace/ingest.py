import os
import shutil
import re
import xml.dom
import copy

from ausnc_ingest import utils
from ausnc_ingest import metadata
from ausnc_ingest.ingest_base import IngestBase
from ausnc_ingest.annotations import *
from ausnc_ingest.utils.filehandler import *
from ausnc_ingest.utils.parsing import *
from ausnc_ingest.utils.serialiser import *
from ausnc_ingest.utils.statistics import *
from ausnc_ingest.ace.html_parser import *

from rdf import aceMap
from xml.dom.minidom import parse, parseString
from xml.dom import Node


class ACEIngest(IngestBase):

  filemetadata = {}
  status  = ""

  
  def setMetaData(self, srcdir):
    '''
    This method uses the AceHTMLParser to extract the meta data for the Ace corpus. This meta data is stored
    in a dictionary which is later used by the ingest function.
    '''  
    fileHandler = FileHandler()

    # KATLS.HTM appears to be a duplicate file, this file is in the incorrect format.
    # Plus on the Mac we get those Finder .DS_Store files which also need to be ignored.
    rs = fileHandler.getFiles(srcdir, inclusionPredicate = '^KAT\w+\.HTM$', exclusionPredicate = '^KATLS.HTM$|^.DS_Store$') 
     
    # Extract the meta data for each file in the list
    for key, value in rs.iteritems():
    
      parser = AceHTMLParser()
      file_handle = open(value, 'r')
      input_str = file_handle.read()
    
      parser.feed(unicode(input_str))  
      self.filemetadata = merge_dictionaries(parser.get_meta(), self.filemetadata)
  
  
  def ingestCorpus(self, srcdir, outdir):
  
    print "  converting corpus in", srcdir, "into normalised data in", outdir
    print "    clearing and creating output location"
  
    self.clear_output_dir(outdir)

    print "    processing files..."
  
    rs = []
  
    # Input collection may contain accompanying documentation, this needs to be ignored.
    utils.listFiles(rs, srcdir, True, ['Manual', '.DS_Store'])
  
    total = len(rs)
    sofar = 0

    serialiser = Serialiser(outdir)

    for f in rs:

      samples = self.ingestDocument(f)
          
      for s in samples:
        (rawtext, meta, text, anns) = samples[s]
      
        # update this meta data by grabbing the equivalent key items from
        # the global meta data file
        if meta['sampleid'] in self.filemetadata:
          for key, value in meta.iteritems():
            if not key.capitalize() in self.filemetadata[meta['sampleid']]:
              self.filemetadata[meta['sampleid']][key] = value
        
          serialiser.serialise_single(s, 'ace', rawtext, text, aceMap, self.filemetadata[meta['sampleid']], anns, f) 
        
        else:
          serialiser.serialise_single(s, 'ace', rawtext, text, aceMap, meta, anns, f)
        
      sofar = sofar + 1
      print "\033[2K   ", sofar, "of", total, self.status, "\033[A"
    
    print "\033[2K   ", total, "files processed"


  def ingestDocument(self, sourcepath):
      """Read and process a corpus document,  writing out raw text and XML metadata"""

      res = {}

      # read the document and parse as xml
      import codecs
      fhandle = codecs.open(sourcepath, "r", "utf-8")
    
      # print 'About to read document: ', sourcepath
      text = fhandle.read()
      fhandle.close()
    
      text = utils.replaceEntitiesInStr(text)
    
      # files generally don't have a root node.  However, they sometimes have one (called section) and sometimes
      # have just one of the tags for the root node.  So we fix this.
      stringWithRoot = text
      if (text.find(u'<section>') < 0):
        stringWithRoot = u'<section>' + stringWithRoot
      if (text.rfind(u'</section>') < 0):
        print "adding </section>"
        stringWithRoot = stringWithRoot + u'</section>'
    
      h = open("last_processed_file", 'w')

      h.write(stringWithRoot.encode("utf-8"))
      h.close()
      h = open("/tmp/sample_"+os.path.basename(sourcepath), 'w')
      h.write(stringWithRoot.encode("utf-8"))
      h.close()
    
      doc = parseString((stringWithRoot).encode("utf-8"))
    
      # Loop through sample elements
      samples = doc.documentElement.getElementsByTagName('sample')
      for sample in samples:
          res.update(self.__ingestSample(sample))
      return res


  def __ingestSample(self, sample):
      """ Process a single sample from within a corpus document. May be made of subsamples, which are processed independantly. """

      res = {}

      # Check whether subsamples exist (in which case just use those)
      subs = sample.getElementsByTagName('subsample')
      if len(subs) != 0:
          # Loop through subsamples and process as if they were samples
          for sub in subs:
              res.update(self.__ingestSample(sub))
      else: 
          # Fetch the sample id and source
          id = self.__get_element_content(sample, 'id')
          genre = id[0]
          source = self.__get_element_content(sample, 'source')
          if source == "":
              source = "Unknown"
    
          self.status =  "id: %s source: %s, genre: %s" % (id, source, genre)
    
          content = []
          for node in sample.childNodes:
            h = open("/tmp/node"+id, 'a')
            h.write('------')
            h.write(self.__nodeText(node).encode("utf-8"))
            h.close()
            content.append(self.__nodeText(node))
        
          content = u' '.join(content) 

          h = open("/tmp/"+id, 'w')
          h.write(content.encode("utf-8"))
          h.close()
          content,anns = self.__extractAnnotations(content)
        
          res[id] = (sample.toprettyxml(), {u'sampleid': id, u'genre': genre, u'source': source}, content, anns)
      return res


  def __extractAnnotations(self, data):
      """
      From the text with no meta-data, extract all the annotations and return the text
      free of these annotations along with the list of annotations found
      """
      import pyparsing
    
      if data == "":
        return ("",[])
      
      # 17/01/2012 SP: ^ Is used to Or the expressions together, this effectively matches the longest possible 
      # string in the input data for the given parsers
      parser = pyparsing.OneOrMore( slurpParser('*<+')                       \
                                  ^ aceCorrectionParser()                    \
                                  ^ markupParser("h", "heading")          \
                                  ^ markupParser("misc", "misc")          \
                                  ^ markupParser("list", "extended list") \
                                  ^ markupParser("note", "note")          \
                                  ^ markupParser("bl", "by line")         \
                                  ^ exactParser("<")                      \
                                  ^ pyparsing.Literal("+").setParseAction(lambda s, loc, toks: AnnotatedText('', [Annotation('special character', 'linebreak', 0,0)])) \
                                  ) .setParseAction(lambda s, loc, toks: concatAnnotatedText(self.__transposeCorrections(toks)))
                
      # 17/01/2012 SP: At the moment parseException is supressed because the second argument is False by default
      # Going forward we may want to set this to true         
      res = parser.parseString(data)
    
      return (res[0].text, res[0].anns)


  def __transposeCorrections(self, toks):
      """The ace correction parser can't see the text infront of the correction and this is the text we want in the correction
      position, so we swap them around (we only look back until a space)
      """
      if (len(toks) < 1):
        return toks
      for i in range(1, len(toks)):
        if ((len(toks[i].anns) > 0) and (toks[i].anns[0].tipe == 'correction')):
          anncapt = toks[i].anns[0]['val']
          original_pre = ""
          original = toks[i-1].text
          original_parts = original.rsplit(" ", 1)
          if (len(original_parts) == 2):
            original_pre = original_parts[0] + " "
            original = original_parts[1]
          else:
            original = original_parts[0]
          # reset to desired values
          toks[i-1].text = original_pre + anncapt
          new_ann = copy.deepcopy(toks[i].anns[0])
          new_ann["val"] = original
          toks[i].anns[0] = new_ann
      return toks


  def __get_element_content(self, node, tagname):
      """Return the textual content of the element
      with the given tag name inside node.
      Return the empty string if not found."""
    
      nodes = node.getElementsByTagName(tagname)
      if len(nodes) != 0:
        if nodes[0].hasChildNodes():
          return nodes[0].firstChild.nodeValue.strip()
    
      return ''


  def __nodeText(self, node):
      """Return the text in this node with
      any markup that is not one of 'id' 'source' or 'note'"""
    
      if node.nodeType == node.TEXT_NODE:
          return node.nodeValue
      elif node.nodeType == node.ELEMENT_NODE:
          result = u""
          if node.tagName not in ('id', 'source', 'note'):
              result += u'<' + node.tagName + u'>'
              for n in node.childNodes:
                result += self.__nodeText(n)
              
              result += u'</' + node.tagName + u'>'
    
      return result
