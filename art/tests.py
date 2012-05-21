import pyparsing
import unittest

from ausnc_ingest.annotations.annotation_parsers import *
from ausnc_ingest.annotations import *
from ausnc_ingest.art.ingest import ARTIngest
from ausnc_ingest.art.parser import *
from ausnc_ingest.art.sample import *
from ausnc_ingest.art.iterator import *

def unittests():
    res = unittest.TestSuite()
    # res.addTest(unittest.makeSuite(ParsingTests))
    # res.addTest(unittest.makeSuite(MetaTests))
    res.addTest(unittest.makeSuite(IngestTests))
    return res

class ParsingTests(unittest.TestCase):
    
    def test_simple_pause(self):
        
        rawText = "<,>"
        
        parser = pyparsing.OneOrMore( artpauseParser() )
        res = parser.parseString(rawText)
        
        self.assertEqual("[@( ,[pause:  0 -> 0])]", str(res))
        
    
    def test_simple_pause(self):

        rawText = "One of the jewels in the open garden scheme crown is opening today and this is just a garden to envy how would you like <,> to have <,> a beautiful sandstone cottage nestled underneath a waterfall with a little pond and then a creek that runs through with thousands of water dragons so tame they come up and just <,> kiss you. Would you like to live there"

        ingest = ARTIngest()
        res = ingest.extractAnnotations(rawText)

        # print res[0]
        self.assertEqual("[pause:  120 -> 120, pause:  130 -> 130, pause:  309 -> 309]", str(res[1]))
            
              
    def test_simple_correction(self):
        
        rawText = "{propagation} Mr Propergation"
        
        parser = pyparsing.OneOrMore( correctionParser() )
        res = parser.parseString(rawText)
        
        self.assertEqual("[@(,[correction: propagation 0 -> 0])]", str(res))
        
    
    def test_simple_interjection(self):
        
        rawText = "<E1 sounds reasonable> for his ability to open cosposting toilets so he can tell you"
        ingest = ARTIngest()
        parser = pyparsing.OneOrMore( interjectionParser() )
        res = parser.parseString(rawText)

        self.assertEqual("[@(,[interjection: E1 sounds reasonable 0 -> 0])]", str(res))
        
    
    def test_complex_interjection(self):

        rawText = "He's also known <E1 sounds reasonable> for his ability to open cosposting"
        ingest = ARTIngest()
        res = ingest.extractAnnotations(rawText)

        self.assertEqual("He's also known  for his ability to open cosposting", str(res[0]))
        self.assertEqual("[interjection: E1 sounds reasonable 16 -> 16]", str(res[1]))
           
            
    def test_extract_annotations(self):
        
        rawText = "Thanks for that John Hall now John Hall will be listening for the next hour 'cos Angus Stewart is here to take your calls eight-triple-three-one-thousand one-eight-hundred-eight-hundred-seven-oh-two something in the garden that's causing you problems give us a call right now and Angus can I mean y'know he is known in the trade as Mr popergation {propagation} Mr propagation. He's also known for his passion for natives and his love of o orchids am I right so far."
        ingest = ARTIngest()
        res = ingest.extractAnnotations(rawText)

        self.assertEqual("[correction: propagation 347 -> 347]", str(res[1]))


class IngestTests(unittest.TestCase):
    
    ingest = ARTIngest()
    
    def setUp(self):
        self.ingest.setMetaData('../input/ART/ART-corpus-catalogue.xls')
    
    @unittest.skip("Tmp")    
    def test_simple_speaker_turn_parsing(self):
        parsed_content = parseCompleteDocument("[P1] Well hello there.")
        self.assertEqual(2, len(parsed_content))
        self.assertEqual('P1', parsed_content[0][0])
        
        parsed_content  = parseCompleteDocument("[E1] Just some normal text\n and more text. [P2] and some more text.")
        self.assertEqual(4, len(parsed_content))
        self.assertEqual("E1", parsed_content[0][0])
        

    @unittest.skip("Tmp")        
    def test_parse_sample1(self):
        file = open("../systemtests/art/sample1.txt", "r")
        content = file.read()
        parsed_content = parseCompleteDocument(content)
                
        self.assertEqual(10, len(parsed_content))
        self.assertEqual("E1", parsed_content[6][0])
        
        for sample in ArtIterator(parsed_content):
            self.assertEqual((0, 10), sample)
        

    @unittest.skip("Tmp")    
    def test_parse_sample2(self):
        file = open("../systemtests/art/sample2.txt", "r")
        content = file.read()
        parsed_content = parseCompleteDocument(content)
                
        self.assertEqual("P1", parsed_content[8][0])
        
        index = 0
        for sample in ArtIterator(parsed_content):
            if (index == 0):
                # print parsed_content[204]
                self.assertEqual((0, 203), sample)
            else:
                self.assertEqual((204, 438), sample)
            index += 1

    
    @unittest.skip("Tmp")           
    def test_parse_sample3(self):
        file = open("../systemtests/art/sample3.txt", "r")
        content = file.read()
        parsed_content = parseCompleteDocument(content)
            
        self.assertEqual("Caller", parsed_content[12][0])
        
        index = 0
        for sample in ArtIterator(parsed_content):
            if (index == 0):
                # print parsed_content[262]
                self.assertEqual((0, 261), sample)
            else:
                self.assertEqual((262, 622), sample)
            index += 1
            

    @unittest.skip("Tmp")        
    def test_parse_sample4(self):
        file = open("../systemtests/art/sample4.txt", "r")
        content = file.read()
        parsed_content = parseCompleteDocument(content)
        
        self.assertEqual("E1", parsed_content[12][0])
        
        index = 0
        for sample in ArtIterator(parsed_content):
            if (index == 0):
                # print parsed_content[406]
                self.assertEqual((0, 405), sample)
            else:
                self.assertEqual((406, 1284), sample)
            index += 1
            
                        
    @unittest.skip("Tmp")
    def test_parse_original(self):
        file = open("../input/ART/Austgram-texts.txt", "r")
        content = file.read()
        parsed_content = parseCompleteDocument(content)
        
        for index in range(0, len(parsed_content) -1, 2):
            self.assertTrue(parsed_content[index][0][0] in ('P','C', 'E'))
            
            
        for sample in ArtIterator(parsed_content):
            print sample
            print parsed_content[sample[0]]
            
            
    def test_ingest_samples(self):
        
        self.ingest.ingestCorpus("../input/ART", "../output/ART")
        # self.ingest.ingestCorpus("../systemtests/art", "../output/ART")
    

