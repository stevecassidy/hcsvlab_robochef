class UploadException(Exception):
  
  def __init__(self, value):
    ''' Custom Constructor '''
    self.parameter = value

  def __str__(self):
    ''' String message '''
    return repr(self.parameter)