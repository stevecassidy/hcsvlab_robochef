import httplib, urllib, urllib2, cookielib

class PostRequest(GetRequest):
    '''
    This class is used to perform an http post to a Plone server. In this implementation
    a POST is a type of GET request with some additional handlers
    '''   
    def __init__(self, url, headers, data):
      '''
      A Post request is a type of Get request in our implementation, so we chain the constructors
      explicitly
      '''
      super(Post, self).__init__(url, headers) 
      self.request.add_data(urllib.urlencode(data))