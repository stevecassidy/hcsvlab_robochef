import os
import shutil

from abc import ABCMeta, abstractmethod


class IngestBase(object):
    __metaclass__ = ABCMeta
    '''
    This abstract class is a representation of an ingest. It is being used in-lieu of an interface
    '''
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
      
    
    def clear_output_dir(self, outdir):
        ''' Clears the output directory '''
        if os.path.exists(outdir):
            shutil.rmtree(outdir)
        os.mkdir(outdir)
