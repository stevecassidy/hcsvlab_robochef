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

from rdf import mdMap #, annotation_rdf
from pyparsing import *
from copy import deepcopy

class MDIngest(IngestBase):
  
  filemetadata = {}
  META_DEFAULTS = {'language': 'eng'}

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
    metagraph = mdMap.mapdict(meta)
  
    # all samples are interviews
    meta['genre'] = 'interview'
  
    file_name = os.path.splitext(name)[0]
    anns = self.__get_annotations(name, sourcepath)
  
    self.__generate_participant_info(meta)
  
    serialiser = Serialiser(outdir)
    serialiser.serialise_single_nontext(file_name, 'md', sourcepath, 'Audio', mdMap, meta, anns)
    

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

    flab = self.__get_annotation_file_path(file_name, full_path, '.flab')
    if flab:
      anns = self.__parse_annotation('phonetic', flab)
  
    # Word files are more accurate than fword files, so in the event
    # both exist favour the word file
    word = self.__get_annotation_file_path(file_name, full_path, '.word')
    if word == None:
      word = self.__get_annotation_file_path(file_name, full_path, '.fword')
  
    # If there are annotations for words then add them to the collection
    if word:  
      word_anns = self.__parse_annotation('words', word)
      for word_ann in word_anns:
        anns.append(word_ann)
 
    
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


  def __parse_annotation(self, tipe, file_path):
    '''
    This function extracts the annotation information from the audio annotation files
    This function is generic and can work on the flab, fword and word files as they
    all share a similar enough format.
    '''
    annotations_found = False
    phonemes = []
    anns = []

    # Check to see if the flab file exists
    if os.path.exists(file_path):
      f = codecs.open(file_path, encoding='latin-1')

      for line in f:    
        if annotations_found:
          time = re.findall(r'[0-9]*\.?[0-9]+', line)
          if len(phonemes) > 0:
            phoneme = re.findall(r'[\w:#\+]+\n', line)
            phonemes[len(phonemes)-1] =  merge_dictionaries(phonemes[len(phonemes)-1], {'end': time[0], 'word': phoneme[0].rstrip()})
      
          phonemes.append({'start': time[0]})
     
        match = re.search('^#\w*$', line)
    
        if match:
          annotations_found = True
  
      # Because of the way I parse and the nature of the file I need to remove the last two entries from the list
      phonemes.pop()
      phonemes.pop()
  
      for item in phonemes:
        if not item['word'] in ('#','B','+'):
          anns.append(SecondAnnotation(tipe, item['word'], item['start'], item['end']))
  
      return anns
  
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