from ausnc_ingest.upload.uploadexception import *

import logging
import os

class FormDecorator(object):
  '''
  This class is used to decorate Form classes with logging behaviour
  '''
  def __init__(self, form, collection = 'ausnc_ingest'):
    '''
    Track the form to be decorated. Also set the logger based on the current collection name
    '''
    self.form = form
    
    self.logger = logging.getLogger(collection)
    hdlr = logging.FileHandler(os.path.join('/var/tmp', collection + '.log'))
    formatter = logging.Formatter('%(asctime)s %(message)s')
    hdlr.setFormatter(formatter)
    self.logger.addHandler(hdlr) 
    self.logger.setLevel(logging.DEBUG)

    self.form.set_logger(self.logger)


  def submit(self, url, session, contextual_uri, param1, param2, param3):
    '''
    Re-directs the call to the concrete implementation, but wraps the call in some standard
    logging code which traps exceptions. This allows the calling code to proceed except in
    the event of some fatal failure.
    '''
    try:
      return self.form.submit(url, session, contextual_uri, param1, param2, param3)
    
    except IOError as (errno, strerror):
      ''' Log the exception '''
      self.logger.error('Form ' + str(type(self.form)) + ' failed with message ' +\
                          strerror + ' and error no ' + str(errno) +\
                          ' with data, param1: ' + param1 + ' and param2: ' + param2)
                          
    except UploadException as e:
      ''' Log the exception '''
      self.logger.warning('Form ' + str(type(self.form)) + ' failed with message ' +\
                          e.parameter + ' with data, param1: ' + param1 + ' and param2: ' + param2)