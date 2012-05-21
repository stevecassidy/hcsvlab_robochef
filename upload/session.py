from ausnc_ingest.upload.loginform import *
from ausnc_ingest.upload.formdecorator import *

import httplib2, urllib

class Session(object):
  '''
  This class manages the login session with the Plone server
  ''' 
  def __init__(self):
    # Initialise header information
    self.headers = {'Content-type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}

    self.authenticated = False
    
       
  def authenticate(self, url, username, password):
    '''
    Authenticates with the Plone server returning true or false depending on the success of authentication
    '''
    assert username != None or username != ""
    
    # Create an instance of the login form
    loginForm = FormDecorator(LoginForm())
    
    try:
      response, content = loginForm.submit(url, self.headers, None, username, password, None)

      if response.has_key('set-cookie') and response['set-cookie'].find('_ac') != -1:
        # Add the cookie to the header, we should now be able to access protected resources
        self.headers['Cookie'] = response['set-cookie']
        self.authenticated = True
        return True
    
      return False
        
    except:
      
        # If an exception is raised, assume an authentication failure
        return False
        # raise
    
    
  def inSession(self):
    '''
    Tells the caller is the session is activate or not
    '''
    return self.authenticated

    
  def getHeaders(self):
    '''
    Returns the current request headers
    '''
    return self.headers