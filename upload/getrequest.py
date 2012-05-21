import httplib, urllib, urllib2, cookielib

class GetRequest(object):
    '''
    This class is used to perform an http request with the Plone server
    '''  
    handlers = list()
    
    def __init__(self,url,session):
      '''
      No need for invariance checking, if the url and headers are invalid then
      the connection will fail
      '''     
      assert session != None
      
      self.url = url
      
      ''' Note how we use the session cookie by grabbing the headers from the session '''
      self.request = urllib2.Request(url, headers = session.getHeaders()) 


    def submit(self):
        try:
            opener = urllib2.build_opener(*self.handlers)
            
            response = opener.open(self.request)
            to_return = {
                'code': response.code,
                'contents': response.read(),
                'url': response.geturl(),
                'headers': dict(response.info())
            }
          
        except urllib2.URLError as e:
            if hasattr(e, 'reason'):
                print 'Error accessing the server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                return {'code': getattr(e, 'code')}
        else:
            return to_return


    def _add_handler(self,handler):     
      self.handlers.append(handler)