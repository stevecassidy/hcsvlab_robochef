import os
import shutil
import logging

from abc import ABCMeta, abstractmethod
from hcsvlab_robochef import configmanager


class IngestBase(object):
    __metaclass__ = ABCMeta
    '''
    This abstract class is a representation of an ingest. It is being used in-lieu of an interface
    '''

    configmanager.configinit()
    logger = logging.getLogger('parsers')
    handler = logging.FileHandler('corpus_parsers.log', mode='w')
    logger.addHandler(handler)

    def __init__(self, corpus):
        self.corpus = corpus
        self.raw_plain_const = float(configmanager.get_config('C_' + corpus, 0))
        self.raw_plain_th_ratio = float(configmanager.get_config('TH_' + corpus, 0.3))


    @abstractmethod
    def setMetaData(srcdir):
        ''' Loads the meta data for use during ingest '''
        return None
      
    
    @abstractmethod
    def ingestCorpus(srcdir, outdir):
        '''
        The ingest entry point where an input and output directory is specified 
        '''
        return None
      
      
    @abstractmethod
    def ingestDocument(sourcepath):
        '''
        Ingest a specific source document, from which meta-data annotations and raw data is produced
        '''
        return None
      
    def check_filesize_ratio(self, plain_text, raw_text, filename):
        """
        Performs a sanity check to see if there is a massive difference between the raw text and plain
        text files, which might indicate that something has gone wrong in the parsing.
        """
        ratio = (len(plain_text) + 0.0) / (len(raw_text) - self.raw_plain_const)
        print "%s, %s, %s" % (self.corpus, ratio, self.raw_plain_th_ratio)
        if ratio < self.raw_plain_th_ratio:
             self.logger.warn("%s: plain to raw ratio warning (%.2f < %.2f): %s" % (self.corpus, ratio,
                                                                                   self.raw_plain_th_ratio, filename))


    def clear_output_dir(self, outdir):
        ''' Clears the output directory '''
        if os.path.exists(outdir):
            shutil.rmtree(outdir)
        os.mkdir(outdir)

    def copy_collection_metadata(self, srcdir, outdir, filename, savename):
        ''' Copies the collection level metadata file to output directory '''
        print "    copying collection level metadata file..."
        metadata_file = os.path.join(srcdir, filename)
        if os.path.exists(metadata_file) and os.path.exists(outdir):
            shutil.copyfile(metadata_file, os.path.join(outdir,savename))
