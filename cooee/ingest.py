import os.path
import pyparsing
import shutil
import re
import xlrd

from hcsvlab_robochef import utils
from hcsvlab_robochef.ingest_base import IngestBase
from hcsvlab_robochef.cooee.rdf import cooeeMap
from hcsvlab_robochef.annotations import *
# from hcsvlab_robochef.ice.rdf import iceM
from hcsvlab_robochef.utils.serialiser import *
from hcsvlab_robochef.utils.statistics import *


class CooeeIngest(IngestBase):
  
  status = ""
  filemetadata = {}
  META_DEFAULTS = {'language': 'eng'}

  def __init__(self):
    super(CooeeIngest, self).__init__('COOEE')

  def setMetaData(self, filename):
      """
      Set the csv file from which cooee metadata is read.  This data will
      be combined with whatever is found in the documents themselves.
      """

      wb = xlrd.open_workbook(filename)
      sheet = wb.sheet_by_index(0)
      for row in [sheet.row(i) for i in range(2, sheet.nrows)]:
          self.filemetadata[self.__convert(row[0])] = {
              u'table_person_A' : {
                u'role': u'author',
                u'id': self.__convert(row[0])+u"author",
                u'name': self.__convert(row[1]),
                u'birth': self.__convert(row[2]),
                u'gender': self.__convert(row[3]),
                u'origin': self.__convert(row[4]),
                u'age': self.__convert(row[5]),
                u'status': self.__convert(row[6]),
                u'arrival': self.__convert(row[7]),
                u'abode': self.__convert(row[8])
              },
              u'table_text_year_of_writing': self.__convert(row[9]),
              u'table_text_place_of_writing': self.__convert(row[10]),
              u'table_text_register': self.__convert(row[11]),
              u'table_text_type': self.__convert(row[12]),
              u'table_text_number_of_words': self.__convert(row[13]),
              u'table_person_B': {
                u'role': u'addressee',
                u'id': self.__convert(row[0])+u"addressee",
                u'gender': self.__convert(row[14]),
                u'status': self.__convert(row[15]),
                u'place': self.__convert(row[16])
              },
              u'table_source': self.__convert(row[17]),
              u'table_pages': self.__convert(row[18]),
            }


  def ingestCorpus(self, srcdir, outdir):

      print "  converting corpus", srcdir, "into normalised data in ", outdir
      print "    clearing and creating output location"
      
      self.clear_output_dir(outdir)

      print "    processing files..."
      
      sofar = 0
      files = filter(lambda x: os.path.isfile(os.path.join(srcdir, x)), os.listdir(srcdir))
    
      total = len(files)
      
      for f in files:
          
          (sampleid, rawtext, body, meta, anns) = self.ingestDocument(os.path.join(srcdir, f))
          meta.update(self.META_DEFAULTS)
          self.check_filesize_ratio(body, rawtext, f)
          self.__serialise(outdir, sampleid, rawtext, body, meta, anns, os.path.join(srcdir, f))
        
          sofar = sofar + 1
          print "\033[2K   ", sofar, "of", total, self.status, "\033[A"
          
      print "\033[2K   ", total, "files processed"


  # function by Steve Cassidy
  def ingestDocument(self, sourcepath):

      """Parse and index a document from the COOEE corpus

      Document format is:

      <source>...various <xmlish> tags
      ...document text...
      <\\xmlish end tags>

      we get the source document and grab various attributes from
      the xmlish tags.

      Then the raw text and an XML metadata file are written, these can
      then be indexed by the AusNC code.

      If a call has previously been make to setMetaData, that data file
      is combined with what we find in the document, with data
      from the meta-data file taking precedence.

      """
      self.status = "DOC:", sourcepath

      import codecs
      fhandle = codecs.open(sourcepath, "r", "iso8859")
      text = fhandle.read()
      fhandle.close()

      # this pattern will find opending "tags" and will build up a group
      # dictionary of normalised names for the tags. so g is gender for example
      opat = re.compile(
          r'<source><g=(?P<item_gender>[mf])><o=(?P<item_o>.)>'
          r'<age=(?P<item_age>[0-9un]+)><status=(?P<item_status>[1234])>'
          r'<abode=(?P<item_abode>[0-9unv]+)><p=(?P<item_place>[a-z]+)>'
          r'<r=(?P<item_register>[a-z]+)><tt=(?P<item_texttype>..)>'
          r'<(?P<sampleid>.*)>'
        )

      #<source><g=m><o=a><age=31><status=2><abode=nv><p=nsw><r=pcw><tt=nb><3-170>

      cpat = re.compile(r'<\\')

      content = []
    
      for line in text.split('\n'):
        
          o = opat.match(line)
          c = cpat.match(line)

          if o:
              meta_almost = o.groupdict()
              meta = {'sampleid': meta_almost['sampleid'], 'table_person_A':{'id':meta_almost["sampleid"]+"author"}}
              meta['table_person_A']['gender'] = meta_almost['item_gender']
              meta['table_person_A']['age'] = meta_almost['item_age']
              meta['table_person_A']['status'] = meta_almost['item_status']
              meta['table_person_A']['abode'] = meta_almost['item_abode'].lstrip("0")
              meta['table_text_place_of_writing'] = meta_almost['item_place']
              meta['table_text_register'] = meta_almost['item_register']
              meta['table_text_type'] = meta_almost['item_texttype']
          elif c:
              finaltext = u'\n'.join(content)
              finaltext,anns = self.__extractAnnotations(finaltext)
              # pull in the metadata from the metadata file (if we can find it)
              if (meta['sampleid'] in self.filemetadata):
                  # the update assures that anything from the metadata file overrides what is in the document file
                  meta.update(self.filemetadata[meta['sampleid']])

              return (meta['sampleid'], text, finaltext, meta, anns)
          else:
              content.append(line)
              
      # if we get here we've failed to parse the file
      raise Exception("Failed to parse file %s, content '%s'" % (sourcepath, content))


  def __serialise(self, outdir, sampleid, rawtext, body, meta, anns, source_file):
    '''
    Function serialises the graphs to disc and returns the object graph to the caller
    '''
    serialiser = Serialiser(outdir)
    return serialiser.serialise_single(sampleid, 'cooee', rawtext, body, cooeeMap, meta, anns, source_file)


  def __extractAnnotations(self, data):
      """
      From the text with no meta-data, extract all the annotations and return the text
      free of these annotations along with the list of annotations found
      """
      if data == "":
        return ("",[])
        
      parser = pyparsing.OneOrMore( slurpParser('[')                       \
                                  ^ cooeeParagraphParser()                    \
                                  ) .setParseAction(lambda s, loc, toks: concatAnnotatedText(toks))
      res = parser.parseString(data)
      return (res[0].text, res[0].anns)


  def __convert(self, cell):
    ''' There are no float values in the Excel sheet. Cut hem here to int before converting to unicode. '''
    if cell.ctype in (2, 3, 4):
        return unicode(int(cell.value))
    return cell.value
