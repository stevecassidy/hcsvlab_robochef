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
    
    corpus_basedir = configmanager.get_config("CORPUS_BASEDIR", "../input/")
    output_dir = configmanager.get_config("CORPUS_OUTPUTDIR", "../output/")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for c in corpra:
      
        if c == "art":
            print "converting ART"
            art = ARTIngest()
            art.setMetaData(corpus_basedir+"ART/ART-corpus-catalogue.xls")
            art.ingestCorpus(corpus_basedir+"ART", output_dir+"ART")
            
        elif c == "cooee":
            print "converting COOEE"
            cooee = CooeeIngest()
            cooee.setMetaData(corpus_basedir+"COOEE/COOEE.XLS")
            cooee.ingestCorpus(corpus_basedir+"COOEE/data", output_dir+"cooee")
            
        elif c == "ace":
            print "converting ace"
            ace = ACEIngest()
            ace.setMetaData(corpus_basedir+"ace/Manual")
            ace.ingestCorpus(corpus_basedir+"ace", output_dir+"ace")
            
        elif c == "ice":
            print "converting ice"      
            ice = ICEIngest()
            ice.ingest(os.path.join(corpus_basedir, "ICE"), os.path.join(output_dir, "ice")) 
            
        elif c == "monash": 
            print "converting monash"
            monash = MonashIngest()
            monash.ingestCorpus(corpus_basedir+"Monash Corpus of Australian English/Transcripts-sanitised", output_dir+"monash")
            
        elif c == "griffith":
            print "converting griffith"
            griffith = GriffithIngest()
            griffith.setMetaData(corpus_basedir+"griffith/metadata")
            griffith.ingestCorpus(corpus_basedir+"griffith", output_dir+"griffith")
            
        elif c == "md":
            print "converting mitchell & delbridge"
            md = MDIngest()
            md.setMetaData(corpus_basedir+"MD/flatfilesrc.txt")
            md.ingestCorpus(corpus_basedir+"MD", output_dir+"md")
            
        elif c == "auslit":
            print "converting auslit"
            auslit = AuslitIngest()
            auslit.ingestCorpus(corpus_basedir+"AusLit", output_dir+"auslit")
            
        elif c == "braided":
            print "converting braided channels"
            braided = BraidedIngest()
            braided.ingestCorpus(corpus_basedir+"braided_channels", output_dir+"braided")

if __name__ == "__main__":
    main()
