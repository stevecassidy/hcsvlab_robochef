class Sample(object):
    
    def __init__(self, fromArray):
        """ The Sample object serves to wrap the array construct containing
        the raw information from the parser """
        self.sample = fromArray
        self.current = 0
    
    
    def __iter__(self):
        """ Method conforming to the iterator interface in Python """
        return self

    
    def next(self):
        """ This method iterates through a given sample returning the speaker label
        and then speaker text for each iteration. """
        if self.current + 1 >= len(self.sample):
            raise StopIteration
        else:
            res = (self.sample[self.current], self.sample[self.current + 1])
            self.current += 2
            return res
        
        
    def extractRawText(self):
        """ This function returns the raw text for the sample """
        rawData = u''
        for item in self.sample:
            if not isinstance(item, basestring):
                rawData += '['
                for subItem in item:
                    rawData += subItem + ' '
                rawData = rawData.strip()
                rawData += ']'
            else:
                rawData += item + '\n\n'
            
        return rawData
        
    
    def getPrimarySpeaker(self):
        """ This method returns the name of the primary presenter or Presenter 1 """
        firstSpeaker = self.sample[0]
        secondSpeaker = self.sample[2]

        if 'Presenter' in firstSpeaker[0]:
            return self.constructSpeakerName(firstSpeaker)
        elif 'Presenter' in secondSpeaker[0]:
            return self.constructSpeakerName(secondSpeaker)
        
        return None
    
    
    def getSecondarySpeaker(self):
        """ This method returns the name of the seondary presenter or Presenter 2 """
        firstSpeaker = self.sample[0]
        secondSpeaker = self.sample[2]

        if 'Expert' in firstSpeaker[0]:
            return self.constructSpeakerName(firstSpeaker)
        else:
            if len(self.sample) > 1:
                return self.constructSpeakerName(secondSpeaker)
        
        return None
    
    
    def constructSpeakerName(self, speaker):
        """ This method constructs the speakers full name from the raw construct being
        the array holding the name. An example of such a construct is
        ['Presenter', '1:', 'Simon', 'Marnie,', 'M'] """
        # if the speaker turn is not in the format specified above then return None
        if len(speaker) > 1:
            if len(speaker) == 4 and speaker[3].replace(',', '').strip() in ('M', 'F'):
                return speaker[2].replace(',', '')
            elif len(speaker) >= 4:
                lastName = speaker[3].replace(',', '')
                firstName = speaker[2]
                return firstName + ' ' + lastName
        
        return None