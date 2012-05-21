import os
import re

from rdflib import Graph
from rdflib.term import URIRef
from ausnc_ingest import configmanager

class Helper(object):
    
     
  def derive_title(self, file_name):
   '''
   This method derives the title of a file from the filename by removing the extension and using
   the segment prior to the extension.
   '''
   return os.path.splitext(file_name)[0]
    
  
  def derive_annotation_filename_from_meta_filename(self, meta_file_name):
    '''
    This function returns the name of the annotation file when provided with the name of the meta file name
    '''
    return meta_file_name.replace('-metadata.rdf', '-ann.rdf')
    
    
  def get_uploaded_files(self, collection, base_path='/var/tmp'):
    '''
    This method looks up a local log file to determine which files have been uploaded already
    and returns them in a dictionary (Dictionary so the lookup time is O(1))
    '''
    uploaded_files = {}
    
    if not (os.path.exists(os.path.join(base_path, collection + '.log'))):
      return uploaded_files
      
    file_handle = open(os.path.join(base_path, collection + '.log'), 'r')
          
    for line in file_handle.readlines():
      # Match the file name for the successfully uploaded file
      text_segments = re.findall(r'(?<=Key:)(.*)(?=Message: uploaded successfully)', line)
      
      if len(text_segments) > 0:
        file_name = text_segments[0].replace('Key:', '')
        uploaded_files[file_name.strip()] = '' 
    
    return uploaded_files
      
  
  def is_uploaded(self, file_name, uploaded_files):
    ''' Method returns true is file name occurs in dictionary else false '''
    if file_name in uploaded_files:
      return True
    else:
      return False
      
    
  def build_url(self, template, collection_name):
    ''' This function builds a complete url from a template by inserting the collection name into the template '''
    new_url = template.replace('#COLNAME#', collection_name)
    return new_url
    
    
  def get_download_url(self, sampleid, collection_name):
    ''' This function builds the download url for a particular sample and collection '''
    configmanager.configinit()
    baseUrl = self.build_url(configmanager.get_config("BASEURL"), configmanager.get_config(collection_name))
    return baseUrl + sampleid
    
    
  def get_required_urls(self, corpus_folder_name):
    # If there are files to upload authenticate with the server      
    loginUrl = configmanager.get_config("LOGINURL")

    # 09/03/2012: Switched to the new upload form
    uploadUrl = self.build_url(configmanager.get_config("ADMINUPLOADURL"), corpus_folder_name)
    corpusuploadUrl = self.build_url(configmanager.get_config('CORPUSLOADURL'), corpus_folder_name)
    
    return (loginUrl, uploadUrl, corpusuploadUrl)