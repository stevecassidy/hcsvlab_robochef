from hcsvlab_robochef import configmanager
from hcsvlab_robochef.upload.form import *

import httplib2, urllib

class LoginForm(Form):

  '''
  A login form is a type of form
  '''
  def submit(self, url, headers, contextual_uri, username, password, charset = None):   
    ''' 
    Declare Plone form field names 
    '''
    formFields = urllib.urlencode({'__ac_name': username, \
                                  '__ac_password': password, \
                                  'cookies_enabled': '1', \
                                  'js_enabled': '0', \
                                  'form.submitted': '1'})
    
                           
    # Create and http object and use it to obtain the session cookie
    http = httplib2.Http('.cache')
    return http.request(url, 'POST', headers = headers, body = formFields)