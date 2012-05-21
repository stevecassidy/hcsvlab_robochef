import urllib

from abc import ABCMeta, abstractmethod


class Form(object):
  __metaclass__ = ABCMeta
  '''
  This class is essentially an asbtract base class. All forms (i.e. loginForm) inherit
  from this form
  '''

  @abstractmethod
  def submit(self, url, session, contextual_uri, param1, param2, param3): 
    '''
    All forms implement this method, it is used to submit data to a dynamic
    url generated at runtime. This behaviour will be used in production
    '''
    return None
    

  def isValidUploadResponse(self, response):
    '''
    This method checks the http response to see if the server received the upload
    file successfully. Essentially it check to see if the response code is 302 (data received)
    and that it does not contain any Zope exceptions (aka bobo)
    '''
    
    if 'status' in response.keys():
      if response['status'] == '302':
        if not 'bobo-exception-value' in response.keys():
          return True
          
    return False
    
    
  def isValid(self, url):     
    ''' 
    Checks the validity of a url by performing a GET request. The response code
    to this request is asserted to be 200 for validity. 
    '''
    try:
      resource = urllib.urlopen(url)
    except:
      return False
      
    return resource.getcode() == 200
    
    
  def set_logger(self, logger):
    self.logger = logger