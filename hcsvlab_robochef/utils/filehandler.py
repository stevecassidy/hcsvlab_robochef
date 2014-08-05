import os
import re # Regular expression support

class FileHandler(object):
  
  
  def getFileSize(self, path):
    '''
    This method returns the size of a file. If a directory or missing file is passed in the method
    returns 0 bytes as the size.
    '''
    if not os.path.exists(path) or os.path.isdir(path):
      return 0 # if does not exist return 0 as size
      
    return os.path.getsize(path)
  
  
  def getFiles(self, path, inclusionPredicate = r'\w+\.rdf', exclusionPredicate = r'\w+-raw\.txt'):
    ''' 
    Returns files with the provided extension from the top level directory specified by the path. It
    also excludes any file whos name matches the exclusion predicate passed in the last parameter.
    '''
    
    returnList = {}
        
    for root, dirs, files in os.walk(path, topdown = True):
      # We ignore directories and only look at files
      
      for name in files: 
        # Only load a file with given name once, if for any reason a file appears
        # twice in our recursive traversal ignore the second (third etc etc) occurence
                
        if self.isMatch(name, inclusionPredicate, exclusionPredicate) and not (name in returnList):
          # Only process rdf files, give priority to those files in the top level
          # directory over those in nested directories
          returnList[name] = os.path.join(root, name)
          
        
    # We are done
    return returnList

  def getUniqueFiles(self, path, inclusionPredicate = r'\w+\.rdf', exclusionPredicate = r'\w+-raw\.txt'):
    '''
    Returns files with the provided extension from the top level directory specified by the path. It
    also excludes any file whos name matches the exclusion predicate passed in the last parameter.
    '''

    returnList = {}

    for root, dirs, files in os.walk(path, topdown = True):
      # We ignore directories and only look at files

      for name in files:
        # When files can have the same given name, but can still be uniquely identified by their paths
        if self.isMatch(name, inclusionPredicate, exclusionPredicate):
          returnList[(name, root)] = os.path.join(root, name)

    # We are done
    return returnList
 
    
  def isMatch(self, fileName, inclusionPredicate, exclusionPredicate):
    '''
    This method checks a file name to see if it matches the inclusion predicate and exclusion predicate. If a file
    name meets the inclusionPredciate and does NOT meet the exclusion predicate the function returns true. It returns
    false in all other cases.
    '''
    
    # Check for inclusion first
    match = re.search(inclusionPredicate, fileName)
    
    if match:
      
      # Now check for exclusion
      if re.search(exclusionPredicate, fileName) == None:
        
        return True
    
    return False;
    
    
  def findCompatriot(self, path, fileName, inclusionPredicate, exclusionPredicate):
    '''
    This function will attempt to find a compatrior file (i.e. Audio file) with a name similar to the original
    '''
    fileNameWithoutExt = os.path.splitext(fileName)[0]
    
    for root, dirs, files in os.walk(path, topdown = True):
      for name in files:
        # Check the file name to see if it is similar to the passed in file name
        if name.find(fileNameWithoutExt) != -1 and name != fileName:
          if self.isMatch(name, inclusionPredicate, exclusionPredicate):
            return os.path.join(root, name)
        
    
    # No compatriot file exists
    return None