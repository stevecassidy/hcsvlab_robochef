import httplib2
import logging
import urllib

from hcsvlab_robochef import configmanager
from hcsvlab_robochef.upload.multipartform import *
from hcsvlab_robochef.upload.form import *
from hcsvlab_robochef.upload.uploadexception import *


class RDFUploadForm(Form):
    
  def submit(self, url, session, fileName, fullPath): 
    ''' 
    The MultiPartForm is used to upload files. Though the PostRequest supports file uploads I am trying this for the moment 
    '''
    form = MultiPartForm()
    
    # form.add_field('form.widgets.replace:list', 'selected')
    form.add_field('form.widgets.replace-empty-marker', '1')
    form.add_field('form.widgets.format:list', 'n3')
    form.add_field('form.widgets.format-empty-marker', '1')
    form.add_field('form.buttons.upload', 'Upload')
    form.add_file('form.widgets.file', fileName, open(fullPath, "rb"))
    
    body = str(form)
    
    headers = session.getHeaders()
    headers['Content-type'] = form.get_content_type()
    headers['Content-length'] = str(len(body))

    http = httplib2.Http('.cache')
    response, content = http.request(url, 'POST', headers = headers, body = body)
    
    if self.isValidUploadResponse(response):
      print "\033[2K   ", fileName, " uploaded"
      self.logger.info('Key:' + fileName + ' Message: uploaded successfully')
      return response
    
    ''' If we cannot obtain a valid response then raise an exception '''
    raise UploadException('Could not upload ' + fullPath)