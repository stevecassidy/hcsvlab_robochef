from ausnc_ingest.utils.filehandler import *

import os
import sys
import re
import tempfile

class Statistics(object):

  def get_item_stats(self, source):
    # To calculate the size of a source string we place it in a temporary file
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(source.encode("utf-8"))       
    f.close()
    
    # After we store the file size we need to delete the file
    filesize = os.path.getsize(f.name)
    os.unlink(f.name)
    
    return filesize
  
  
  def get_file_stats(self, path):
   ''' Gets the file statistics '''
   file_handler = FileHandler()
   return file_handler.getFileSize(path)

  
  def append_item_stats(self, source, meta_dict):
    ''' 
    Appends the item level statistics to the meta dictionary 
    '''
    meta_dict['filewordcount'] = self.get_sample_wordcount(source)
    meta_dict['filesize'] = self.get_item_stats(source)
    
  
  def append_file_stats(self, path, meta_dict):
    ''' 
    Appends the item level statistics to the meta dictionary 
    '''
    word_count = self.get_word_count(path)

    file_handler = FileHandler()
    file_size = file_handler.getFileSize(path)
    
    meta_dict['filewordcount'] = word_count
    meta_dict['filesize'] = file_size
  
  
  def get_word_count(self, path):
    ''' 
    This method returns the word count of a file. At present this method only supports txt files.
    If a raw file contains XML tags, the tags are removed in the word count. Words separated by
    hyphens are treated as a single word.
    '''
    file_handler = FileHandler()
    
    # If the file is empty then just return 0
    if file_handler.getFileSize(path) == 0:
      return 0
      
    extension = os.path.splitext(path)   
    if extension[1] != '.txt':
      return 0
      
    # Open the file and perform a word count
    lines = open(path, 'r').read()
    return self.get_sample_wordcount(lines) 
    
    
  def get_sample_wordcount(self, lines):
    '''
    Function calculates the number of words in document. HTML tags are ignored in the count. Words
    that are separated by a hyphen are counted as a single word
    '''
    raw_lines = re.sub(r'<.*?>', ' ', lines)
    match = re.findall(r'[\w\-]+', raw_lines)
          
    return len(match)
    