from ausnc_ingest.utils.filehandler import *

import shutil
import os

class Organiser(object):
  '''
  This class is responsible for re-organising the MD source data files into a structure that is easier
  to navigate and manager.
  '''
  def organise(self, srcdir, outdir):
    
    # Check if the outdir exists, if not create it
    if not os.path.exists(outdir):
      os.makedirs(outdir)
      
    file_list = self.get_file_list(srcdir)
    dir_names = self.get_data_keys(outdir, file_list)
    self.__make_toplvl_dir__(dir_names)
    
    # Now copy the files from the source to the outdir by key
    for key, value in file_list.iteritems():
      shutil.copy(value, dir_names[self.__get_file_dirkey__(key)])
    

  def get_data_keys(self, outdir, fileList):
    '''
    Function builds a unique list of data keys, these keys are based on the file names from which the 
    first three alphanumeric characters are extracted
    '''
    key_list = {}
    
    for key in fileList.iterkeys():
      shortened_key = self.__get_file_dirkey__(key)
      if not shortened_key in key_list:
        key_list[shortened_key] = os.path.join(outdir, shortened_key)
  
    return key_list
  
  
  def get_file_list(self, srcdir):
    '''
    Function recurses through a folder in a topdown manner and retrieves all the source audio files
    including the annotations
    '''
    file_handler = FileHandler()
    return file_handler.getFiles(srcdir, inclusionPredicate = r'\w+', exclusionPredicate = r'.DS_Store')
    
    
  def __make_toplvl_dir__(self, dir_names):
    '''
    This function makes a series of directories at a single level using outdir as its reference folder.
    '''
    for key, value in dir_names.iteritems():
      if not os.path.exists(value):
        os.makedirs(value)
    

  def __get_file_dirkey__(self, name):
    '''
    Helper function which obtains the key from a file name, this is based on the first 3 alpha-numeric
    characters of the file name
    '''
    if len(name) > 2:
      return name[0:3]
    else:
      return name
  
  
if __name__=='__main__':
    import sys
    
    if len(sys.argv) != 3:
        print "Usage: organiser.py <inputdir> <outputdir>"
        exit()
        
    o = Organiser()
    o.organise(sys.argv[1], sys.argv[2])