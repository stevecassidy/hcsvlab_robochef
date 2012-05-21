import unittest

from ausnc_ingest.auslit.ingest import *
from ausnc_ingest.annotations import *

def unittests():
  return unittest.makeSuite(UnitTest)  


class UnitTest(unittest.TestCase):

  def test_processes_properfiles(self):
    auslit = AuslitIngest()
    files = auslit._AuslitIngest__get_files('../input/auslit')
    self.assertEqual(68, len(files))
    
  
  def test_adaessa_get_meta_tree(self):
    auslit = AuslitIngest()
    (meta_text, meta_tree) = auslit._AuslitIngest__get_meta_tree('../systemtests/auslit', 'adaessa.xml')
    self.assertIsNotNone(meta_tree)
   
   
  def test_barmoth_get_meta_tree(self):
    auslit = AuslitIngest()
    (meta_text, meta_tree) = auslit._AuslitIngest__get_meta_tree('../systemtests/auslit', 'barmoth.xml')
    self.assertIsNone(meta_tree)
    
    
  def test_adaessa_includable(self):
    auslit = AuslitIngest()
    (meta_text, meta_tree) = auslit._AuslitIngest__get_meta_tree('../systemtests/auslit', 'adaessa.xml')
    self.assertTrue(auslit._AuslitIngest__is_includable(meta_tree))
    
  
  def test_adamans_includable(self):
    auslit = AuslitIngest()
    (meta_text, meta_tree) = auslit._AuslitIngest__get_meta_tree('../systemtests/auslit', 'adamans.xml')
    self.assertTrue(auslit._AuslitIngest__is_includable(meta_tree))


  def test_adasong_includable(self):
    auslit = AuslitIngest()
    (meta_text, meta_tree) = auslit._AuslitIngest__get_meta_tree('../systemtests/auslit', 'adasong.xml')
    self.assertFalse(auslit._AuslitIngest__is_includable(meta_tree))
    

  def test_banconf_includable(self):
    auslit = AuslitIngest()
    (meta_text, meta_tree) = auslit._AuslitIngest__get_meta_tree('../systemtests/auslit', 'banconf.xml')
    self.assertFalse(auslit._AuslitIngest__is_includable(meta_tree))
