import sys

sys.path.append('../')

#import logging
#import ausnc_ingest

from ausnc_ingest import configmanager
from ausnc_ingest.utils import *
from ausnc_ingest.utils.filehandler import *
from ausnc_ingest.upload.session import *
from ausnc_ingest.upload.adminrdfuploadform import *
from ausnc_ingest.upload.corpusitemuploadform import *
from ausnc_ingest.upload.helper import *
from ausnc_ingest.upload.resolver import *


supported_collections = ['ace', 'art', 'md', 'griffith', 'auslit', 'braided', 'cooee', 'ice', 'monash']

helper = Helper()
resolver = Resolver()


def corpus_item_upload(form, session, meta_path, corpusuploadUrl, folder_loc, uploaded_files, charset = None):

  # We use the dc:title if one is available if not we use dc:identifier
  # where one is not available
  upload_title = resolver.get_title(meta_path)
  if upload_title == '':
      upload_title = resolver.get_identifier(meta_path)
      
  source_files = resolver.get_upload_units(meta_path)

  # Then iterate the files that required uploading and upload them
  for file_name in source_files:
      subject_uri = resolver.get_subject_uri(meta_path, file_name)

      file_path = os.path.join(folder_loc, file_name)
      if not os.path.isfile(file_path):
        print "Ignoring not existing file %s" + file_path
        continue

      if not helper.is_uploaded(file_name, uploaded_files):

          print 'About to upload ', file_name

          # We need to update the title to specify the type of document
          updated_upload_title = upload_title + ' (' + resolver.get_document_type(meta_path, subject_uri) + ')'
        
          form.submit(corpusuploadUrl, session, subject_uri, updated_upload_title, file_path, charset)
      
          if not helper.is_uploaded(file_name, uploaded_files):
              uploaded_files[file_name] = ''
                

def rdf_upload(form, session, rdf_file, rdf_path, uploadUrl, item_uri, uploaded_files):
  """ Method assists the upload process for rdf files """
  
  if not helper.is_uploaded(rdf_file, uploaded_files):

      print 'About to upload ', rdf_file

      form.submit(uploadUrl, session, item_uri, rdf_file, rdf_path, None)
      if not helper.is_uploaded(rdf_file, uploaded_files):
          uploaded_files[rdf_file] = ''


def main():
    ''' Primary application entry point for uploading of collection rdf files '''
    
    print "Corpora upload tool "
  
    if len(sys.argv) < 5:
        print 'Insufficient Parameters, please provide a collection name (e.g. ace, md etc), the name of the corpus folder, the location of the files to upload and a True or False value indicating whether corpus documents require uploading.'
        print 'Example: python uploader.py cooee cooee ../output/cooee True'
        return
  
    # Example command: python uploader.py md mdtest '/Users/Shirren/Desktop/md/S00/ True'
    # First parameter (i.e. md) is the name of the collection, this value should be reflected in the supported_collections dictionary
    # Second parameter (i.e. mdtest) is the name of the corpus folder in Plone
    # Third paramter is the location of the files
    collection_name = sys.argv[1].strip()
    corpus_folder_name = sys.argv[2].strip()
    folder_loc = sys.argv[3].strip()
    upload_corpus_doc = sys.argv[4].strip().lower() == 'true'
  
    print 'Parameters: Collection Name->', collection_name, \
          ' Corpus Folder Name->', corpus_folder_name, \
          ' Location of Upload Files->', folder_loc, \
          ' Upload Corpus Documents->', upload_corpus_doc
  
    if collection_name in supported_collections:
  
        # Initialise configuration file and grab reference data for the upload. This reference data
        # also includes the files we have already uploaded which comes from the log files in the tmp folder
        configmanager.configinit("griffithconfig.ini")
        uploaded_files = helper.get_uploaded_files(collection_name)
        (loginUrl, uploadUrl, corpusuploadUrl) = helper.get_required_urls(corpus_folder_name)
  
        # Get the file we would like to upload for a particular collection
        fileHandler = FileHandler()
        fileList = sorted(fileHandler.getFiles(folder_loc, r'^.+-metadata.rdf$'))
    
        print 'Attempting Authentication using ', loginUrl
    
        session = Session()
        session.authenticate(loginUrl, configmanager.get_config("USERNAME"), configmanager.get_config("PASSWORD"))

        # Authentication successful proceed with the upload
        if session.inSession():

            print "Authenticated and pushing data up for ", collection_name
      
            # Switched to the new upload form
            rdfForm = FormDecorator(AdminRDFUploadForm(), collection_name)        # Collection name is used for the logger
            corpusForm = FormDecorator(CorpusItemUploadForm(), collection_name)
    
            for meta_file in fileList:       
        
                meta_path = os.path.join(folder_loc, meta_file)
                ann_file = helper.derive_annotation_filename_from_meta_filename(meta_file)
                ann_path = os.path.join(folder_loc, ann_file)
        
                item_uri = resolver.get_item_uri(meta_path)
                source_files = resolver.get_upload_units(meta_path)
    
                # Now upload the meta data file and annotation file
                rdf_upload(rdfForm, session, meta_file, meta_path, uploadUrl, item_uri, uploaded_files)
                rdf_upload(rdfForm, session, ann_file, ann_path, uploadUrl, item_uri, uploaded_files)
                
                # Only upload corpus documents if asked too
                if upload_corpus_doc:
                  
                  # As cooee is a one-off special case at this moment I am using a simple if statement, if more
                  # complex character set determination is required then we can refactor this code
                  if collection_name == 'cooee':
                    corpus_item_upload(corpusForm, session, meta_path, corpusuploadUrl, folder_loc, uploaded_files, 'ISO-8859-1')
                  else:
                    corpus_item_upload(corpusForm, session, meta_path, corpusuploadUrl, folder_loc, uploaded_files)
          
        else:
            print 'Authentication failure for user: ', configmanager.get_config("USERNAME"), ' with password ', configmanager.get_config("PASSWORD")
  
    else:
        print collection_name + " is an unsupported collection type."
    

if __name__ == "__main__":
    main()
