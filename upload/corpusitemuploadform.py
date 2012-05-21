import httplib2
import logging
import urllib

from ausnc_ingest import configmanager
from ausnc_ingest.upload.helper import *
from ausnc_ingest.upload.multipartform import *
from ausnc_ingest.upload.form import *
from ausnc_ingest.upload.uploadexception import *


class CorpusItemUploadForm(Form):


  def submit(self, url, session, subject_uri, title, fullPath,  charset = None):   
    ''' 
    The MultiPartForm is used to upload files. Though the PostRequest supports file uploads I am trying this for the moment 
    '''
    fileName = os.path.basename(fullPath)
    
    form = MultiPartForm()    
    form.add_field('form.widgets.IDublinCore.title', title)
    form.add_field('form.widgets.IRDFMetadata.subjecturi', subject_uri)
    form.add_field('form.buttons.save', 'Save')
    form.add_field('form.buttons.cancel', 'Cancel')
    form.add_file('form.widgets.itemcontent', fileName, open(fullPath, "rb"), charset = charset)
      
    body = str(form)
    
    headers = session.getHeaders()
    headers['Content-type'] = form.get_content_type()
    headers['Content-length'] = str(len(body))

    http = httplib2.Http('.cache')
    response, content = http.request(url, 'POST', headers = headers, body = body)

    if 'status' in response.keys():
      print 'Response status for content upload ', response['status']
      
    if self.isValidUploadResponse(response):
      print "\033[2K   ", fileName, " uploaded"
      self.logger.info('Key:' + fileName + ' Message: uploaded successfully')
      return response

    ''' If we cannot obtain a valid response then raise an exception '''
    raise UploadException('Could not upload ' + fullPath + ' which returned ' + response['status'] + ' code ')
    
    