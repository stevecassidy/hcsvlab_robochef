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

    def copy_collection_metadata(self, srcdir, outdir, filename, savename):
        ''' Copies the collection level metadata file to output directory '''
        print "    copying collection level metadata file..."
        metadata_file = os.path.join(srcdir, filename)
        if os.path.exists(metadata_file) and os.path.exists(outdir):
            shutil.copyfile(metadata_file, os.path.join(outdir,savename))
