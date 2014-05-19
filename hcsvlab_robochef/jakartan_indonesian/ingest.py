import os.path
import xlrd

from hcsvlab_robochef import utils
from hcsvlab_robochef.ingest_base import IngestBase
from hcsvlab_robochef.jakartan_indonesian.rdf import jakartanIndonesianMap
from hcsvlab_robochef.utils.serialiser import *
from hcsvlab_robochef.utils.statistics import *
from hcsvlab_robochef.utils.filehandler import FileHandler


class JakartanIndonesianIngest(IngestBase):

    metadata = {}
    speakermetadata = {}
    META_DEFAULTS = {}

    def setMetaData(self, filename):
        """
        Set the spreadsheet file from which pixar metadata is read.  This data will
        be combined with the pathnames to the documents themselves.
        """

        wb = xlrd.open_workbook(filename)
        sheet = wb.sheet_by_index(1)
        tags = map(self.__convert, sheet.row(0))

        speakerSheet = wb.sheet_by_index(2)
        speakerTags = map(self.__convert, speakerSheet.row(0))
        speakerTags.pop(0)
        speakerTags.insert(0, u'id')


        for row in [sheet.row(i) for i in range(1, sheet.nrows)]:
            sampleid = self.__convert(row[0]).strip()
            row_metadata = { 'sampleid': sampleid }
            row_metadata.update(self.META_DEFAULTS)
            for idx in range(1, sheet.ncols):
                propertyName = tags[idx].strip()
                propertyValue = self.__convert(row[idx]).strip()
                row_metadata[propertyName] = propertyValue

            # Collect speaker metadata
            speakersId = self.__convert(row[3]).split(",")
            for speakerId in speakersId:
                speakerId = speakerId.strip()
                speakerRow = self.__lookForSpeaker(speakerId, speakerSheet)
                if (speakerRow != None):
                    self.speakermetadata[speakerId] = {
                        u'table_person_' + speakerId: {
                            speakerTags[idx]:self.__convert(speakerRow[idx]) for idx in range(0, len(speakerRow)-1)
                        }
                    }
                else:
                    print "### WARN: Speaker with id", speakerId, "Not found."

            self.metadata[sampleid] = row_metadata

    def ingestCorpus(self, srcdir, outdir):

        print "  converting corpus", srcdir, "into normalised data in ", outdir
        print "    clearing and creating output location"
      
        self.clear_output_dir(outdir)

        print "    processing files..."

        dirs = os.walk(srcdir)

        fileHandler = FileHandler()
        files = fileHandler.getFiles(srcdir, r'^.+\.(wav|WAV)')
        total = len(files.keys())

        sofar = 0
        for name, path in files.iteritems():
            # item_name = name.replace(".wav", "")
            item_name = name[:-4]
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
            if doc.get('filetype') == 'MP3':
                display = doc['uri']
            if doc.get('filetype') == 'TXT':
                indexable = doc['uri']
        return (indexable, display)

    def __serialise(self, outdir, sampleid, source, srcdir):
        '''
        Function serialises the graphs to disc and returns the object graph to the caller
        '''
        serialiser = Serialiser(outdir)

        if (sampleid in self.metadata):
            meta = {}
            meta.update(self.metadata[sampleid])
            speakersId = self.metadata[sampleid]["Speakers"]
            for speakerId in speakersId.split(","):
                meta.update(self.speakermetadata[speakerId.strip()])

            source_list = []
            source_list.append({'filetype': 'Audio', 'sourcepath': source})

            full_mp3 = os.path.join(srcdir, 'mp3', sampleid) + ".mp3"
            if os.path.isfile(full_mp3):
                source_list.append({'filetype': 'MP3', 'sourcepath': full_mp3})
            else:
                print "### Error:", full_mp3, "No found"

            transcriptFile = self.metadata[sampleid]['Transcript File']
            if (transcriptFile != "" and transcriptFile != "No transcript"):
                full_transcript_rtf = os.path.join(srcdir, 'transcriptFiles', transcriptFile) + ".rtf"
                full_transcript_txt = os.path.join(srcdir, 'transcriptFiles', transcriptFile) + ".txt"

                if os.path.isfile(full_transcript_rtf):
                    source_list.append({'filetype': 'RTF', 'sourcepath': full_transcript_rtf})
                else:
                    print ""
                    print "### Error:", full_transcript_rtf, "Not found"
                    print ""
                if os.path.isfile(full_transcript_txt):
                    source_list.append({'filetype': 'TXT', 'sourcepath': full_transcript_txt})
                else:
                    print ""
                    print "### Error:", full_transcript_txt, "Not found"
                    print ""

            return serialiser.serialise_multiple(sampleid, source_list, 'JakartanIndonesian', jakartanIndonesianMap, meta, [], self.identify_documents)

        else:
            print ""
            print "### Error: file '", source, "' with key '", sampleid, "' has no metadata."
            print ""

    def __lookForSpeaker(self, speakerId, speakerSheet):
        ''' Function  iterates the speakers sheet looking for speakerId '''
        for row in [speakerSheet.row(i) for i in range(1, speakerSheet.nrows)]:
            currentId = self.__convert(row[0])
            if currentId == speakerId:
                return row
        return None


    def __convert(self, cell):
        ''' There are no float values in the Excel sheet. Cut hem here to int before converting to unicode. '''
        if cell.ctype in (2, 3, 4):
            return unicode(int(cell.value))
        return cell.value
