import sys
import logging

from ausnc_ingest.cooee.ingest import *
from ausnc_ingest.ace.ingest import *
from ausnc_ingest.ice.ingest import *
from ausnc_ingest.monash.ingest import *
from ausnc_ingest.griffith.ingest import *
from ausnc_ingest.md.ingest import *
from ausnc_ingest.auslit.ingest import *
from ausnc_ingest.braided.ingest import *
from ausnc_ingest.art.ingest import *

from ausnc_ingest import utils
from ausnc_ingest import configmanager

def main():
    '''
    Primary application entry point
    '''
    corpra = utils.getCorporaArgs(sys.argv)
    
    print "cpr: corpora conversion tool\n"
    
    ''' Configure the logger and the configuration manager '''
    configmanager.configinit()
    logging.basicConfig(filename='ausnc_ingest.log', level=logging.INFO, format='%(asctime)s %(message)s')
    
    for c in corpra:
      
        if c == "art":
            print "converting ART"
            art = ARTIngest()
            art.setMetaData("../input/ART/ART-corpus-catalogue.xls")
            art.ingestCorpus("../input/ART", "../output/ART")
            
        elif c == "cooee":
            print "converting COOEE"
            cooee = CooeeIngest()
            cooee.setMetaData("../input/COOEE/COOEE.XLS")
            cooee.ingestCorpus("../input/COOEE/data", "../output/cooee")
            
        elif c == "ace":
            print "converting ace"
            ace = ACEIngest()
            ace.setMetaData('../input/ace/Manual')
            ace.ingestCorpus("../input/ace", "../output/ace")
            
        elif c == "ice":
            print "converting ice"      
            ice = ICEIngest()
            ice.setWrittenMetaData("../input/ICE/metadata")
            ice.setMetaData("../input/ICE/metadata")
            ice.ingestCorpus("../input/ICE/standoff", "../output/ice")
            
        elif c == "monash": 
            print "converting monash"
            monash = MonashIngest()
            monash.ingestCorpus("../input/Monash Corpus of Australian English/Transcripts-sanitised", "../output/monash")
            
        elif c == "griffith":
            print "converting griffith"
            griffith = GriffithIngest()
            griffith.setMetaData("../input/griffith/metadata")
            griffith.ingestCorpus("../input/griffith", "../output/griffith")
            
        elif c == "md":
            print "converting mitchell & delbridge"
            md = MDIngest()
            md.setMetaData("../input/MD/flatfilesrc.txt")
            md.ingestCorpus("../input/MD", "../output/md")
            
        elif c == "auslit":
            print "converting auslit"
            auslit = AuslitIngest()
            auslit.ingestCorpus("../input/AusLit", "../output/auslit")
            
        elif c == "braided":
            print "converting braided channels"
            braided = BraidedIngest()
            braided.ingestCorpus("../input/braided_channels", "../output/braided")

if __name__ == "__main__":
    main()
