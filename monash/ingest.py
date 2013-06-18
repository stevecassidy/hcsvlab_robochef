import codecs
import re
import doctest
import subprocess
import pprint
import sys
import os
import shutil 

from hcsvlab_robochef import utils
from hcsvlab_robochef import metadata
from hcsvlab_robochef.ingest_base import IngestBase
from hcsvlab_robochef.annotations import *
from hcsvlab_robochef.utils.serialiser import *
from hcsvlab_robochef.utils.statistics import *

from pyparsing import *
from rdf import monashMap


class MonashIngest(IngestBase):


  META_DEFAULTS = {'language': 'eng'}

  def setMetaData(self, srcdir):
    ''' Loads the meta data for use during ingest '''
    pass
    
    
  def ingestCorpus(self, srcdir, outdir):
  
    print "  converting corpus in", srcdir, "into normalised data in", outdir
    print "    clearing and creating output location"
  
    self.clear_output_dir(outdir)
    
    file_handler = FileHandler()
    res = file_handler.getFiles(srcdir, r'^[\w\d-]+\.doc$', r'^.DS_Store$')
    
    sofar = 0
    total = len(res)
  
    print "    processing files..."
  
    for name, f in res.items():
      print "\033[2K   ",sofar, "of", total, f, "\033[A"
      
      (basename, rawtext, body, meta, annotations) = self.ingestDocument(f)
      meta.update(self.META_DEFAULTS)
    
      source_file = f
      f = f.replace(srcdir, outdir, 1)
      try:
        os.makedirs(os.path.dirname(f))
      except:
        pass
      ff = os.path.abspath(f)
    
      # Serialise the documents to rdf documents and write the output to disk
      self.__serialise(srcdir, os.path.dirname(ff), source_file, basename, name, rawtext, body, meta, annotations)
         
      sofar += 1
      
    print "\033[2K   ", total, "files processed"       
       
         
  def ingestDocument(self, f):
    """
    This function is responsible for sending the text off to be parsed and converting the
    result into our AST (such as it is).  The "AST" is an array of (arrays of) strings.  This
    function will grow to build more suitable data structures as we need them.  In fact, by now
    it might already be doing so.
    """
  
    text = subprocess.check_output(["antiword",f])
    print text
    text = text.decode('utf-8')

    u = open("monash_last_data.txt", 'w')
    u.write(text.encode('utf-8'))
    u.close
      
    res, bodyres = self.__parseData(text)  
    topTable = res["topTable"]
    
    if "bottomTable" in res:
      bottomTable = res["bottomTable"]
    else:
      bottomTable = {}

    if "notes" in res:
      notes = "\n".join(res["notes"])
    else:
      notes = ""

    if "transcriptionNotes" in bodyres:
      transcription_notes = bodyres["transcriptionNotes"]
    else:
      transcription_notes = ""
      
    body = bodyres["body"]
    
    md = dict({u'notes':notes, u'transcription_notes': transcription_notes})
    md.update(topTable)
    md.update(bottomTable)
  
    # code gives the main participant identifier, usually with a trailing .X  where X in [12AB]
    # but in one case there's no following stuff and in another it's :.A 
    mcode = re.search("([A-Z0-9]+)([.:][12AB])?", topTable['CODE:'])
    if mcode:
        mainspeaker = mcode.groups()[0]

    # generate descriptions of all the participants as table_person
    participants = dict()
    for p in res["participants"]: 
        if p == mainspeaker:
            # copy over participant metadata
            info = {'id': p, 
                    'role': 'primary',
                    'gender': md.get('SEX:',""),
                    'age': md.get('AGE:', ""),
                    'school': md.get('SCHOOL:', ""),
                    'birthplace': md.get('BIRTHPLACE:', ""),
                    'initials': md.get("STUDENT'S INITIALS:", ""),              # FIXME: doesn't work because it's not
                    'fathers_ethnicity': md.get("Father's Ethnicity", ""),      # a ' char, same for other *Ethnicity fields 
                    }
            participants['table_person_main'] = info
        else:
            suffix = p[len(mainspeaker):]
            if suffix == "Mo": 
                info = {'id': p, 'gender': 'female', 'relationship': 'mother'}
                participants['table_person_mother'] = info
            elif suffix == "Fa": 
                info = {'id': p, 'gender': 'male', 'relationship': 'father'}
                participants['table_person_father'] = info
            elif suffix.startswith("B"):
                info = {'id': p, 'gender': 'male', 'relationship': 'brother'}
                participants['table_person_%s' % suffix] = info
            elif suffix.startswith("S"):
                info = {'id': p, 'gender': 'female', 'relationship': 'sister'}
                participants['table_person_%s' % suffix] = info
            elif suffix.find("m") >= 0:
                info = {'id': p, 'suffix': suffix, 'gender': 'male'}
                participants['table_person_%s' % suffix] = info
            elif suffix.find("f") >= 0:
                info = {'id': p, 'suffix': suffix, 'gender': 'female'}
                participants['table_person_%s' % suffix] = info
            else:
                info = {'id': p, 'suffix': suffix}
                participants['table_person_%s' % suffix] = info
  
  
    md.update(participants)
  
    # all monash samples are interviews
    md['genre'] = 'interview'
  
    # extract annotations
    body, anns = self.__extractAnnotations(body, res["participants"])  
    md['sampleid'] = os.path.splitext(os.path.basename(f))[0]
    
    return (md['sampleid'], text, body, md, anns)


  def __serialise(self, srcdir, outdir, source_file, basename, name, rawtext, body, meta, annotations):
     '''
     This function serialises the data and returns the serialised graph object
     '''
     file_handler = FileHandler()
     serialiser = Serialiser(outdir)

     # Now check to see if the text file has a compatriot audio file. If it does generate output
     # relevant to the presence of two such files
     compatriot = file_handler.findCompatriot(srcdir, name, r'^[\w\d-]+.wav$', r'^[\w\d-]+.doc$')

     if compatriot is not None:
       original_doc = { 'filetype': 'Text', 'sampleid': basename, 'rawtext': rawtext, 'text': body, 'sourcepath': source_file}        
       compatriot = { 'filetype': 'Audio', 'sampleid': basename, 'sourcepath': compatriot}
       return serialiser.serialise_multiple(basename, (original_doc, compatriot, ), 'monash', monashMap, meta, annotations)

     else:
       return serialiser.serialise_single(basename, 'monash', rawtext, body, monashMap, meta, annotations, source_file)
         
         
  def __extractAnnotations(self, data, participants):
    markups = oneOrMoreParsers( slurpParser(u'[@')                      \
                              ^ redactParser()                          \
                              ^ monashLaughterParser()                  \
                              ^ monashOverlapParser()                   \
                              )
    try:
      full_anns = None
      if participants:
        full_anns =  knownSpeakerParser(participants, markups).parseString(data)[0]
      else:
        full_anns =  speakerParser(markups).parseString(data)[0]
    except:
      f = open("monash_error_data.txt", 'w')
      f.write(data.encode('utf-8'))
      f.close
      raise
    return (full_anns.text, full_anns.anns)

    
  def __headerText(self):
    """
    Parser for reading in all the header text.  This is almost always the same, but we can just
    as safely read to the first pipe, so we do
    """
    return CharsNotIn("|")


  def __noteParser(self):
    """
    This function is a parser for notes.  Notes in the Monash corpus take diverse forms.  Depending on the decisions
    we make regarding cleaning the corpus, this will either be a very simple function, or a very complex one :)
    """
    return \
      (Suppress(u"{") + CharsNotIn(u"}") + Suppress(u"}")) \
      | (Suppress(u"(") + CharsNotIn(u")") + Suppress(u")")) \
      |                                                    \
      OneOrMore(Suppress(u"Note") + (SkipTo(Literal(u"Participants") | Literal(u"Note"))))


  def __participantParser(self):
    """
    Parses one line of the participant list
    """
    return (((Word(alphanums+"?") + Suppress(Optional(Literal(" (interviewer)")))) | Empty() ) + Suppress(Literal(u"\n")))


  def __dashedLine(self):
    """
    Parses the dashed lines that appear between the meta-data and transcript in some of the files
    """
    return (Word("_") | Word("-"))


  def __parseData(self, string):
    """
    Parses the whole document, after it has been converted to text
    """
    whole = Suppress(self.__headerText())                        \
          + utils.tableParser(4).setResultsName("topTable")     \
          + Optional(utils.tableParser(2).setResultsName("bottomTable"))                                        \
          + ZeroOrMore(self.__noteParser()).setResultsName("notes")                                              \
          + Optional(Suppress("."))                                                                       \
          + Suppress(ZeroOrMore(self.__dashedLine()))                                                            \
          + Suppress(Literal(u"Participant") + Optional(u"s") + Optional(u":")) + ZeroOrMore(Word(" \n")) \
          + OneOrMore(((self.__participantParser()).leaveWhitespace())).setResultsName("participants")    \
          + CharsNotIn(u"").setResultsName("remainder")
    
    partial = whole.parseString(string)

    def skip_to(participants):
      if participants:
        return Or([Literal(p) for p in participants]) + Literal(u":")
      else: 
        return Word(alphanums) + Literal(":")
          
    rest  = SkipTo(skip_to(partial["participants"]), False).setResultsName("transcriptionNotes") \
          + CharsNotIn(u"").setResultsName("body")
          
    return (partial, rest.parseString(partial["remainder"]))

