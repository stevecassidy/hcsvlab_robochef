class ArtIterator:
    
    def __init__(self, parsed_content):
        """ Class is initialised with the parsed list containing the full data set """
        self.start = self.end = 0
        self.source = parsed_content
        self.knownPatterns = (('Presenter 1:', 'Expert 1:'), ('Presenter 1:', 'Presenter 2:'), ('Expert 1:', 'Presenter 1:'), 
                              ('Presenter 1:', 'Caller 1:'), ('Presenter 1:', 'P1'))


    def __iter__(self):
        """ Method conforming to the iterator interface in Python """
        return self

    
    def next(self):
        """ 
        This method gets the next sample from the collection keeping tracking of where it is 
        
        In the source data the start of sample cannot be simply obtained. What we have managed to
        establish is that a sample normally starts with a fully descriptive token for presenter
        then followed by an expert.
        
        i.e. [Presenter 1: ... ] ...
             [Expert 1: ...] ...
             
        However there are other noticeable patterns. Examples of these are listed below
        
        Presenter 1 and 2
        [Presenter 1: ... ]
        [Presenter 2: ... ]
        
        Expert 1 and Presenter 1
        [Expert 1: ... ] ...
        [Presenter 1: ... ] ...
        
        Presenter 1 and Caller 1
        [Presenter 1: ... ] ...
        [Caller 1 : ... ] ...
        
        Presenter 1 followed by a normal speaker turn (i.e. [P1], [C1] etc)
        [Presenter 1: ... ]
        [P1]
        """
        if self.end == len(self.source):
            raise StopIteration
        else:
            initialStart = self.start
            self.start = self._moveMarkerToNextSample()
            self.end = self.start - 1
            return (initialStart, self.end)
        
        
    def _getCurrentSampleStartMarker(self, location):
        """ This method returns a tuple indicating what the sample start looks like. Examples of the return values
        are;
        (Presenter 1:, Expert 1:)
        (Presenter 1:, Presenter 1:)
        (Expert 1:, Presenter 1:)
        (Presenter 1:, Caller 1:)
        (Presenter 1:, P1)
        """
        # Speaker turns labels are stored in even index positions, the speaker turn content are
        # stored in odd positions. A speaker turn label may only consist of one item like [P1]
        # or might be a full label like [Presenter 1:]. The parser splits the Presenter and 1:
        # into two index positions
        if len(self.source[location]) > 1:
            firstSpeakerType = self.source[location][0] + ' ' + self.source[location][1]
        else:
            firstSpeakerType = self.source[location][0]
            
        if len(self.source[location + 2]) > 1:
            secondSpeakerType = self.source[location + 2][0] + ' ' + self.source[location + 2][1]
        else:
            secondSpeakerType = self.source[location + 2][0]
        
        return (firstSpeakerType, secondSpeakerType)
    
    
    def _moveMarkerToNextSample(self):
        """ This method moves the marker to the next sample """
        for index in range(self.start + 2, len(self.source), 2):
            # If there is no next item, meaning we have run out of samples
            # then just return that particular index to the iterator
            # which will gracefully terminate 
            if index + 3 > len(self.source):
                return index + 3
            else:
                # This retrieves a two speaker turn identifiers
                # certain patterns denote the start of a new sample
                res = self._getCurrentSampleStartMarker(index)
                if res in self.knownPatterns:
                    return index
        