class MetaTests(unittest.TestCase):

    ingest = ARTIngest()

    def setUp(self):
        self.ingest.setMetaData('../input/ART/ART-corpus-catalogue.xls')


    def test_grouped_callers(self):
        come6 = self.ingest.file_meta['COME6']
        self.assertEqual('Jasmine', come6['table_person_13']['name'])
        self.assertEqual('F', come6['table_person_13']['gender'])

        self.assertEqual('Jimmy', come6['table_person_14']['name'])
        self.assertEqual('M', come6['table_person_14']['gender'])


    def test_find_meta_from_sample1(self):
        file = open("../systemtests/art/sample1.txt", "r")
        content = file.read()
        parsedContent = parseCompleteDocument(content)
        
        for item in ArtIterator(parsedContent):
            sample = Sample(parsedContent[item[0]: item[1]])
            meta = self.ingest.findMetaData(sample)
            self.assertEqual('ABCE1', meta['sampleid'])
        

    def test_find_meta_from_sample2(self):
        file = open("../systemtests/art/sample2.txt", "rb")
        content = file.read()
        parsedContent = parseCompleteDocument(content)
        
        index = 0
        for item in ArtIterator(parsedContent):
            sample = Sample(parsedContent[item[0]: item[1]])
            meta = self.ingest.findMetaData(sample)
            
            if index == 0:
                self.assertEqual('COMNE6', meta['sampleid'])
                index += 1
            else:
                self.assertEqual('COMNE7', meta['sampleid'])
    
                
    def test_find_meta_from_sample3(self):
        file = open("../systemtests/art/sample3.txt", "r")
        content = file.read()
        parsedContent = parseCompleteDocument(content)
        
        index = 0
        for item in ArtIterator(parsedContent):
            sample = Sample(parsedContent[item[0]: item[1]])
            meta = self.ingest.findMetaData(sample)
            
            if index == 0:
                self.assertEqual('ABCE4', meta['sampleid'])
                index += 1
            else:
                self.assertEqual('ABCNE1', meta['sampleid'])   
                
    
    def test_find_meta_from_sample4(self):
        file = open("../systemtests/art/sample4.txt", "r")
        content = file.read()
        parsedContent = parseCompleteDocument(content)
        
        index = 0
        for item in ArtIterator(parsedContent):
            sample = Sample(parsedContent[item[0]: item[1]])
            meta = self.ingest.findMetaData(sample)
            
            if index == 0:
                self.assertEqual('NAT2', meta['sampleid'])
                index += 1
            else:
                self.assertEqual('NAT7', meta['sampleid'])   
    
    
    def test_extract_of_raw_data(self):
        file = open("../systemtests/art/sample1.txt", "r")
        content = file.read()
        parsedContent = parseCompleteDocument(content)
        
        index = 0
        for item in ArtIterator(parsedContent):
            sample = Sample(parsedContent[item[0]: item[1]])
            raw = sample.extractRawText()
            
    
    @unittest.skip("Commented out because test takes very long to execute")
    def test_extract_of_raw_data_for_original(self):
        file = open("../input/ART/Austgram-texts.txt", "r")
        content = file.read()
        parsedContent = parseCompleteDocument(content)
        
        index = 0
        for item in ArtIterator(parsedContent):
            sample = Sample(parsedContent[item[0]: item[1]])
            raw = sample.extractRawText()


    def test_no_of_samples(self):
        self.assertEqual(29, len(self.ingest.file_meta))
    
    
    def test_extract_of_unknown_location(self):
        self.assertTrue(self.ingest.file_meta.has_key('NAT1'))
        self.assertEqual('', self.ingest.file_meta['NAT1']['location'])


    def test_extract_of_known_location(self):
        self.assertTrue(self.ingest.file_meta.has_key('ABCE1'))
        self.assertEqual('Sydney', self.ingest.file_meta['ABCE1']['location'])


    def test_extract_of_station(self):
        self.assertTrue(self.ingest.file_meta.has_key('COME3'))
        self.assertEqual('2GB', self.ingest.file_meta['COME3']['station'])
    

    def test_extract_of_program(self):
        self.assertTrue(self.ingest.file_meta.has_key('COME1'))
        self.assertEqual('The Garden Clinic', self.ingest.file_meta['COME1']['program'])
        

    def test_extract_of_recorded_date(self):
        self.assertTrue(self.ingest.file_meta.has_key('ABCE3'))
        self.assertEqual('2004/03/02', self.ingest.file_meta['ABCE3']['recorded'])
        

    def test_extract_of_proof_heard_and_final_check(self):
        self.assertTrue(self.ingest.file_meta.has_key('COME5'))
        self.assertEqual('y', self.ingest.file_meta['COME5']['proof_heard'])
        self.assertEqual('y', self.ingest.file_meta['COME5']['final_check'])
        

    def test_extract_of_known_subject(self):
        self.assertTrue(self.ingest.file_meta.has_key('COME6'))
        self.assertEqual(u'"installing stuff" "love song dedications" film reviews', self.ingest.file_meta['COME6']['subject'])
        

    def test_extract_of_unknown_subject(self):
        self.assertTrue(self.ingest.file_meta.has_key('COME7'))
        self.assertEqual('', self.ingest.file_meta['COME7']['subject'])
 

    def test_extract_of_known_ti(self):
        self.assertTrue(self.ingest.file_meta.has_key('NAT3'))
        self.assertEqual("Don't transcribe 0-7.05 (introduction, book reading and interview with child); 33.50-35.12 (book reading)", self.ingest.file_meta['NAT3']['transcriber_instructions'])
    

    def test_extract_of_known_transcribed(self):
        self.assertTrue(self.ingest.file_meta.has_key('NAT3'))
        self.assertEqual("2005/01/09", self.ingest.file_meta['NAT3']['transcribed'])
        
        
    def test_extract_nat4_caller_53_info(self):
        self.assertTrue(self.ingest.file_meta.has_key('NAT4'))
        
        # Check for person 1 who should be a presenter with the name Tony Delroy
        self.assertTrue(self.ingest.file_meta['NAT4'].has_key('table_person_1'))
        self.assertEqual('Tony Delroy', self.ingest.file_meta['NAT4']['table_person_1']['name'])
        self.assertEqual('presenter', self.ingest.file_meta['NAT4']['table_person_1']['role'])

        # Check for person 2 who should be a expert with the name Dr Barry Wren
        self.assertTrue(self.ingest.file_meta['NAT4'].has_key('table_person_2'))
        self.assertEqual('Barry Wren', self.ingest.file_meta['NAT4']['table_person_2']['name'])
        self.assertEqual('Gynecological Researcher/author', self.ingest.file_meta['NAT4']['table_person_2']['role'])
        
        # Check for person 3 who should be a caller with the name Carol
        self.assertTrue(self.ingest.file_meta['NAT4'].has_key('table_person_3'))
        self.assertEqual('Carol', self.ingest.file_meta['NAT4']['table_person_3']['name'])
        self.assertEqual('caller', self.ingest.file_meta['NAT4']['table_person_3']['role'])
        
        # Check for person 54 who should be a caller with the name Carol
        self.assertTrue(self.ingest.file_meta['NAT4'].has_key('table_person_54'))
        self.assertEqual('Ian', self.ingest.file_meta['NAT4']['table_person_54']['name'])
        self.assertEqual('caller', self.ingest.file_meta['NAT4']['table_person_54']['role'])
        self.assertEqual('M', self.ingest.file_meta['NAT4']['table_person_54']['gender'])
    
    
    def test_extract_normal_name(self):
        file = open("../systemtests/art/sample1.txt", "r")
        content = file.read()
        parsedContent = parseCompleteDocument(content)
        
        index = 0
        for item in ArtIterator(parsedContent):
            sample = Sample(parsedContent[item[0]: item[1]])
            self.assertEqual('Simon Marnie', sample.constructSpeakerName(parsedContent[item[0]: item[1]][0]))
            
    
    def test_extract_short_name(self):
        file = open("../systemtests/art/sample5.txt", "r")
        content = file.read()
        parsedContent = parseCompleteDocument(content)

        index = 0
        for item in ArtIterator(parsedContent):
            sample = Sample(parsedContent[item[0]: item[1]])
            self.assertEqual('Les', sample.constructSpeakerName(parsedContent[item[0]: item[1]][0]))
            return