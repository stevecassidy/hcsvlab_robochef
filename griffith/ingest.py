import subprocess
import string

from hcsvlab_robochef import utils
from hcsvlab_robochef.ingest_base import IngestBase
from hcsvlab_robochef.utils.serialiser import *
from hcsvlab_robochef.annotations import *


from pyparsing import *
from xml.etree import ElementTree as ET
from rdf import griffMap


class GriffithIngest(IngestBase):
    filemetadata = {}
    META_DEFAULTS = {'language': 'eng'}

    def setMetaData(self, dirpath):
        """ Load the meta data from the XML documents provided for the Griffith corpus """

        rst = []
        utils.listFiles(rst, dirpath, False)

        for fl in rst:
            xml_tree = ET.parse(fl)
            tags = {}

            for tag in xml_tree.iter():
                if len(list(tag)) == 0:

                    # Characters that cannot be decoded are re-encoded firstly. The 'replace' argument
                    # replaces characters with ? that cannot be decoded
                    tmp_text = None
                    if tag.text is not None:
                        tmp_text = tag.text.encode('utf-8', 'replace')

                    tags[tag.tag.decode('utf-8')] = u"" if (tmp_text is None) else tmp_text.decode('utf-8')

            pos_of_space = int(string.find(tags[u"Title"], u" "))
            sample_name = tags[u"Title"][0:pos_of_space]

            # Only add the meta data if it is not present
            if not sample_name in self.filemetadata:
                self.filemetadata[sample_name] = {}

            spec_tags = {}
            sample_type = re.sub("\s|-", u"_", tags[u"Title"][pos_of_space + 1:].strip(u" -"))

            if u"Participant" in sample_type:
                sample_type = u"table_person_" + sample_type
                spec_tags[u"role"] = u"participant"
                spec_tags[u"id"] = sample_name + u"#" + (re.search("(\d)*$", sample_type).group(1))
            elif sample_type in ["Audio", "Transcript", "Audio_Recording"]:

                if sample_type == 'Transcript':
                    sample_type = 'Text'
                elif sample_type == 'Audio_Recording':
                    sample_type = 'Audio'

                spec_tags[u'filename'] = sample_name
                spec_tags[u"id"] = sample_name + u"#" + sample_type
                sample_type = u"table_document_" + sample_name + '#' + sample_type

            for k, v in tags.iteritems():
                spec_tags[k] = v

            self.filemetadata[sample_name][sample_type] = spec_tags


    def ingestCorpus(self, srcdir, outdir):

        print "  converting corpus in", srcdir, "into normalised data in", outdir
        print "    clearing and creating output location"
        self.clear_output_dir(outdir)

        '''
        Get the files we would like to process, GCSAusE12, E13 and E06 appear to be problematic and have been ignored,
        perhaps this is something we need to address?
        '''
        file_handler = FileHandler()
        res = file_handler.getFiles(srcdir, r'^[\w\d-]+\.doc$', r'.DS_Store|GCSAusE12.doc|GCSAusE13.doc|GCSAusE06.doc')

        sofar = 0
        total = len(res)

        print "    processing files..."

        for name, f in res.items():

            print sofar, "of", total, f, "\033[A"

            (rawtext, body, meta, anns) = self.ingestDocument(f)
            meta.update(self.META_DEFAULTS)
            # Set the output location and make the directory if is not present
            source_file = f
            f = f.replace(srcdir, outdir, 1)
            try:
                os.makedirs(os.path.dirname(f))
            except:
                pass

            ff = os.path.abspath(f)

            # Serialise the documents to rdf documents and write the output to disk
            self.__serialise(srcdir, os.path.dirname(ff), source_file, name, rawtext, body, meta, anns)

            sofar += 1

        print "\033[2K   ", total, "files processed"


    def ingestDocument(self, f):

        text = subprocess.check_output(["antiword", '-m', 'UTF-8.txt', "-f", f])
        text = text.decode('utf-8')
        fh = open("last_processed_file", "w")
        fh.write(text.encode('utf-8'))
        fh.close()

        body = self.parseBody(text)["body"]
        meta = self.parseTopTable(text)["topTable"]

        # we need meta to have a sampleid field
        meta[u'sampleid'] = os.path.basename(os.path.splitext(f)[0])

        # all griffith samples are interviews
        meta['genre'] = 'interview'

        body, anns = self.__extractAnnotations(body)

        samplename = re.search("GC.*\d", f).group()
        meta.update(self.filemetadata[samplename])

        return text, body, meta, anns


    def parseTopTable(self, text):
        """ Parses the header block after it has been converted to text """

        whole = Suppress(u"Transcript Coversheet") + Suppress(u"|") + Suppress(u"|Data") + Suppress(u"|") \
                + utils.tableParser(2).setResultsName("topTable")

        return whole.parseString(self.__getHeader(text))


    def parseBody(self, text):
        """ Parses the remainder of the document, after it has been converted to text """

        data = text.replace(self.__getHeader(text), "")

        whole = ZeroOrMore(Suppress("\n") ^ Suppress(Literal("((") + CharsNotIn(")") + Literal("))"))) \
                + (OneOrMore(self.__possibleLine()).leaveWhitespace().setParseAction(
            lambda s, loc, toks: "\n".join(toks))).setResultsName("body") \
                + StringEnd()
        try:
            result = whole.parseString(data)
        except Exception, e:
            self.logger.exception(e)

        return result



    def __serialise(self, srcdir, outdir, source_file, name, rawtext, body, meta, anns):
        """
        This function serialises the data and returns the serialised graph object
        """

        file_handler = FileHandler()
        serialiser = Serialiser(outdir)

        # Now check to see if the text file has a compatriot audio file. If it does generate output
        # relevant to the presence of two such files. We ignore the XML files because those files
        # contain the meta data used by the setMetaData method
        compatriot = file_handler.findCompatriot(srcdir, name, r'^[\w\d\s-]+.mp3$', r'^[\w\d-]+.xml$')

        if compatriot is not None:
            original_doc = {'filetype': 'Text', 'sampleid': meta['sampleid'], 'rawtext': rawtext, 'text': body,
                            'sourcepath': source_file}
            compatriot = {'filetype': 'Audio', 'sampleid': meta['sampleid'], 'sourcepath': compatriot}
            return serialiser.serialise_multiple(meta['sampleid'], (original_doc, compatriot, ), 'griffith', griffMap,
                                                 meta, anns)

        else:
            return serialiser.serialise_single(meta['sampleid'], 'griffith', rawtext, body, griffMap, meta, anns,
                                               source_file)


    def __getHeader(self, text):
        """
        This function returns the header block. Note that it also returns the initial index digit
        of the speaker turns. This has no side-effect though.
        """
        return SkipTo(Word("ABCDEFGHIJKLMNOPQRSTUVWXY") + Word(":")).parseString(text)[0]


    def __markupParser(self):
        markups = Forward()
        markups << oneOrMoreParsers(
            slurpParser(u"():?,." + unichr(9702) + u"\u00B0\xbf\xba<>=\u2020" + unichr(8593) + unichr(8595))
            ^ micropauseParser()
            ^ pauseParser()
            ^ elongationParser()
            ^ uncertaintyParser()
            ^ unknownParser()
            ^ dubiousOrNonsenseParser(markups)
            ^ intonationParser()
            ^ softParser(markups)
            ^ speedParser(markups)
            ^ latchedParser()
            ^ (Suppress(u'\u2020') + markups + Suppress(u'\u2020')).setParseAction(
                lambda s, loc, toks: toks[0].add_anns_chain([Annotation("unknown", "pic", 0, len(toks[0].text))]))
        )
        return markups

    def __ourSpeakerParser(self):
        return speakerParser(self.__markupParser())


    def __extractAnnotations(self, data):
        # there is an artifact of the doc conversion to fix up here.  "[pic] in the document
        # means _something else_, but we don't know what yet.
        data = data.replace(u"[pic]", u'\u2020')

        # remove troublesome characters
        # TODO: reinstate these so you can pick up more annotations from griffith.
        # pipe is not an annotation, it is junk data coming from some of the docs.
        for c in u"<>[]|":
            data = data.replace(c, u'')

        try:
            # we are not quite ready for this yet
            full_anns = (Optional(pauseParser(), AnnotatedText("", [])) + self.__ourSpeakerParser()) \
                .setParseAction(lambda s, loc, toks: toks[0] + toks[1]).parseString(data)[0]
            #full_anns =  markups.parseString(data)[0]
        except:
            f = open("griffith_error_data.txt", 'w')
            f.write(data.encode('utf-8'))
            f.close()
            raise

        return full_anns.text, full_anns.anns


    def __possibleLine(self):
        return (Suppress(Optional(Optional(Word(" ")) + Optional(Word("|")) + Word(nums + "."))).leaveWhitespace()
                + CharsNotIn("\n").leaveWhitespace() + Suppress(Optional("\n"))) ^ ( Suppress("\n"))

