import os.path
import pyparsing
import shutil
import re
import xlrd

from hcsvlab_robochef import utils
from hcsvlab_robochef.ingest_base import IngestBase
from hcsvlab_robochef.avozes.rdf import avozesMap
from hcsvlab_robochef.annotations import *
from hcsvlab_robochef.ice.rdf import iceM
from hcsvlab_robochef.utils.serialiser import *
from hcsvlab_robochef.utils.statistics import *


class AvozesIngest(IngestBase):
  
  status = ""
  filemetadata = {}
  speakermetadata = {}
  META_DEFAULTS = {
      'created':  'August 2000',
      'language': 'eng',
  }
  conversions = { # The conversion calculator would get these wrong, so we cache the correct answers 
      'CVCWords': u'CVC Words',
      'VCVWords': u'VCV Words'
  }

  def setMetaData(self, filename):
      """
      Set the spreadsheet file from which avozes metadata is read.  This data will
      be combined with the pathnames to the documents themselves.
      """

      wb = xlrd.open_workbook(filename)
      sheet = wb.sheet_by_index(0)
      tags = map(self.__convert, sheet.row(0))

      for row in [sheet.row(i) for i in range(1, sheet.nrows)]:
#          dict = {tags[idx]:self.__convert(row[idx]) for idx in range(1, sheet.ncols)}
          speaker_id = self.__convert(row[0])
          self.speakermetadata[speaker_id] = {
              u'table_person_' + speaker_id: {
                  tags[idx]:self.__convert(row[idx]) for idx in range(0, sheet.ncols)
              }
          }


  def ingestCorpus(self, srcdir, outdir):

      print "  converting corpus", srcdir, "into normalised data in ", outdir
      print "    clearing and creating output location"
      
      self.clear_output_dir(outdir)

      print "    processing files..."

      #dirs = os.walk(srcdir)
      items = self.findItems(srcdir)
      total = len(items)

      sofar = 0
      for item_name, directory, speaker, module, sequence, source_list in items:
          self.status = "DOC:" + os.path.join(directory, item_name)
          self.__serialise(outdir, item_name, module, sequence, speaker, source_list)
          sofar += 1
          print "   ", sofar, "of", total, self.status

      print "   ", total, " Items processed"


  def findItems(self, directory):
      directory = os.path.normpath(directory) + "/" # make sure there's a slash on the end

      items = []

      for root, dirs, files in os.walk(directory, followlinks=True):
          if len(files) >= 2:
              breadcrumbs = root.replace(directory, "", 1).split('/')
              self.checkForItems(root, files, breadcrumbs, items)

      return items


  def checkForItems(self, directory, files, breadcrumbs, collect_items):
      avis = set()
      wavs = set()

      for file in files:
          root, ext = os.path.splitext(file)
          if ext == ".avi":
              avis.add(root)
          elif ext == ".wav":
              wavs.add(root)

      items = avis & wavs
      for item in items:
          full_wav = os.path.join(directory, item) + ".wav"
          full_avi = os.path.join(directory, item) + ".avi"
          collect_items.append(self.recordItem(directory, item, breadcrumbs, full_wav, full_avi))


  def recordItem(self, directory, item_name, breadcrumbs, audio_file = None, video_file = None):
      if len(breadcrumbs) > 0:
          speaker = self.__convert_label(breadcrumbs.pop(0))
      else:
          speaker = ""
      if len(breadcrumbs) > 0:
          module = self.__convert_label(breadcrumbs.pop(0))
      else:
          module = ""
      sequence = map(self.__convert_label, breadcrumbs)
      source_list = []
      if not audio_file is None:
          source_list.append({'filetype': 'Audio', 'sourcepath': audio_file})
      if not video_file is None:
          source_list.append({'filetype': 'Video', 'sourcepath': video_file})

      return (item_name, directory, speaker, module, sequence, source_list)

  def ingestDocument(sourcepath):
      '''
      Ingest a specific source document, from which meta-data annotations and raw data is produced
      '''
      print "Error: calling unsupported operation - ingestDocument(" + sourcepath + ")"
      return None


  def __serialise(self, outdir, sampleid, module, sequence, speakerid, source_list):
      '''
      Function serialises the graphs to disc and returns the object graph to the caller
      '''
      serialiser = Serialiser(outdir)
  
      '''
      This function takes the source list of document and a dictionary of meta information and
      annotations and outputs rdf graphs.
      '''
      return serialiser.serialise_multiple(sampleid, source_list, 'avozes', avozesMap, self.__fileMetadata(sampleid, module, sequence, speakerid, self.speakermetadata), [])


  def __fileMetadata(self, sampleid, module, sequence, speakerid, speakermetadata):
      '''
      Fabricate the metadata for the given sampleid from two sources: the speakermetadata
      previously read in from the spreadsheet and the known properties of the AVOZES corpus
      '''
      result = {}
      result.update(self.META_DEFAULTS)
      result['sampleid'] = sampleid
      result['genre'] = 'Test'
      if speakerid != '':
          result.update(speakermetadata[speakerid])
      if module != '':
          result['module'] = module
      if sequence != '':
          result['sequence'] = " ".join(sequence)
      return result


  def __extractAnnotations(self, data):
      """
      Return the annotations for this document. In the case of Avozes we're assuming there are none.
      """
      return ("",[])


  def __convert_label(self, label):
      '''
      Given a camel case label, convert it to title case. Maintain a cache of
      conversions to save us repeating calculation. The cache also allows us
      to have some non-standard cases, e.g. CVCWords -> CVC Words.
      '''
      if not label in self.conversions:
          self.conversions[label] = self.__calculate_conversion(label)
      return self.conversions[label]


  def __calculate_conversion(self, label):
      '''
      Convert something like "BlahDeBlah" to "Blah De Blah"
      '''
      result = u""
      out = 0
      for c in label:
          if out == 0:
              result += c
          elif c.isupper():
              result += " " + c
          else:
              result += c
          out += 1
      return result


  def __convert(self, cell):
    ''' There are no float values in the Excel sheet. Cut hem here to int before converting to unicode. '''
    if cell.ctype in (2, 3, 4):
        return unicode(int(cell.value))
    return cell.value
