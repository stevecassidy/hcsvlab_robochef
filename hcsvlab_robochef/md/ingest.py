import codecs
import csv
import re
import xlrd
import os.path
import shutil

from hcsvlab_robochef import utils
from hcsvlab_robochef.ingest_base import IngestBase
from hcsvlab_robochef.annotations.annotation import *
from hcsvlab_robochef.utils.filehandler import *
from hcsvlab_robochef.utils.serialiser import *
from hcsvlab_robochef.utils.statistics import *
from hcsvlab_robochef.utils.parsing import *
from hcsvlab_robochef.md.textgrid import TextGrid


from rdf import mdMap #, annotation_rdf
from pyparsing import *
from copy import deepcopy

class MDIngest(IngestBase):
  
  filemetadata = {}
  META_DEFAULTS = {'language': 'eng',
                   }

  def setMetaData(self, filepath):
    '''
    Function processes the flat file to extract the meta data for the MD source files
    '''
    f = codecs.open(filepath, encoding='latin-1')
    
    for line in f:
        row = line.split("#")
        self.filemetadata[row[0]] = {
          'table_uid': unicode(row[0]),
          'table_state': unicode(row[1]),
          'table_place': unicode(row[2]),
          'table_institute': unicode(row[3]),
          'table_date_of_recording': unicode(row[4]),
          'table_tsid': unicode(row[5]),
          'table_sex': unicode(row[6]),
          'table_place_of_birth': unicode(row[7]),
          'table_fathers_place_of_birth': unicode(row[8]),
          'table_fathers_occupations': unicode(row[9]),
          'table_mothers_place_of_birth': unicode(row[10]),
          'table_misc': unicode(row[10]),
          'table_recording_environment': unicode(row[11])
        }


  def ingestCorpus(self, srcdir, outdir):

    print "  converting corpus in", srcdir, "into normalised data in", outdir
    print "    clearing and creating output location"
    
    self.clear_output_dir(outdir)
  
    print "    processing files..."
  
    # Get the list of source files which we will use as our base for extracting meta data
    file_handler = FileHandler()
    files = file_handler.getFiles(srcdir, '^\w+\.wav$', '^.DS_Store$') # DS_Store Required for macs
  
    total = len(files.keys())
    sofar = 0
  
    for name, path in files.iteritems():
      print sofar, " of ", total, "\033[A"
      self.ingestDocument(name, path, outdir)    
      sofar += 1
    
    print "\033[2K   ", total, "files processed"
  

  def ingestDocument(self, name, sourcepath, outdir):
    ''' Try and locate meta data for this particular document '''
  
    sampleid = self.__extract_sampleid(name)
    meta_dict = self.__extract_metadata(sampleid, sourcepath)
    
    meta_dict.update(self.META_DEFAULTS)
    
    (rawtext, meta, body, annotations) = ("", meta_dict, "", [])
    meta['sampleid'] = os.path.splitext(name)[0]
    
    sourcefiles = [{'filetype': 'Audio', 'sourcepath': sourcepath}]
    # locate any TextGrid file and add to documents list
    tgfile = self.__get_annotation_file_path(name, sourcepath, '.TextGrid')
    if tgfile != None:
        sourcefiles.append({'filetype': 'TextGrid', 'sourcepath': tgfile})
    
    metagraph = mdMap.mapdict(meta, self.identify_documents)
  
    # s1, s2 and s3 are read, n is interview
    if sampleid.endswith('n'):
        meta['genre'] = 'interview'
    else:
        meta['genre'] = 'read'
  
    file_name = os.path.splitext(name)[0]
    anns = self.__get_annotations(name, sourcepath)
  
    self.__generate_participant_info(meta)
  
    serialiser = Serialiser(outdir)
    serialiser.serialise_multiple(file_name, sourcefiles, 'md', mdMap, meta, anns, self.identify_documents)
    

  def identify_documents(self, documents):
    # should only be one Audio and one TextGrid document, Audio is the display document
    for doc in documents:
      if doc['filetype'] == 'Audio':
        return (None, doc['uri'])
    return (None, None)
    

  def __generate_participant_info(self, participant):
    '''
    This function extracts the participant information from the meta data and
    generates the appropriate nested table
    '''
    info = {'id': participant.get('sampleid', ''),
            'birthplace': participant.get('table_place_of_birth', ''),
            'state': participant.get('table_state', ''),
            'fathers_birthplace': participant.get('table_fathers_place_of_birth', ''),
            'fathers_occupation': participant.get('table_fathers_occupations', ''),         
            'mothers_birthplace': participant.get('table_mothers_place_of_birth', ''),
            'gender': participant.get('table_sex', '')
            }
  	  
    participant['table_person_main'] = info
    participant.update(participant)


  def __get_annotations(self, file_name, full_path):
    ''' 
    This function returns the annotations for the a source wav file. Annotations can be located
    in flab, fword and word files. All of these file types are processed for annotations. If however
    there is both a word and fword file the word file takes precedence as the datasets overlap.
    '''
    anns = []

    tgfile = self.__get_annotation_file_path(file_name, full_path, '.TextGrid')
 
    if tgfile != None:
        tg = TextGrid.load(tgfile)
        
        for i, tier in enumerate(tg):
            # generate annotations for this tier
            
            for row in tier.simple_transcript:
                (start, end, label) = row
                if label == "":
                    label = "#"
                anns.append(SecondAnnotation(tier.nameid, label, start, end))
                #print tier.nameid, label, start, end
            
    return anns


  def __get_annotation_file_path(self, file_name, full_path, extension):
    '''
    This function returns the name of an annotation file if one exists
    for the particular source file. So for example if the wav file is named
    S1200.wav and we pass in the extension .flab, then if S1200.flab exist
    this function returns the absolute path to this file.
    '''
    dir_name = os.path.dirname(full_path)
    ann_file_name = os.path.splitext(file_name)[0] + extension

    if os.path.exists(os.path.join(dir_name, ann_file_name)):
      return os.path.join(dir_name, ann_file_name)
    else:
      return None



  def __extract_metadata(self, sampleid, current_path):
    ''' 
    Check to see if the flat file has meta data firstly, if so grab that. Then check to see if
    there is other meta data such as the meta data in the fwlab, fword and flab files.
    '''

    meta_instance = {}

    if sampleid in self.filemetadata:
      meta_instance = deepcopy(self.filemetadata[sampleid])

    return meta_instance


  def __extract_sampleid(self, name):
    ''' Extracts the sample identifier from the file name. The assumption is that sample ids are 4 digit numbers. '''

    match = re.findall('\d{4}', name) # The sample id is a 4 digit number

    if len(match) > 0:
      return match[0]
    else:
      return None