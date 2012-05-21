from HTMLParser import HTMLParser

import re

class AceHTMLParser(HTMLParser):
    '''
    This class is used to parse Ace meta data files which are in XML format. It works on such documents
    which comprise of a HTML table consisting of 3 columns (anything other than 3 columns will fail).
    In this 3 column format the first column can be empty or can consist of the sample id. The second
    column can consist of an empty value, a title, the source or publisher. The third column can consist
    of an empty value or the articles author.
    
    The design of this class is based on the HTMLParser from the Python library. This class is event
    driven and hence requires state as such is the nature of event driven code.
    '''
  
    nth_row = nth_column = 0
    meta_data = {}
    current_source = current_sample_id = None
    group_ids = ()
    is_title_row = publisher_obtained = False
    pub_date = ''


    def __init__(self):
      HTMLParser.__init__(self) 
      self.meta_data = {}   # This array is initialised during class initialisation again


    def handle_starttag(self, tag, attrs):  
        ''' 
        Event fires and handles the opening <tr>, <td> and <p> tags. All other tags are ignored 
        '''
        if tag == 'tr':
          self.is_title_row = False
          self.nth_column = 0
          self.nth_row = self.nth_row + 1
        elif tag == 'td':
          self.nth_column = self.nth_column + 1
          if self.nth_column == 3 and self.publisher_obtained:
            self.group_ids = ()
            self.publisher_obtained = False
        elif tag == 'p':
          self.val_present = True
 
          
    def handle_endtag(self, tag):
        ''' 
        Sets the global flag to say there is no current data to process 
        '''
        if tag == 'td' or tag == 'p':
          # If we see a closing td or p tag then we know there is no more data to process
          self.val_present = False

        
    def handle_data(self, data):
        '''
        Primary event which fires when data is present between HTML tags
        '''
      
        # Only process new rows, ignoring the header row (self.nth_row > 1) where there is a value 
        # and these values are not just a series of spaces
        if self.nth_row > 1 and self.val_present and not re.search('^\s+$', data):
               
          if self.nth_column == 1:      
            # Start of a new sample
            self.is_title_row = True
            self.current_sample_id = self.__cleanse_sample__(data)            
            
            self.__add_sample__(self.current_sample_id)
            
            self.meta_data[self.current_sample_id] = {}
            
          elif self.nth_column == 2:    
            # Processing of title, source or publication
            if self.is_title_row:
              self.__add_title__(self.current_sample_id, data)
            else:
              self.__add_sourceorpublication__(self.current_sample_id, data)
              
          elif self.nth_column == 3:    # Processing of author
                
            if 'Author' in self.meta_data[self.current_sample_id]:
              self.meta_data[self.current_sample_id][u'Author'] = self.meta_data[self.current_sample_id][u'Author'].strip() + ' and ' + data.strip()
            else:
              self.meta_data[self.current_sample_id][u'Author'] = data.strip()


    def get_meta(self):
      return self.meta_data


    def extract_date(self, source):
      ''' 
      Function extracts a date from a source string. This function only supports 2 formats at present.
      dd months_in_words yyyy or yyyy only.
      '''
      if re.search(r'\d+\s+\w+\s+\d{2,4}', source):
        return re.findall(r'\d+\s+\w+\s+\d{2,4}', source)
      
      if re.search(r'\s\d{4}\s', source):
        return re.findall(r'\s\d{4}\s', source)

      return []

     
    def __cleanse_sample__(self, sample_id):
      ''' 
      The ACE sample id's are surrounded by () brackets. This function removes those () 
      '''
      stage1 = sample_id.replace('(', '')
      return stage1.replace(')', '').strip()
      

    def __cleanse_wordcount__(self, wordcount):
      '''
      Word counts are included with either the source or title, this method
      extracts the word count from these fields.
      '''
      res = re.findall(r'(\d+\swords)', wordcount)
      if len(res) > 0:
        return res[0]
      
      return ''

      
    def __add_title__(self, sample_id, data):
      
      values = data.partition('(')
      self.meta_data[sample_id][u'Title'] = values[0].strip()
      
      # If we cannot obtain the word count from the title, just pluck it out of the source
      if self.__cleanse_sample__(values[1] + values[2]).strip() != '':
        self.meta_data[sample_id][u'Word Count'] = self.__cleanse_wordcount__(values[1] + values[2]).strip()
      else:
        values = self.current_source.strip().partition('(')
        self.meta_data[sample_id][u'Word Count'] = self.__cleanse_wordcount__(values[1] + values[2]).strip()
        
        
    def __add_sourceorpublication__(self, sample_id, data):
      
      # Source fields always contain a word count
      if re.search('\(\d+\swords\)$', data.strip()):
        
        self.__update_group__()

        # We are now most likely processing source details details
        self.current_source = data.strip()
        
        pub_date = self.extract_date(self.current_source) # Store the publication date as it might be useful for later
        if len(pub_date) > 0:
          self.pub_date = pub_date[0].strip()
        
      else:
        
        pub_date = self.extract_date(data.strip())
        if len(pub_date) > 0:
          
          for val in self.group_ids:
            if not 'Publication Date' in self.meta_data[val]:
              self.meta_data[val][u'Publication Date'] = self.pub_date
              
          self.pub_date = pub_date[0].strip()
          
        else:
          
          self.__update_group__()
          
          for val in self.group_ids:
          
            if 'Publisher' in self.meta_data[val]:
              self.meta_data[val][u'Publisher'] = self.meta_data[val][u'Publisher'].strip() + ' & ' + data.strip()
            else:
              self.meta_data[val][u'Publisher'] = data.strip()
        
          self.publisher_obtained = True


    def __update_group__(self):
      '''
      A group might be divided in the source data into sections, each section will present new information
      pertaining to the group. This information includes document source and publication date. This function
      updates the current group with this information prior to a section change.
      '''
      for val in self.group_ids:
          
        # Only update the source when we back track if the sample has no such data
        if not 'Source' in self.meta_data[val]:
          self.meta_data[val][u'Source'] = self.current_source.strip()
          
        if not 'Publication Date' in self.meta_data[val]:
          self.meta_data[val][u'Publication Date'] = self.pub_date


    def __add_sample__(self, sample_id):
      '''
      Adds the sample id to the group id list, if however the sample signifies the start of a new group, we reset the list
      '''
      sample_numeric_val = re.findall(r'\d+', sample_id)
     
      for group_id in self.group_ids:
        group_id_numberic_val = re.findall(r'\d+', group_id)
        if sample_numeric_val != group_id_numberic_val:
          self.group_ids = ()
          
      self.group_ids = self.group_ids + (sample_id,)