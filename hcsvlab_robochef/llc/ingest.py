import os.path
import xlrd
import datetime

from hcsvlab_robochef import utils
from hcsvlab_robochef.ingest_base import IngestBase
from hcsvlab_robochef.llc.rdf import llcMap
from hcsvlab_robochef.utils.serialiser import *
from hcsvlab_robochef.utils.statistics import *
from hcsvlab_robochef.utils.filehandler import FileHandler


class LLCIngest(IngestBase):

    metadata = {}
    META_DEFAULTS = {'language': 'eng'}

    def setMetaData(self, filename):
        """
        Set the spreadsheet file from which LLC metadata is read.  This data will
        be combined with the pathnames to the documents themselves.
        """

        wb = xlrd.open_workbook(filename)
        count = 0
        for sheet_i in range(2, 19):
            sheet = wb.sheet_by_index(sheet_i)
            tags = map(self.__convert, sheet.row(0))

            for row in [sheet.row(i) for i in range(1, sheet.nrows)]:
                sampleid = self.__convert(row[0]).strip() # use Recording ID as sampleid, which is what we want as the identifier of the item
                row_metadata = {'sampleid': sampleid}
                row_metadata.update(self.META_DEFAULTS)
                for idx in range(0, sheet.ncols):
                    propertyName = tags[idx].strip()
                    propertyValue = self.__convert(row[idx], wb).strip()
                    row_metadata[propertyName] = propertyValue

                self.metadata[(sampleid)] = row_metadata

                # need name of the recording to look up metadata
                sample_name = row[3].value.strip()

                # use path in addition to look up metadata, as filenames are not unique
                if row[2].value == '':
                    sample_path = row[1].value.strip()
                else:
                    sample_path = os.path.join(row[1].value.strip(), row[2].value.strip())
                self.metadata[(sample_name, sample_path)] = sampleid
                # when the actual file name does not match the recording name listed in spreadsheet, use path only
                self.metadata[(sample_path)] = sampleid
                count += 1

    def ingestCorpus(self, srcdir, outdir):

        print "  converting corpus", srcdir, "into normalised data in ", outdir
        print "    clearing and creating output location"
      
        self.clear_output_dir(outdir)

        print "    processing files..."

        fileHandler = FileHandler()
        # 3 items in the LLC corpus have transcripts only (no audio), as indicated by Keith Bain
        files = fileHandler.getUniqueFiles(srcdir, r'^.+\.(wav|WAV|mp3|MP3|rm|RM|wma|WMA)$|^AbnPsycHistandTheoCh4Oct20.xml$|^sip_2010_10_19_1.XML$|^abnpsycspecdisoct13_EML.XML$')
        total = len(files.keys())
        sofar = 0


        for (name, root), path in files.iteritems():
            item_name = name
            self.__serialise(outdir, item_name, path, srcdir)
            sofar += 1
            print "   ", sofar, "of", total, "DOC:" + path

        print "   ", total, " Items processed"


    def ingestDocument(sourcepath):
        '''
        Ingest a specific source document, from which meta-data annotations and raw data is produced
        '''
        print "Error: calling unsupported operation - ingestDocument(" + sourcepath + ")"
        return None

    def identify_documents(self, documents):
        indexable = None
        display = None
        for doc in documents:
            if doc.get('filetype') == 'Audio':
                display = doc['uri']
        return (indexable, display)

    def __serialise(self, outdir, sample_name, source, srcdir):
        ''':
        Function serialises the graphs to disc and returns the object graph to the caller
        '''
        serialiser = Serialiser(outdir)
        sample_path = re.search('/LLC/(.+?)/'+re.escape(sample_name), source).group(1)

        if (sample_name, sample_path) in self.metadata:
            sampleid = self.metadata[(sample_name, sample_path)]
        else:
            sampleid = self.metadata[(sample_path)]

        if (sampleid) in self.metadata:
            meta = {}
            meta.update(self.metadata[(sampleid)])

            source_list = []

            if meta['Recording'].lower() == 'no audio':
                meta['Recording'] = sampleid + ' (No Audio)'
            else:
                meta['Recording'] = meta['Recording'].replace(meta['Recording'].split('.')[0], sampleid+'_Audio')

            # handle the 'flat' directories separately, as they shouldn't do a dir tree walk (just have recording + transcript docs)
            if sample_path.endswith('Feb_4_2011') or sample_path.endswith('April_2012_Business_Case') or \
                    sample_path.endswith('Stan-Armstrong') or sample_path.endswith('Paul-Erickson') or \
                    sample_path.endswith('John-Bechtold') or sample_path.endswith('Mike-Wald'):
                sampleid = self.metadata[(sampleid)]['Recording ID']
                source_list.append({'filetype': 'Audio', 'sourcepath': source, 'keyname': meta['Recording']})
                transcript = meta['Transcript']
                transcript_keyname = transcript.replace(transcript.split('.')[0], sampleid+'_Transcript')
                source_list.append({'filetype': transcript.split('.')[-1].upper(), 'sourcepath': os.path.join(os.path.dirname(source), transcript), 'keyname': transcript_keyname})
                meta['Transcript'] = transcript_keyname
                return serialiser.serialise_unique_multiple(sampleid, source_list, 'LLC', llcMap, meta, [], self.identify_documents)

            current_dir = os.path.join(srcdir, self.metadata[(sampleid)]['Root Directory'], self.metadata[(sampleid)]['Folder'])
            for (path, dirs, files) in os.walk(current_dir):
                for filename in files:
                    accuracy = '_accuracy_'
                    source_path = os.path.join(path, filename)
                    if filename == "raw.txt":
                        filetype = 'Raw'
                        keyname = accuracy + filename
                    elif filename == "ed.txt":
                        filetype = 'TXT'
                        keyname = accuracy + filename
                    elif filename == "raw.cmp":
                        filetype = 'CMP'
                        keyname = accuracy + filename
                    elif filename.lower().endswith('.wav') or filename.lower().endswith('.mp3') or filename.lower().endswith('.rm') or filename.lower().endswith('.wma'):
                        filetype = 'Audio'
                        keyname = '_Audio.' + filename.split('.')[-1].upper()
                    else:
                        filetype = filename.split('.')[-1].upper()
                        if filename.lower() == meta['Transcript'].lower():
                            keyname = '_Transcript.' + filetype
                        else:
                            keyname = '.' + filetype

                    source_list.append({'filetype': filetype, 'sourcepath': source_path, 'keyname': sampleid + keyname})
            meta['Transcript'] = meta['Transcript'].replace(meta['Transcript'].split('.')[0], sampleid+'_Transcript')
            return serialiser.serialise_unique_multiple(sampleid, source_list, 'LLC', llcMap, meta, [], self.identify_documents)
        else:
            print ""
            print "### Error: file '", source, "' with key '", sample_name, sampleid, "' has no metadata."
            print ""

    def __convert(self, cell, workbook=None):
        ''' There are no float values in the Excel sheet. Cut hem here to int before converting to unicode. '''
        if cell.ctype == 2:  # XL_CELL_NUMBER
            if cell.value == int(cell.value):
                return unicode(int(cell.value))
            else:
                return unicode(cell.value)
        elif cell.ctype == 3:  # XL_CELL_DATE
            return self.__convert_to_date(cell.value, workbook)
        elif cell.ctype == 4:  # XL_CELL_BOOLEAN
            return unicode(int(cell.value))
        elif cell.ctype == 5:  # XL_CELL_ERROR
            return ''
        return cell.value

    def __convert_to_date(self, value, workbook):
        """ Function returns recorded data for sample """
        date_tuple = xlrd.xldate_as_tuple(value, workbook.datemode)
        py_date = datetime.datetime(date_tuple[0], date_tuple[1], date_tuple[2], date_tuple[3], date_tuple[4], date_tuple[5])
        return unicode(py_date.strftime('%Y-%m-%d'))