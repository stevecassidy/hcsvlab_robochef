import httplib2, unittest, logging, os

from ausnc_ingest.upload.helper import *
from ausnc_ingest.upload.session import *
from ausnc_ingest.upload.getrequest import *
from ausnc_ingest.upload.adminrdfuploadform import *
from ausnc_ingest.upload.rdfuploadform import *
from ausnc_ingest.upload.corpusitemuploadform import *
from ausnc_ingest.upload.formdecorator import *
from ausnc_ingest.upload.resolver import *
from ausnc_ingest.upload.uploadexception import *
from ausnc_ingest.utils.filehandler import *

def unittests():
  return unittest.makeSuite(UnitTest)  


class UnitTest(unittest.TestCase):

  helper = Helper()
  
  def setUp(self):
    '''
    The initialisation MUST BE performed in this setup method otherwise it breaks
    the uploader because ConfigManager can only initialised once.
    '''
    current_dir = os.path.abspath(os.path.dirname(__name__))
    if os.path.basename(current_dir) == 'bin':
      homedir = '../src/ausnc_ingest'
    else:
      homedir = os.path.join(current_dir, 'ausnc_ingest')
  
    DEFAULT_CONFIG_FILE = os.path.join(homedir, "griffithconfig.ini")
    configmanager.configinit(DEFAULT_CONFIG_FILE)
  
    self.uploadUrl = self.helper.build_url(configmanager.get_config("UPLOADURL"), 'ace') 
    self.corpusuploadUrl = self.helper.build_url(configmanager.get_config('CORPUSLOADURL'), 'ace')
    self.loginUrl = configmanager.get_config("LOGINURL")


  def test_get_ace_url(self):
    
    downloadUrl = self.helper.get_download_url('a01a', 'ACE')
    self.assertEqual('http://ausncdev.rcs.griffith.edu.au:8080/Plone/corpora/acetest/a01a', downloadUrl)
    
    
  def test_get_md_url(self):
    
    downloadUrl = self.helper.get_download_url('a01a', 'MD')
    self.assertEqual('http://ausncdev.rcs.griffith.edu.au:8080/Plone/corpora/mdtest/a01a', downloadUrl)

          
  @unittest.skip("Uncomment once proper dev server setup") 
  def testLoginFormInitialisation(self):
    
    loginForm = LoginForm()

     
  @unittest.skip("Uncomment once proper dev server setup")   
  def testSessionCreationWithValidUsernameAndPassword(self):
    
    session = Session()
    self.assertTrue(session.authenticate(self.loginUrl, 'admin','admin'))
    self.assertTrue(session.inSession())


  @unittest.skip("Uncomment once proper dev server setup")     
  def testSessionCreationWithInvalidUsernameAndPassword(self):
    
    session = Session()
    self.assertFalse(session.authenticate(self.loginUrl, 'admin',''))
    self.assertFalse(session.inSession())

      
  @unittest.skip("Uncomment once proper dev server setup")          
  def testGetRequestWithPloneOnAValidPage(self):
    
    session = Session()
    session.authenticate('admin','admin')
    
    getRequest = GetRequest('http://localhost:8499/ausnc/ace/',session)
    return_codes = getRequest.submit()
    
    self.assertEqual(return_codes['code'],200)


  @unittest.skip("Uncomment once proper dev server setup") 
  def testGetRequestWithPloneOnAInvalidPage(self):
    
    session = Session()
    session.authenticate('admin','admin')
    
    getRequest = GetRequest('http://localhost:8499/ausnc/ucb/',session)
    return_codes = getRequest.submit()
    
    self.assertEqual(return_codes['code'], 404)


  @unittest.skip("Uncomment once proper dev server setup") 
  def testUploadOfRDFFile(self):
    
    session = Session()
    session.authenticate(self.loginUrl, 'admin','$ailing')
    
    if session.inSession():
      uploadForm = FormDecorator(AdminRDFUploadForm())
      
      adminuploadUrl = configmanager.get_config("ADMINUPLOADURL")
      response = uploadForm.submit(adminuploadUrl, session, 'http://ns.ausnc.org.au/corpus/ACE/', 'A01a-ann.rdf', '../output/ace/A01a-ann.rdf')

      print
      print 'SERVER RESPONSE:'
      print response
      
    else:
      
      print 'Failed Authentication'

  
  @unittest.skip("Uncomment once proper dev server setup") 
  def testUploadOfFileFailure(self):

    logging.basicConfig(filename='testing.log', level=logging.INFO, format='%(asctime)s %(message)s')
    session = Session()
    session.authenticate(self.loginUrl, 'admin','admin')

    uploadForm = FormDecorator(RDFUploadForm())
    uploadForm.submit(self.uploadUrl, session, 'W1A-001-ann.rdf', 'nosuchfile.rdf')
    
  
  @unittest.skip("Uncomment once proper dev server setup") 
  def testUploadOfNonN3FileFailure(self):
    
    logging.basicConfig(filename='testing.log', level=logging.INFO, format='%(asctime)s %(message)s')
    session = Session()
    session.authenticate(self.loginUrl, 'admin','admin')

    uploadForm = RDFUploadForm("ace")
    self.assertRaises(UploadException, uploadForm.submit, self.uploadUrl, session, 'A01a.txt', '../output/ace/A01a.txt')
    
      
  @unittest.skip("Uncomment once proper dev server setup") 
  def testUploadOfCorpusItem(self):

    session = Session()
    session.authenticate(self.loginUrl, 'admin','admin')

    uploadForm = FormDecorator(CorpusItemUploadForm())
    uploadForm.submit(self.corpusuploadUrl, \
                      session, \
                      'A01a.txt', \
                      '../output/ace/A01a.txt')
 
  @unittest.skip("Uncomment once proper dev server setup") 
  def testUploadOfBinaryCorpusItem(self):

    session = Session()
    session.authenticate(self.loginUrl, 'admin','admin')

    uploadForm = FormDecorator(CorpusItemUploadForm())
    
    print self.corpusuploadUrl
    uploadForm.submit(self.corpusuploadUrl, \
                      session, \
                      'S0099s3.wav', \
                      '../output/MD/S0099s3.wav')
 
      
  @unittest.skip("The Plone development server does not support basic authentication") 
  def testPloneAuthWithBasicAuthentication(self):

    h = httplib2.Http(".cache")
    h.add_credentials('admin', 'admin')

    headers = {}
    headers['Content-type'] = 'application/x-www-form-urlencoded'
    headers['User-Agent'] = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'

    response, content = h.request("http://localhost:8499/ausnc/ace/", "GET", headers = headers )

    self.assertTrue(response.has_key('set-cookie'))
   
  
  def testDynamicUrlConstructionUsingTemplate(self):
    template = configmanager.get_config("UPLOADURL") 
    helper = Helper()
    self.assertEqual(helper.build_url(template, 'acetest'), template.replace('#COLNAME#', 'acetest'))
   

  @unittest.skip("Uncomment once proper dev server setup")
  def testUploadTracking(self):
    
    helper = Helper()
    uploaded_files = helper.get_uploaded_files('ace')
    self.assertEqual(uploaded_files, {'A01a-ann.rdf': '', 'A01a-metadata.rdf': '', 'A01a.txt': ''})
    


  def test_get_subject_urifor_ace(self):
    resolver = Resolver()
    sub_uri = resolver.get_subject_uri('../systemtests/ace/A01a-metadata.rdf', 'A01a-plain.txt')
    
    self.assertEqual('http://ns.ausnc.org.au/corpora/ace/source/A01a#Text', sub_uri)


  def test_get_subject_for_missing_document(self):
    resolver = Resolver()
    sub_uri = resolver.get_subject_uri('../systemtests/ace/A01a-metadataXYZ.rdf', 'A01a.txt')

    self.assertEqual(sub_uri, '')


  def test_get_subject_uri_GCSAusE07mp3(self):
    resolver = Resolver()
    sub_uri = resolver.get_subject_uri('../systemtests/griffith/GCSAusE07-metadata.rdf', 'GCSAusE07.mp3')

    self.assertEqual('http://ns.ausnc.org.au/corpora/gcsause/source/GCSAusE07#Audio', sub_uri)
      

  def test_get_subject_uri_GCSAusE07txt(self):
    resolver = Resolver()
    sub_uri = resolver.get_subject_uri('../systemtests/griffith/GCSAusE07-metadata.rdf', 'GCSAusE07-plain.txt')

    self.assertEqual('http://ns.ausnc.org.au/corpora/gcsause/source/GCSAusE07#Text', sub_uri)
        

  def test_get_item_uri_GCSAusE07txt(self):
    resolver = Resolver()
    item_uri = resolver.get_item_uri('../systemtests/griffith/GCSAusE07-metadata.rdf')

    self.assertEqual('http://ns.ausnc.org.au/corpora/gcsause/items/GCSAusE07', item_uri)
    

  def test_get_item_uri_ACE01(self):
    resolver = Resolver()
    item_uri = resolver.get_item_uri('../systemtests/ace/A01a-metadata.rdf')

    self.assertEqual('http://ns.ausnc.org.au/corpora/ace/items/A01a', item_uri)
      
          
  def test_get_griffith_uploadfiles(self):
    resolver = Resolver()
    upload_files = resolver.get_upload_units('../systemtests/griffith/GCSAusE07-metadata.rdf')

    self.assertEqual(['GCSAusE07-plain.txt', 'GCSAusE07-raw.txt', 'GCSAusE07.doc', 'GCSAusE07.mp3'], sorted(upload_files))
    

  def test_get_ace_uploadfiles(self):
    resolver = Resolver()
    upload_files = resolver.get_upload_units('../systemtests/ace/A01a-metadata.rdf')

    self.assertEqual(['A01a-plain.txt', 'A01a-raw.txt', 'ace_a.txt'], sorted(upload_files))
    
  
  def test_get_ace_usingannotationfile(self):
    resolver = Resolver()
    upload_files = resolver.get_upload_units('../systemtests/ace/A01a-ann.rdf')

    self.assertEqual([], sorted(upload_files))
    
    
  def test_get_a01a_title(self):
    resolver = Resolver()
    self.assertEqual("Gala opening for extension to Qld Govt's DP centre", resolver.get_title('../systemtests/ace/A01a-metadata.rdf'))
    

  def test_get_BC_DC_09_title(self):
    resolver = Resolver()
    self.assertEqual("Braided Channels of History Recording & Transcript - 08", resolver.get_title('../systemtests/braided/08_BC_DV_EATTS-metadata.rdf'))
    

  def test_get_1_001_id(self):
     resolver = Resolver()
     self.assertEqual("1-001", resolver.get_identifier('../systemtests/cooee/1-001-metadata.rdf'))
     
     
  def test_get_document_type(self):
    resolver = Resolver()
    self.assertEqual('Raw', resolver.get_document_type('../systemtests/cooee/1-001-metadata.rdf', 'http://ns.ausnc.org.au/corpora/cooee/source/1-001#Raw'))
    
    
  def testProdBraidedUploadLog(self):
    helper = Helper()
    uploaded_files = helper.get_uploaded_files('Braided', base_path='../systemtests/braided')
    
    self.assertTrue(uploaded_files.has_key('INTERVIEW WITH EDITH MCFARLANE 01 of 03.pdf'))
    self.assertTrue(uploaded_files.has_key('INTERVIEW WITH NARELLE & BRONWEN MORRISH 02 of 02.pdf'))
    self.assertTrue(uploaded_files.has_key('INTERVIEW WITH DAVID DUNCAN-KEMP 02a of 02.pdf'))
