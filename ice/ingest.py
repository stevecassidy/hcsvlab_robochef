import codecs
import datetime
import xlrd
import os.path
import shutil
import re

from pyparsing import *
from hcsvlab_robochef import utils
from hcsvlab_robochef.ingest_base import IngestBase
from hcsvlab_robochef.annotations import *
from hcsvlab_robochef.utils.serialiser import *
from hcsvlab_robochef.utils.statistics import *
from hcsvlab_robochef.rdf.map import FieldMapper

from rdf import iceM
from xml.etree import ElementTree
  
class ICEIngest(IngestBase):
  
  filemetadata = {}
  book_date_mode = 0
  META_DEFAULTS = {'language': 'eng'}

  def __init__(self):
    super(ICEIngest, self).__init__('ICE')

  def ingest(self, corpus_basedir, output_dir): 
     """Perform the ingest process for this corpus"""    
      
     self.setWrittenMetaData(os.path.join(corpus_basedir, "metadata"))
     self.setMetaData(os.path.join(corpus_basedir, "metadata"))
     self.ingestCorpus(os.path.join(corpus_basedir, "standoff"), output_dir)
            
     
  def setWrittenMetaData(self, dirpath):
    """ This method extracts the meta data for the written corpora for the ICE collections """

    # Initialise locally used vars
    rst = []
    utils.listFiles(rst, dirpath, False)
    new_group = True  # This boolean is used to mark the start of a new title in the written Meta file  
    group_ids = ()
    meta_publisher = {}
  
    # Open written workbook and extract meta data
    wb = xlrd.open_workbook(os.path.join(dirpath, "ICE-catalogue.xls"))
    self.book_date_mode = wb.datemode
  
    # TODO: This looks a bit nasty. The problem is the spreadsheet has so many empty fields.
    common_row_defn = (u'ignore',u'table_subtitle',u'table_date_of_publication',u'ignore',u'table_author')
    common_publisher_defn = self.__gen_ignores(1) + (u'table_publisher',)  
  
    w1a_header = (u'ignore', u'table_genre_subject', u'ignore', u'table_wordcount')
    w1a_row = (u'ignore', u'table_subtitle')
  
    w1b_header = (u'ignore', u'table_letter_genre', u'table_date_of_publication', u'table_wordcount')
    w1b_row = (u'ignore', u'table_subtitle')
  
    w2a_header = (u'ignore', u'table_source_title', u'table_date_of_publication', u'table_wordcount')
    w2b_header = w2a_header
    w2c_header = (u'ignore', u'table_source_title', u'ignore', u'table_wordcount')
  
    w2d_header = w2c_header
    w2d_row = (u'ignore', u'table_subtitle', u'table_date_of_publication', u'table_wordcount', u'table_author')
  
    w2e_header = self.__gen_ignores(9) + (u'table_source',) + self.__gen_ignores(213) + (u'table_wordcount',)
    w2e_row = self.__gen_ignores(8) + (u'table_source', u'table_subtitle',) + self.__gen_ignores(17) + (u'table_date_of_publication',)
    w2e_publisher_defn = self.__gen_ignores(9) + (u'table_publisher',) 
  
    w2f_header = self.__gen_ignores(8) + (u'table_source',) + self.__gen_ignores(67) + (u'table_date_of_publication',) + (u'table_wordcount',)
    w2f_row = self.__gen_ignores(3) + (u'table_wordcount',) + self.__gen_ignores(3) + (u'table_source', u'table_subtitle',) + self.__gen_ignores(4) + (u'table_publisher',) + self.__gen_ignores(9) + (u'table_date_of_publication',) + self.__gen_ignores(54) + (u'table_author',)
    w2f_publisher_defn = self.__gen_ignores(8) + (u'table_publisher',) 
       
    sheet_defn_ref = {0: [w1a_header, w1a_row, common_publisher_defn], \
      1: [w1b_header, w1b_row, common_publisher_defn], \
      2: [w2a_header, common_row_defn, common_publisher_defn], \
      3: [w2b_header, common_row_defn, common_publisher_defn], \
      4: [w2c_header, common_row_defn, common_publisher_defn], \
      5: [w2d_header, w2d_row, common_publisher_defn], \
      6: [w2e_header, w2e_row, w2e_publisher_defn], \
      7: [w2f_header, w2f_row, w2f_publisher_defn]}
  
    # Indicate which sets have publisher information
    has_publisher_info = {0: False, 1: False, 2: True, 3: True, 4: True, 5: True, 6: True, 7: True}
  
    # The written meta data spreadsheet consists of more than 8 work sheets
    # however the first 8 are for the written word only, the rest
    # are for the spoken word. These have been ignored for the moment
    for sheet_index in range(0,8):     
    
      sheet = wb.sheet_by_index(sheet_index)
      group_ids = ()
  
      # Iterate through all the rows ingesting meta data as we go along
      for i in range(1, sheet.nrows):
      
        row = sheet.row(i)
        sampleid = self.__convert(row[0]).upper()
      
        # We have a new sample at this point
        if sampleid != "":
        
          group_ids = group_ids + (sampleid,)
        
          # If it is a new group grab the Meta header row
          if new_group == True:
          
            # The header row is the row prior in a new group
            meta_header_item = self.__convert_row(sheet.row(i-1), sheet_defn_ref[sheet_index][0])
            new_group = False

          # Grab the meta line item for the corresponding sample
          meta_line_item = self.__convert_row(row, sheet_defn_ref[sheet_index][1])
        
          # Only add a meta item if it is clean and complete
          if meta_line_item['table_subtitle'] != "":

              # Update this line item with header values
              self.filemetadata[sampleid] = utils.merge_dictionaries(meta_line_item, meta_header_item)

        else: 
        
          # If the sample id is empty & we have just finished processing a group there might be publisher information
          # if so this publisher information should be appended to the samples data set
          if len(group_ids) > 0 and has_publisher_info[sheet_index] == True:
            meta_publisher = self.__convert_row(sheet.row(i), sheet_defn_ref[sheet_index][2])
          
            # Add the publisher to the meta line items discovered in the last round of updates
            for group_id in group_ids:
                self.filemetadata[group_id] = utils.merge_dictionaries(self.filemetadata[group_id], meta_publisher)      
          
          # Reset the group information
          group_ids = ()
          new_group = True


  def setMetaData(self, dirpath):

    rst = []
    utils.listFiles(rst, dirpath, False)
  
    # S1A
    wb = xlrd.open_workbook(os.path.join(dirpath, "demographic_info_ice-aus_s1a.xls"))
  
    # this spreadsheet has two sheets, they were slightly different but I've 
    # modified them to be the same
    fields = (
        u'ignore',
        u'table_category',
        u'table_wordcount',
        u'table_free_comments',
        u'table_source_type',
        u'table_date_of_recording',
        u'table_place_of_recording',
        u'table_communicative_situation',
        u'table_subject',
        u'table_number_of_speakers',
        u'table_relationship')
  
    for sheet_index in (0,1):
        sheet = wb.sheet_by_index(sheet_index)
        for row in [sheet.row(i) for i in range(1, sheet.nrows)]:
            sampleid = self.__convert(row[0]).upper()
                    
            self.filemetadata[sampleid] = self.__convert_row(row, fields)
            spkrinfo = self.__convert_speaker_info(row, 9, 11, sampleid, (u'age', u'gender', u'education', u'occupation'))
          
            self.filemetadata[sampleid].update(spkrinfo) 

    # S1B
    wb = xlrd.open_workbook(os.path.join(dirpath, "demographic_info_ice-aus_s1b.xls"))
    sheet = wb.sheet_by_index(0)
    fields = (
            u'ignore',
            u'table_number_of_subtexts' ,
            u'table_category',
            u'table_wordcount',
            u'table_version',
            u'table_free_comments',
            u'table_source_type',
            u'table_date_of_recording',
            u'table_place_of_recording',
            u'table_organising_body',
            u'table_subject',
            u'table_source_title',
            u'table_communicative_situation',
            u'table_number_of_participants',
            u'table_number_of_speakers',
            u'table_relationship')
    for row in [sheet.row(i) for i in range(1, sheet.nrows)]:
            sampleid = self.__convert(row[0]).upper()
            self.filemetadata[sampleid] = self.__convert_row(row, fields)
            spkrinfo = self.__convert_speaker_info(row, 14, 16, sampleid, (u'age', u'gender', u'education', u'occupation'))
            self.filemetadata[sampleid].update(spkrinfo)
          
    # sheet 'broadcast discussions'
    sheet = wb.sheet_by_index(1)
    fields = (
        u'ignore',
        u'table_number_of_subtexts' ,
        u'table_category',
        u'table_wordcount',
        u'table_version',
        u'table_free_comments',
        u'table_subject',
        u'table_place_of_recording',
        u'table_date_of_recording',
        u'table_program',
        u'table_channel', 
        u'table_recorder',
        u'table_mode',
        u'table_number_of_speakers',
    )
    for row in [sheet.row(i) for i in range(1, sheet.nrows)]: 
          sampleid = self.__convert(row[0]).upper()
          self.filemetadata[sampleid] = self.__convert_row(row, fields)
          spkrinfo = self.__convert_speaker_info(row, 13, 14, sampleid, (u'age', u'gender', u'education', u'surname', u'forename', u'occupation'))
          self.filemetadata[sampleid].update(spkrinfo)
  
  
    # sheet 'broadcast interviews'
    sheet = wb.sheet_by_index(2)
    fields = (
        u'ignore',
        u'table_number_of_subtexts' ,
        u'table_category',
        u'table_wordcount',
        u'table_free_comments',
        u'table_subject',
        u'table_place_of_recording',
        u'table_date_of_recording',
        u'table_program',
        u'table_channel', 
        u'table_recorder', 
        u'table_relationship',
        u'table_mode',
        u'table_number_of_speakers',
        u'table_number_of_participants',
        u'table_subtext_number',
        u'table_subtext_name',
        u'table_number_of_subtexts',
        u'table_textcode'
    )
    for row in [sheet.row(i) for i in range(1, sheet.nrows)]: 
          sampleid = self.__convert(row[0]).upper()
          self.filemetadata[sampleid] = self.__convert_row(row, fields)
          spkrinfo = self.__convert_speaker_info(row, 13, 19, sampleid, (u'age', u'gender', u'education', u'occupation'))
          self.filemetadata[sampleid].update(spkrinfo)
  
    # sheet 'parliamentary debate'
    sheet = wb.sheet_by_index(3)
    fields = (
        u'ignore', 
        u'table_category',
        u'table_wordcount',
        u'table_free_comments',
        u'table_date_of_recording',
        u'table_place_of_recording',
        u'table_channel',
        u'ignore',
        u'table_tv_or_radio', 
        u'table_source_title',
        u'table_subject',
        u'table_number_of_speakers',
        u'table_comments'
    )
    for row in [sheet.row(i) for i in range(1, sheet.nrows)]: 
          sampleid = self.__convert(row[0]).upper()
          self.filemetadata[sampleid] = self.__convert_row(row, fields)
          spkrinfo = self.__convert_speaker_info(row, 11, 13, sampleid, (u'age', u'gender', u'nationality', u'birthplace', u'education', u'occupation', u'mothertongue', u'otherlanguages'))
          self.filemetadata[sampleid].update(spkrinfo)
        
    # sheet 'legal cross-examination'
    sheet = wb.sheet_by_index(4)
    fields = (
        u'ignore',
        u'ignore',
        u'table_category',
        u'table_wordcount',
        u'table_free_comments',
        u'table_date_of_recording',
        u'table_place_of_recording',
        u'ignore',
        u'table_subject',
        u'table_title', 
        u'ignore',
        u'table_number_of_speakers',
        u'table_relationship',
        u'ignore',
        u'ignore'
    )
    for row in [sheet.row(i) for i in range(1, sheet.nrows)]: 
          sampleid = self.__convert(row[0]).upper()
          self.filemetadata[sampleid] = self.__convert_row(row, fields)
          spkrinfo = self.__convert_speaker_info(row, 11, 15, sampleid, (u'age', u'gender', u'nationality', u'birthplace', u'education', u'occupation', u'mothertongue', u'otherlanguages'))
          self.filemetadata[sampleid].update(spkrinfo)
        
    # sheet 'business transactions'
    sheet = wb.sheet_by_index(5)
    fields = (
        u'ignore',
        u'ignore',
        u'table_category',
        u'table_wordcount',
        u'table_free_comments',
        u'table_date_of_recording',
        u'table_place_of_recording',
        u'ignore',
        u'table_subject',
        u'table_number_of_speakers',
        u'table_relationship',
    )
    for row in [sheet.row(i) for i in range(1, sheet.nrows)]: 
          sampleid = self.__convert(row[0]).upper()
          self.filemetadata[sampleid] = self.__convert_row(row, fields)
          spkrinfo = self.__convert_speaker_info(row, 9, 11, sampleid, (u'age', u'gender', u'nationality', u'birthplace', u'education', u'occupation', u'mothertongue', u'otherlanguages'))
          self.filemetadata[sampleid].update(spkrinfo)
        
             
    
  
    # S2A
    wb = xlrd.open_workbook(os.path.join(dirpath, "demographic_info_ice-aus_s2a.xls"))
  
    # sheet 'spontaneous commentaries'
    sheet = wb.sheet_by_index(0)
    fields = (
            u'ignore',
            u'table_category',
            u'table_wordcount',
            u'table_free_comments',
            u'table_source_type',
            u'table_channel',
            u'table_tv_or_radio',
            u'table_source_title',
            u'table_date_of_recording',
            u'table_place_of_recording',
            u'table_subject',
            u'table_number_of_speakers'
    )
    for row in [sheet.row(i) for i in range(1, sheet.nrows)]: 
          sampleid = self.__convert(row[0]).upper()
          self.filemetadata[sampleid] = self.__convert_row(row, fields)
          spkrinfo = self.__convert_speaker_info(row, 11, 15, sampleid, (u'age', u'gender', u'education', u'occupation'))
          self.filemetadata[sampleid].update(spkrinfo)
        
        
        
    # sheet 'unscripted speeches'
    sheet = wb.sheet_by_index(1)
    fields = (
            u'ignore',
            u'table_category',
            u'table_wordcount',
            u'table_source_type',
            u'table_date_of_recording',
            u'table_place_of_recording',
            u'table_free_comments',
            u'table_audience',
            u'table_audience_size', 
            u'table_subject',
            u'table_number_of_speakers'
    )
    for row in [sheet.row(i) for i in range(1, sheet.nrows)]: 
          sampleid = self.__convert(row[0]).upper()
          self.filemetadata[sampleid] = self.__convert_row(row, fields)
          spkrinfo = self.__convert_speaker_info(row, 10, 11, sampleid, (u'age', u'gender', u'education', u'occupation'))
          self.filemetadata[sampleid].update(spkrinfo)
        
        
        
    # sheet 'demonstrations'
    sheet = wb.sheet_by_index(2)
    fields = (
            u'ignore',
            u'table_category',
            u'table_wordcount',
            u'table_version',
            u'table_free_comments',
            u'table_source_type',
            u'table_channel',
            u'ignore',
            u'table_tv_or_radio',
            u'table_source_title',
            u'table_date_of_recording',
            u'table_place_of_recording',
            u'table_organising_body', 
            u'table_subject',
            u'table_number_of_speakers',
            u'table_relationship',
    )
    for row in [sheet.row(i) for i in range(1, sheet.nrows)]: 
          sampleid = self.__convert(row[0]).upper()
          self.filemetadata[sampleid] = self.__convert_row(row, fields)
          spkrinfo = self.__convert_speaker_info(row, 14, 16, sampleid, (u'age', u'gender', u'education', u'occupation', u'surname', u'forename'))
          self.filemetadata[sampleid].update(spkrinfo)
        
    # sheet 'legal presentations'
    sheet = wb.sheet_by_index(3)
    fields = (
            u'ignore',
            u'table_category',
            u'table_wordcount',
            u'table_version',
            u'table_free_comments',
            u'table_source_type',
            u'table_date_of_recording',
            u'table_place_of_recording', 
            u'table_subject',
            u'table_number_of_speakers', 
    )
    for row in [sheet.row(i) for i in range(1, sheet.nrows)]: 
          sampleid = self.__convert(row[0]).upper()
          self.filemetadata[sampleid] = self.__convert_row(row, fields)
          spkrinfo = self.__convert_speaker_info(row, 9, 10, sampleid, (u'age', u'gender', u'education', u'occupation'))
          self.filemetadata[sampleid].update(spkrinfo)
        

    # S2B
    wb = xlrd.open_workbook(os.path.join(dirpath, "demographic_info_ice-aus_s2b.xls"))
    sheet = wb.sheet_by_index(0)
    fields = (
            u'ignore',
            u'ignore',
            u'table_category',
            u'table_wordcount', 
            u'table_free_comments',
            u'table_source_type',
            u'table_channel',
            u'ignore',
            u'table_tv_or_radio',
            u'table_source_title',
            u'table_date_of_recording',
            u'table_place_of_recording',
            u'table_number_of_speakers',
    )
    for row in [sheet.row(i) for i in range(1, sheet.nrows)]: 
          sampleid = self.__convert(row[0]).upper()
          self.filemetadata[sampleid] = self.__convert_row(row, fields)
          spkrinfo = self.__convert_speaker_info(row, 12, 12, sampleid, [])
          self.filemetadata[sampleid].update(spkrinfo)


    # sheet 'broadcast talks'
    sheet = wb.sheet_by_index(1)
    fields = (
            u'ignore',
            u'ignore',
            u'table_category',
            u'table_wordcount', 
            u'table_free_comments',
            u'table_source_type',
            u'table_channel',
            u'ignore',
            u'table_tv_or_radio',
            u'table_source_title',
            u'table_date_of_recording',
            u'table_place_of_recording',
            u'ignore',
            u'table_subject',
            u'ignore',
            u'ignore',
            u'ignore',
            u'table_number_of_speakers',
    )
    for row in [sheet.row(i) for i in range(1, sheet.nrows)]: 
          sampleid = self.__convert(row[0]).upper()
          self.filemetadata[sampleid] = self.__convert_row(row, fields)
          spkrinfo = self.__convert_speaker_info(row, 17, 21, sampleid, (u'surname', u'forename', u'age', u'gender', u'education'))
          self.filemetadata[sampleid].update(spkrinfo)

    # sheet 'speeches (non broadcast)'
    sheet = wb.sheet_by_index(2)
    fields = (
            u'ignore',
            u'ignore',
            u'table_category',
            u'table_wordcount', 
            u'table_free_comments',
            u'table_source_type', 
            u'table_date_of_recording',
            u'table_place_of_recording',
            u'table_organising_body',
            u'table_consent',
            u'table_subject',
            u'ignore',
            u'ignore',
            u'table_communicative_situation',
            u'table_number_of_speakers',
    )
    
    for row in [sheet.row(i) for i in range(1, sheet.nrows)]: 
          sampleid = self.__convert(row[0]).upper()
          self.filemetadata[sampleid] = self.__convert_row(row, fields)
          spkrinfo = self.__convert_speaker_info(row, 14, 18, sampleid, (u'age', u'gender', u'nationality', u'birthplace', u'education', u'mothertongue', u'otherlanguages'))
          self.filemetadata[sampleid].update(spkrinfo)


  def ingestCorpus(self, srcdir, outdir):

    print "  converting corpus in", srcdir, "into normalised data in", outdir  
    print "    clearing and creating output location"
    
    self.clear_output_dir(outdir)
  
    res = []
    utils.listFiles(res, srcdir, True)
    total = 0
    for f in res:
  
      if ( f.endswith(".txt") ): 
          print "ICE:", f
          (sampleid, rawtext, body, meta, anns) = self.ingestDocument(f)
          
          meta.update(self.META_DEFAULTS)
          
          subdir = f.replace(srcdir, '', 1)
          subdir = subdir.replace(os.path.basename(subdir), '')
          meta['subdir'] = subdir
          
          thisoutdir = os.path.dirname(f.replace(srcdir, outdir, 1))
          
          self.__serialise(thisoutdir, sampleid, body, meta, anns)
          
          #if total > 10:
          #    break
          total += 1
    
    schema = FieldMapper.generate_schema()
    schema.serialize(os.path.join(outdir, "schema.owl"), format="turtle")
    
    
  def ingestDocument(self, sourcepath):
    
    # matching annotation is in the .xml file
    annpath = os.path.splitext(sourcepath)[0]+".xml"
    anns = self.__parseStandoffAnnotations(annpath)
  
    fhandle = codecs.open(sourcepath, "r", "utf-8")
    text = fhandle.read()
    fhandle.close() 

    # get the sample name, also the sample cagetory which is the first three
    # letters (eg. W1A) and denotes the type of sample
    samplename = re.search("[SW].*\d[A-Z]?", os.path.basename(sourcepath)).group()
    meta = {'sampleid': samplename, 'category': samplename[:3]}
    if (samplename in self.filemetadata):
        meta.update(self.filemetadata[samplename])
  
    return (meta['sampleid'], text, text, meta, anns)



  def __serialise(self, outdir, sampleid, body, meta, anns):
    """Write out the various products of ingest to the output
    directory"""
    
    serialiser = Serialiser(outdir)
    return serialiser.serialise_single(sampleid, 'ice', None, body, iceM, meta, anns)



  def __parseStandoffAnnotations(self, path):
      '''Read annotation data from the given file in XML
      format, generate a list of annotation instances and return it'''
    
      #print "parsing", path, "\n"
      doc = ElementTree.parse(path)
     
      root =  doc.getroot()
    
      if root is None:
          print "No root for ", path
          return []
    
      docid = root.attrib['doc']
      # now generate one annotation isntance per annotation element in the
      # input
      anns = []
    
  #    <annotation id='S1A-066#a0'>
  #        <type>corpus</type>
  #        <start>0</start>
  #        <end>0</end>
  #        <property name='id'>S1A-066</property>
  #    </annotation>
      for node in root.findall("annotation"):
          id = node.attrib['id']
          type = node.find("type").text
          start = node.find("start").text
          end = node.find("end").text
          ann = Annotation(type, None, start, end, id=id)
          # add properties
          for p in node.findall('property'):
              ann[p.attrib['name']] = p.text
          anns.append(ann)

      return anns


  def __parseFile(self, filename):

    fhandle = codecs.open(filename, "r", "utf-8")
    text = fhandle.read()
    res = self.__parseData(text)
    fhandle.close()
    return res


  def __parseData(self, string):
    
    textString       = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=?@[\]^_`{|}~\n\t >"
    text             = Word(textString)
    textWithoutClose = Word(textString[0:len(textString)-1])
    iOpen, iClose    = makeHTMLTags("I")
    def inTag(parser):
      return (Literal('<') + parser + Literal('>'))
    header           = inTag(textWithoutClose("id")) + inTag(textWithoutClose("num"))
    body             = iOpen + text("data") + iClose
    whole            = header + body
    
    return whole.parseString(string)


  def __gen_ignores(self, number):
    '''
    Ice contains lots of fields which need to be ignored. This helper method helps to add ignore statements to the
    tuple passed to the converter.
    '''
    tupl = ()
    for i in range(0,number):
      tupl = tupl + (u'ignore',)

    return tupl
    

  def __convert(self, cell, uni=True):
     '''
     There are no float values in the Excel sheet. Cut hem here to int before
     converting to unicode. Also dates get some special treatment because of the way
     dates are represented in Excel (days counting from 1/1/1900)
     '''
     if cell.ctype in (2, 3, 4):

       # Dates require special conversion
       if cell.ctype == 3:

         year, month, day, hour, minute, second = xlrd.xldate.xldate_as_tuple(cell.value, self.book_date_mode)
         py_date = datetime.datetime(year, month, day, hour, minute, second) 

         # TODO: Does this date format work? No spec to decide at the moment
         return unicode(py_date.strftime('%y/%m/%d'))

       if (uni):    
         return unicode(int(cell.value))
       else:
         return int(cell.value)

     value = cell.value
     if value.startswith("'"):
         value = value[1:]

     return value


  def __convert_speaker_info(self, row, countcol, startcol, sampleid, fields):
     """Generate the speaker descriptions from a spreadsheet given 
     the column containing the speaker count, the start column
     and the number of speaker fields to look for. 
     Returns a dictionary of speaker descriptions or an empty dictionary if
     the count field is empty."""

     speakertitles = {0:"A", 1:"B", 2:"C", 3:"D", 4:"E", 5:"F", 6:"G", 7:"H", 8:"I", 9:"J", 10:"K", 11:"L", 12:"M", 13:"N", 14:"O", 15:"P", 16:"Q", 17:"R", 18:"S", 19:"T", 20: "U", 21: "V", 22: "W", 23: "X", 24: "Y", 25: "Z"}

     if self.__convert(row[countcol]) == '':
         return dict()

     result = dict() 
     for speaker in range(0,int(self.__convert(row[countcol], False))):

         info = dict()
         info['id'] = self.__convert(row[0]) + u"#" + speakertitles[speaker]
         if len(row) >= startcol + (1+speaker)*len(fields):
             for i in range(len(fields)):
                 value = self.__convert(row[i+startcol+speaker*len(fields)])
                 if value != '':
                     info[fields[i]] = value

         info[u'role'] = u'speaker'
         result[u"table_person_"+speakertitles[speaker]] = info

     return result     


  def __convert_row(self, row, fields):
   """Given a list of field names, generate a dictionary
   from the consecutive elements of the list row
   by passing the values through 'convert', unless
   the field name is 'ignore' in which case it is skipped.
   Return a dictionary of field names and values"""

   if len(fields) > len(row): 
       raise Exception("Too many fields (%d) for the row I was given (%d)" % (len(fields), len(row)))

   result = dict()

   for i in range(len(fields)):
       if fields[i] != "ignore":
           result[fields[i]] = self.__convert(row[i])
   return result