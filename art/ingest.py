import codecs
import os
import pyparsing
import re
import xlrd

from datetime import datetime

from ausnc_ingest.annotations import *
from ausnc_ingest.annotations.annotation import *
from ausnc_ingest.annotations.annotated_text import *
from ausnc_ingest.annotations.annotation_parsers import *
from ausnc_ingest.ingest_base import IngestBase
from ausnc_ingest.utils.filehandler import FileHandler
from ausnc_ingest.art.iterator import ArtIterator
from ausnc_ingest.art.parser import *
from ausnc_ingest.art.sample import Sample
from ausnc_ingest.art.rdf import *
from ausnc_ingest.utils.serialiser import Serialiser


class ARTIngest(IngestBase):
    
    person_no = 1
    file_meta = {}
    
    presenter_meta = {
        1: {12: 'name', 13: 'gender', 14: 'age'}, 
        2: {15: 'name', 16: 'gender', 17: 'age'}
    }
    
    expert_meta = {
        3: {18: 'name', 19: 'gender', 20: 'age', 21: 'role'},
        4: {22: 'name', 23: 'gender', 24: 'age', 25: 'role'},
        5: {26: 'name', 27: 'gender', 28: 'age', 29: 'role'}
    } 


    def setMetaData(self, srcdir):
        ''' Loads the meta data for use during ingest '''
        
        # Open workbook and extract meta data
        wb = xlrd.open_workbook(srcdir)

        self.book_date_mode = wb.datemode

        # There is only one sheet in the spreadsheet in the meta data
        for sheet_index in range(0,1):     

            sheet = wb.sheet_by_index(sheet_index)

            # Iterate through all the rows ingesting meta data as we go along
            for i in range(1, sheet.nrows):

                row = sheet.row(i)
                sampleid = self.__convert(row[0]).upper()
                
                # Initialise the person_no
                self.person_no = 1
        
                if sampleid != " " and sampleid != "":
                    
                    # Extract linear fields from spreadsheet
                    self.file_meta[sampleid] = { 'sampleid': sampleid }
                    self.file_meta[sampleid]['location'] = self.__convert(row[1])
                    self.file_meta[sampleid]['station'] = self.__convert(row[2])
                    self.file_meta[sampleid]['program'] = self.__convert(row[3])
                    self.file_meta[sampleid]['recorded'] = self.__convert_to_date(row[4].value)
                    self.file_meta[sampleid]['transcribed'] = self.__extract_transcribed(row)
                    self.file_meta[sampleid]['proof_heard'] = self.__convert(row[6])
                    self.file_meta[sampleid]['final_check'] = self.__convert(row[7])
                    self.file_meta[sampleid]['subject'] = self.__convert(row[9])
                    self.file_meta[sampleid]['duration'] = self.__convert(row[10])
                    self.file_meta[sampleid]['transcriber_instructions'] = self.__extract_transcriber_instructions(row)
                    
                    # Extract series fields presenter, expert and caller from spreadsheet
                    self.__extract_presenter_info(sampleid, self.file_meta, row)
                    self.__extract_expert_info(sampleid, self.file_meta, row)
                    self.__extract_caller_info(sampleid, self.file_meta, row)
                    
    
    def ingestCorpus(self, srcdir, outdir):
        
        print "  converting corpus in", srcdir, "into normalised data in", outdir
        print "    clearing and creating output location"
    
        self.outdir = outdir
    
        # Clear the output directory and make it if it does not exist
        self.clear_output_dir(outdir)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
            
        fileHandler = FileHandler()
        res = fileHandler.getFiles(srcdir, r'^[\w\d-]+\.txt') 
        # res = file_handler.getFiles(srcdir, r'^sample1.txt$')
    
        print "    processing files (this might take a while)..."
        
        for name, f in res.items():
            (sofar, total) = self.ingestDocument(f)
    
        print "\033[2K   ", sofar, "of ", total, " samples processed"
        
    
    def ingestDocument(self, sourcepath):
        
        # Read the file line by line
        fileHandle = codecs.open(sourcepath, "r", "utf-8")
        fileContent = fileHandle.read()
        
        # Parse the content into simple list construct
        parsedContent = parseCompleteDocument(fileContent)
        
        sofar = total = 1
        body = ''
        anns = []
        serialiser = Serialiser(self.outdir)
        
        for rawSample in ArtIterator(parsedContent):
            # Find corresponding meta data for sample
            # item holds the start index and length of the sample in the original parsedContent
            sample = Sample(parsedContent[rawSample[0]: rawSample[1]])
            meta = self.findMetaData(sample)
            
            if meta is not None:
                rawText = sample.extractRawText()
            
                # Now we iterates through the speaker turns in a sample and collect
                # annotations and body (minus meta data) from the sample
                for speakerTurn in sample:
                    result = self.extractAnnotations(speakerTurn[1])
                    body += result[0] + '\n'
                    for ann in result[1]:
                        anns.append(ann)
            
                # Serialise the documents to rdf documents and write the output to disk
                serialiser.serialise_single(meta['sampleid'], 'art', unicode(rawText), unicode(body), artMapper, meta, anns)
                
                print "\033[2K   ", sofar, "of 29", "\033[A"
                sofar += 1       
                

            total += 1
      
        return (sofar, total)
        
    
    def findMetaData(self, sample):
        """ This function finds meta data that corresponds to the provided sample
        from the ART corpus collection. The sample is located by matching the presenter
        and expert details in the sample to the meta data. The combination of these
        two fields are unique. """
        
        # Grab the presenter and expert details if it exists from the sample
        speaker1 = sample.getPrimarySpeaker().strip()
        speaker2 = sample.getSecondarySpeaker()
        
        for metaItem in self.file_meta.itervalues():
            metaSpeaker1 = metaItem['table_person_1']['name'].strip()
            metaSpeaker2 = metaItem['table_person_2']['name'].strip()
            
            # print 'metaSpeaker1: ', metaSpeaker1, ' metaSpeaker2: ', metaSpeaker2
            
            # If the two speakers match then we have found our sample
            if speaker2 is None and speaker1 == metaSpeaker1.strip():
                return metaItem
            elif speaker1 == metaSpeaker1 and speaker2.strip() == metaSpeaker2:
                return metaItem
        
        # This means we have not been able to find the meta, this is a problem
        print 'Problem, could not find meta data for sample starting with primary speaker ', speaker1 , \
        ' and secondary speaker ', speaker2

        return None
    
    
    def extractAnnotations(self, data):
        """ From the text with no meta-data, extract all the annotations and return the text
        free of these annotations along with the list of annotations found """
        if data == "":
            return ("",[])
  
        parser = pyparsing.OneOrMore( slurpParser('{<') \
                                  ^ artpauseParser() \
                                  ^ interjectionParser() \
                                  ^ correctionParser() ).setParseAction(lambda s, loc, toks: concatAnnotatedText(toks))
                    
        res = parser.parseString(data)
        return (res[0].text, res[0].anns)
   
       
    def __extract_presenter_info(self, sampleid, file_meta, row):
        """ This function interogates the participant information and builds sub-dictionaries which 
        are attached to the principal sample """
        # Look for presenters firstly
        for key, value in self.presenter_meta.iteritems():
            info = {}
            info['id'] = sampleid + u"#" + str(key)
            info[u'role'] = u'presenter'

            for sub_key, sub_value in value.iteritems():
                info[sub_value] = unicode(row[sub_key].value)
            
            # Only add the value if there is proper content
            if info.has_key('name') and info['name'] != '':
                file_meta[sampleid][u"table_person_" + str(self.person_no)] = info
                self.person_no += 1
    
    
    def __extract_expert_info(self, sampleid, file_meta, row):
        """ This function interogates the participant information and builds sub-dictionaries which are attached to the principal sample """
        # Look for presenters firstly
        for key, value in self.expert_meta.iteritems():
            info = {}
            info['id'] = sampleid + u"#" + str(key)

            for sub_key, sub_value in value.iteritems():
                info[sub_value] = unicode(row[sub_key].value)

            # Only add the value if there is proper content
            if info.has_key('name') and info['name'] != '':
                file_meta[sampleid][u"table_person_" + str(self.person_no)] = info
                self.person_no += 1
                            
    
    def __extract_caller_info(self, sampleid, file_meta, row):
        """ This function extracts the caller information of which there could be a maximum of 53 """
        caller_max_index = 53 * 4 + 30
        for index in range(30, caller_max_index, 4):
          
            # Some callers are grouped into a single cell and separated by a '/'
            if len(self.__convert(row[index]).split('/')) > 1:
              # Add first caller
              info = { 'id' : sampleid + u"#" + str(self.person_no)}
              info['name'] = self.__convert(row[index]).split('/')[0]
              info['gender'] = self.__convert(row[index + 1]).split('/')[0]
              info['age'] = self.__convert(row[index + 2])
              info['location'] = self.__convert(row[index + 3])
              info['role'] = u'caller'
              
              # Only add the value if there is proper content
              if info.has_key('name') and info['name'] != '':
                  file_meta[sampleid][u"table_person_" + str(self.person_no)] = info
                  self.person_no += 1
              
              # Add second caller
              info = { 'id' : sampleid + u"#" + str(self.person_no)}
              info['name'] = self.__convert(row[index]).split('/')[1]
              
              if len(self.__convert(row[index + 1]).split('/')) > 1:
                info['gender'] = self.__convert(row[index + 1]).split('/')[1]
              else:
                info['gender'] = self.__convert(row[index + 1])
                
            else:
              info = { 'id' : sampleid + u"#" + str(self.person_no)}
              info['name'] = self.__convert(row[index])
              info['gender'] = self.__convert(row[index + 1]) 
              
            info['age'] = self.__convert(row[index + 2])
            info['location'] = self.__convert(row[index + 3])
            info['role'] = u'caller'
            
            # Only add the value if there is proper content
            if info.has_key('name') and info['name'] != '':
                file_meta[sampleid][u"table_person_" + str(self.person_no)] = info
                self.person_no += 1
    
    
    def __extract_transcribed(self, row):
        """ This function parses the transcribed value in the meta data by removing the initials and by
        parsing the date component """
        m = re.search('\d+.\d+.\d+', row[5].value)
        if m is not None:
            return self.__convert_to_date(m.group(0))
        else:
            return ''       
        
    def __extract_transcriber_instructions(self, row):
        return self.__convert(row[11])
    
    
    def __convert_to_date(self, value):
        """ Function returns recorded data for sample """
        py_date = datetime.strptime(value, '%d.%m.%y')
        return unicode(py_date.strftime('%Y/%m/%d'))
    

    def __convert(self, cell, uni=True):
        """ A simple function which extracts the value from a cell and unicodes the value if uni is True """
        if uni:
            return unicode(cell.value)
        else:
            return cell.value