import httplib2
import logging
import urllib

from ausnc_ingest import configmanager
from ausnc_ingest.upload.multipartform import *
from ausnc_ingest.upload.form import *
from ausnc_ingest.upload.uploadexception import *


class AdminRDFUploadForm(Form):
    
  def submit(self, url, session, graph_uri, fileName, fullPath, charset = None): 
    ''' 
    The MultiPartForm is used to upload files. Though the PostRequest supports file uploads I am trying this for the moment 
    
    The charset is not required for the rdf upload at this stage as the server seems to have no issues with our use
    of unicode
    '''
    
    form = MultiPartForm()
    form.add_field('form.widgets.graph-empty-marker', '1')
    form.add_field('form.widgets.newgraph', graph_uri)
    form.add_field('form.widgets.replace-empty-marker', '1')
    form.add_field('form.widgets.format:list', 'n3')
    form.add_field('form.widgets.format-empty-marker', '1')
    form.add_field('form.buttons.upload', 'Upload')
    
    form.add_file('form.widgets.filedata', 'fileName', open(fullPath, "rb"))
    
    body = str(form)
    
    headers = session.getHeaders()
    headers['Content-type'] = form.get_content_type()
    headers['Content-length'] = str(len(body))

    http = httplib2.Http('.cache')
    response, content = http.request(url, 'POST', headers = headers, body = body)
    
    if 'status' in response.keys():
      print 'Graph Uri for file ', fileName, ' is ', graph_uri
      print 'Response status for rdf upload ', response['status']
      
    if self.isValidUploadResponse(response):
      print "\033[2K   ", fileName, " uploaded"
      self.logger.info('Key:' + fileName + ' Message: uploaded successfully')
      return response
    
    ''' If we cannot obtain a valid response then raise an exception '''
    raise UploadException('Could not upload ' + fullPath + ' which returned ' + response['status'] + ' code ')
