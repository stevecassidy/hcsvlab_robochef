import unittest

from hcsvlab_robochef.ace.ingest import *
from hcsvlab_robochef.annotations import *
from hcsvlab_robochef.ace.html_parser import *


def unittests():
    return unittest.makeSuite(UnitTest)


class UnitTest(unittest.TestCase):
    ingest = ACEIngest()

    def testAnnotationExtraction(self):
        self.assertEqual(self.ingest._ACEIngest__extractAnnotations(""), ("", []))
        self.assertEqual(self.ingest._ACEIngest__extractAnnotations("aabb"), ("aabb", []))
        self.assertEqual(self.ingest._ACEIngest__extractAnnotations("as*aa I said"),
                         ("aa I said", [Annotation("correction", "as", 2, 2)]))
        self.assertEqual(self.ingest._ACEIngest__extractAnnotations("b as*aa I said"),
                         ("b aa I said", [Annotation("correction", "as", 4, 4)]))
        self.assertEqual(self.ingest._ACEIngest__extractAnnotations("hello as*aa I said"),
                         ("hello aa I said", [Annotation("correction", "as", 8, 8)]))
        self.assertEqual(self.ingest._ACEIngest__extractAnnotations(
            "hello this*bb is the thing*thng, we all need*ned to do right*rgt"),
                         ("hello bb is the thng, we all ned to do rgt",
                          [Annotation("correction", "this", 8, 8), Annotation("correction", "thing", 20, 20),
                           Annotation("correction", "need", 32, 32), Annotation("correction", "right", 42, 42)]))


    def testTransposeCorrections(self):
        self.assertEqual(self.ingest._ACEIngest__transposeCorrections(
            [AnnotatedText("one", [Annotation("a", "b", 0, 0)]), AnnotatedText("two", [Annotation("c", "d", 1, 1)])]),
                         [AnnotatedText("one", [Annotation("a", "b", 0, 0)]),
                          AnnotatedText("two", [Annotation("c", "d", 1, 1)])],
        )
        self.assertEqual(
            self.ingest._ACEIngest__transposeCorrections([AnnotatedText("one", [Annotation("a", "b", 0, 0)])]),
            [AnnotatedText("one", [Annotation("a", "b", 0, 0)])],
        )


    def testHtmlParseOnSampleA01(self):

        file_handle = open('../input/ace/Manual/KATA.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        print ''
        for master_key in sorted(parser.meta_data.iterkeys()):
            if master_key.startswith('A01a'):
                self.assertEqual(parser.meta_data[master_key]['Source'], u'The Australian 28 October 1986 (2007 words)')
                self.assertEqual(parser.meta_data[master_key]['Publisher'],
                                 u"Samples 'Used by permission of News Limited")
                self.assertEqual(parser.meta_data[master_key]['Word Count'], u'443 words')
                self.assertEqual(parser.meta_data[master_key]['Publication Date'], u'28 October 1986')
                self.assertEqual(parser.meta_data[master_key]['Title'],
                                 u"Gala opening for extension to Qld Govt's DP centre")


    def testHtmlParseOnSampleA22f(self):

        file_handle = open('../input/ace/Manual/KATA.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        for master_key in sorted(parser.meta_data.iterkeys()):
            if master_key.startswith('A22f'):
                self.assertEqual(parser.meta_data[master_key]['Source'],
                                 u'The Courier Mail 4 December 1986 (2013 words)')
                self.assertEqual(parser.meta_data[master_key]['Publisher'],
                                 u"Samples 'Used by Permission of Queensland Newspapers Pty Ltd")
                self.assertEqual(parser.meta_data[master_key]['Word Count'], u'185 words')
                self.assertEqual(parser.meta_data[master_key]['Publication Date'], u'4 December 1986')
                self.assertEqual(parser.meta_data[master_key]['Title'], u'Eighth Rhine leak in a month')


    def testHtmlParseOnSampleA23b(self):

        file_handle = open('../input/ace/Manual/KATA.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        for master_key in sorted(parser.meta_data.iterkeys()):
            if master_key.startswith('A23b'):
                self.assertEqual(parser.meta_data[master_key]['Source'],
                                 u'The Courier Mail 15 October 1986 (2001 words)')
                self.assertEqual(parser.meta_data[master_key]['Publisher'],
                                 u"Samples 'Used by Permission of Queensland Newspapers Pty Ltd")
                self.assertEqual(parser.meta_data[master_key]['Word Count'], u'700 words')
                self.assertEqual(parser.meta_data[master_key]['Publication Date'], u'15 October 1986')
                self.assertEqual(parser.meta_data[master_key]['Title'],
                                 u'Myth and fable alive and well on the Australian wine scene')
                self.assertEqual(parser.meta_data[master_key]['Author'], u'Bob Gray (#)')


    def testHtmlParseOnSampleA38(self):

        file_handle = open('../input/ace/Manual/KATA.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        for master_key in sorted(parser.meta_data.iterkeys()):
            if master_key.startswith('A38c'):
                self.assertEqual(parser.meta_data[master_key]['Source'], u'Sunday Press 30 November 1986 (2007 words)')
                self.assertEqual(parser.meta_data[master_key]['Publisher'], u'Publisher - David Syme & Co Ltd')
                self.assertEqual(parser.meta_data[master_key]['Word Count'], u'621 words')
                self.assertEqual(parser.meta_data[master_key]['Publication Date'], u'30 November 1986')
                self.assertEqual(parser.meta_data[master_key]['Title'], u'One week to T day')
                self.assertEqual(parser.meta_data[master_key]['Author'],
                                 u'Kevin Norbury, Megan Jones and Ross Brundrett')


    def testHtmlParseOnSampleA44(self):

        file_handle = open('../input/ace/Manual/KATA.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        for master_key in sorted(parser.meta_data.iterkeys()):
            if master_key.startswith('A44b'):
                self.assertEqual(parser.meta_data[master_key]['Source'], u'Weekly Times 23 July 1986 (2002 words)')
                self.assertEqual(parser.meta_data[master_key]['Publisher'], u'Publisher - Herald and Weekly Times Ltd')
                self.assertEqual(parser.meta_data[master_key]['Word Count'], u'1071 words')
                self.assertEqual(parser.meta_data[master_key]['Publication Date'], u'23 July 1986')
                self.assertEqual(parser.meta_data[master_key]['Title'],
                                 u'An eight year battle - then AB licence is granted')


    def testHtmlParseOnSampleB01a(self):

        file_handle = open('../input/ace/Manual/KATB.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        for master_key in sorted(parser.meta_data.iterkeys()):
            if master_key.startswith('B01a'):
                self.assertEqual(parser.meta_data[master_key]['Source'], u'The Australian 28 October 1986 (2015 words)')
                self.assertEqual(parser.meta_data[master_key]['Publisher'],
                                 u"Samples used by Permission of News Limited")
                self.assertEqual(parser.meta_data[master_key]['Word Count'], u'1008 words')
                self.assertEqual(parser.meta_data[master_key]['Title'],
                                 u"Letters: L Gild, Yokine WA; U Bell, Mundaring WA; M Fischer, Perth WA; CW Allen, Cremorne NSW; Di Yerbury, North Sydney NSW; M Hill, Lakemba NSW; R Aschenbrenner, Ferntree Gully Vic; N Manette, Lane Cove NSW; JK McWilliam, Bardon Qld")
                self.assertEqual(parser.meta_data[master_key]['Publication Date'], u'28 October 1986')


    def testHtmlParseOnSampleB01b(self):

        file_handle = open('../input/ace/Manual/KATB.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        for master_key in sorted(parser.meta_data.iterkeys()):
            if master_key.startswith('B01b'):
                self.assertEqual(parser.meta_data[master_key]['Source'],
                                 u'The Weekend Australian 1-2 November 1986 (2007 words)')
                self.assertEqual(parser.meta_data[master_key]['Publisher'],
                                 u"Samples used by Permission of News Limited")
                self.assertEqual(parser.meta_data[master_key]['Word Count'], u'2007 words')
                self.assertEqual(parser.meta_data[master_key]['Title'],
                                 u"Letters:T Freeman, Croydon Vic; GR Ryan, Mt Pleasant; PR Zeeman, Launceston; P Bonar, Findon SA; IG Hope, Kelso NSW; N Nichols, Buderim Qld; IP Youles, Middleton SA; M DeChadbannes, Beaudesert; RF Harrison, Cambah Act; TV Davies, Pymble NSW")
                self.assertEqual(parser.meta_data[master_key]['Publication Date'], u'2 November 1986')


    def testHtmlParseOnSampleB13a(self):

        file_handle = open('../input/ace/Manual/KATB.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        for master_key in sorted(parser.meta_data.iterkeys()):
            if master_key.startswith('B13a'):
                self.assertEqual(parser.meta_data[master_key]['Source'], u'The Telegraph 1 October 1986 (2024 words)')
                self.assertEqual(parser.meta_data[master_key]['Publisher'], u"Publisher of (a) - News Limited")
                self.assertEqual(parser.meta_data[master_key]['Word Count'], u'212 words')
                self.assertEqual(parser.meta_data[master_key]['Title'], u"Letters: J Smith; E Henry; M Gee")
                self.assertEqual(parser.meta_data[master_key]['Publication Date'], u'1 October 1986')


    def testHtmlParseOnSampleB13b(self):

        file_handle = open('../input/ace/Manual/KATB.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        for master_key in sorted(parser.meta_data.iterkeys()):
            if master_key.startswith('B13b'):
                self.assertEqual(parser.meta_data[master_key]['Source'], u'The Courier Mail 27 June 1986 (1822 words)')
                self.assertEqual(parser.meta_data[master_key]['Publisher'], u"Publisher of (a) - News Limited")
                self.assertEqual(parser.meta_data[master_key]['Word Count'], u'1822 words')
                self.assertEqual(parser.meta_data[master_key]['Title'],
                                 u"Letters: CS Jenkins, Aspley; A Conway, Gold Coast; JW Mooney, Hendra; R Franklin, Kenmore; S Ryan, Minister for Education, Canberra; L Brownsey, Banyo; Dr S Woodford, Mt Isa Base Hospital; ED Halburn, Algester")
                self.assertEqual(parser.meta_data[master_key]['Publication Date'], u'27 June 1986')


    def testHtmlParseOnSampleB03c(self):

        file_handle = open('../input/ace/Manual/KATB.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        for master_key in sorted(parser.meta_data.iterkeys()):
            if master_key.startswith('B03c'):
                self.assertEqual(parser.meta_data[master_key]['Source'],
                                 u'The Daily Mirror 29 September 1986 (2010 words)')
                self.assertEqual(parser.meta_data[master_key]['Publisher'],
                                 u"Samples Used by Permission of News Limited")
                self.assertEqual(parser.meta_data[master_key]['Word Count'], u'352 words')
                self.assertEqual(parser.meta_data[master_key]['Title'], u"US Poll Blow to Australia")
                self.assertEqual(parser.meta_data[master_key]['Publication Date'], u'6 November 1986')


    def testHtmlParseOnSampleB03g(self):

        file_handle = open('../input/ace/Manual/KATB.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        for master_key in sorted(parser.meta_data.iterkeys()):
            if master_key.startswith('B03g'):
                self.assertEqual(parser.meta_data[master_key]['Source'],
                                 u'The Daily Mirror 29 September 1986 (2010 words)')
                self.assertEqual(parser.meta_data[master_key]['Publisher'],
                                 u"Samples Used by Permission of News Limited")
                self.assertEqual(parser.meta_data[master_key]['Word Count'], u'124 words')
                self.assertEqual(parser.meta_data[master_key]['Title'], u"Tax cut rort")
                self.assertEqual(parser.meta_data[master_key]['Publication Date'], u'23 June 1986')


    def testHtmlParseOnKATC(self):

        file_handle = open('../input/ace/Manual/KATC.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        self.assertEqual(len(parser.meta_data), 89)


    def testHtmlParseOnKATD(self):

        file_handle = open('../input/ace/Manual/KATD.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        self.assertEqual(len(parser.meta_data), 37)


    def testHtmlParseOnKATE(self):

        file_handle = open('../input/ace/Manual/KATE.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        self.assertEqual(len(parser.meta_data), 79)


    def testHtmlParseOnKATF(self):

        file_handle = open('../input/ace/Manual/KATF.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        self.assertEqual(len(parser.meta_data), 60)


    def testHtmlParseOnKATG(self):

        file_handle = open('../input/ace/Manual/KATG.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        self.assertEqual(len(parser.meta_data), 88)


    def testHtmlParseOnKATH(self):

        file_handle = open('../input/ace/Manual/KATH.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        self.assertEqual(len(parser.meta_data), 36)


    def testHtmlParseOnKATJ(self):

        file_handle = open('../input/ace/Manual/KATJ.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        self.assertEqual(len(parser.meta_data), 82)


    def testHtmlParseOnSampleK01(self):

        file_handle = open('../input/ace/Manual/KATK.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        for master_key in sorted(parser.meta_data.iterkeys()):
            if master_key.startswith('K01'):
                self.assertEqual(parser.meta_data[master_key]['Source'], u'Colours of the Sky 1986 (2005 words)')
                self.assertEqual(parser.meta_data[master_key]['Publisher'],
                                 u"Sample Used by Permission of Fremantle Arts Centre Press")
                self.assertEqual(parser.meta_data[master_key]['Word Count'], u'2005 words')
                self.assertEqual(parser.meta_data[master_key]['Title'], u"Colours of the Sky 1986")
                self.assertEqual(parser.meta_data[master_key]['Author'], u'Peter Cowan')


    def testHtmlParseOnSampleKL07(self):

        file_handle = open('../input/ace/Manual/KATL.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        for master_key in sorted(parser.meta_data.iterkeys()):
            if master_key.startswith('L07'):
                self.assertEqual(parser.meta_data[master_key]['Source'], u'All Possible Avenues 1986 (2019 words)')
                self.assertEqual(parser.meta_data[master_key]['Publisher'],
                                 u"Sample Used by Permission of Rastor Pty Ltd")
                self.assertEqual(parser.meta_data[master_key]['Word Count'], u'2019 words')
                self.assertEqual(parser.meta_data[master_key]['Title'], u"All Possible Avenues 1986")
                self.assertEqual(parser.meta_data[master_key]['Author'], u'Tom Howard')


    def testHtmlParseOnKATMN(self):

        file_handle = open('../input/ace/Manual/KATMN.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        self.assertEqual(len(parser.meta_data), 16)


    def testHtmlParseOnKATP(self):

        file_handle = open('../input/ace/Manual/KATP.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        self.assertEqual(len(parser.meta_data), 15)

        for master_key in sorted(parser.meta_data.iterkeys()):
            if master_key.startswith('P02'):
                #print parser.meta_data[master_key]
                self.assertEqual(parser.meta_data[master_key]['Source'], u'Julia Paradise 1986 (2017 words)')
                self.assertEqual(parser.meta_data[master_key]['Publisher'], u"Publisher - Penguin Books Australia")
                self.assertEqual(parser.meta_data[master_key]['Author'], u'Rod Jones')


    def testHtmlParseOnKATR(self):

        file_handle = open('../input/ace/Manual/KATR.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        self.assertEqual(len(parser.meta_data), 21)


    def testHtmlParseOnKATS(self):

        file_handle = open('../input/ace/Manual/KATS.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        self.assertEqual(len(parser.meta_data), 23)


    def testHtmlParseOnSampleR01(self):

        file_handle = open('../input/ace/Manual/KATR.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        for master_key in sorted(parser.meta_data.iterkeys()):
            if master_key.startswith('R01'):
                self.assertEqual(parser.meta_data[master_key]['Source'], u'Smear and Innuendo 1986 (2001 words)')
                self.assertEqual(parser.meta_data[master_key]['Publisher'],
                                 u"Sample Used by Permission of Watermark Press Pty Ltd")
                self.assertEqual(parser.meta_data[master_key]['Word Count'], u'2001 words')
                self.assertEqual(parser.meta_data[master_key]['Title'],
                                 u"30:Tax Avoidance and a Big Mac; 31:The Speech Writer; 32:Death At The Cross")
                self.assertEqual(parser.meta_data[master_key]['Author'], u'Robert English')


    def testHtmlParseOnSampleR05(self):

        file_handle = open('../input/ace/Manual/KATR.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        for master_key in sorted(parser.meta_data.iterkeys()):
            if master_key.startswith('R05'):
                self.assertEqual(parser.meta_data[master_key]['Source'],
                                 u'Growing Up Catholic: An infinitely funny guide for the faithful, the fallen and everyone in between 1986     (2007 words)')
                self.assertEqual(parser.meta_data[master_key]['Publisher'], u"Publisher - David Ell Press Pty Ltd")
                self.assertEqual(parser.meta_data[master_key]['Word Count'], u'2007 words')
                self.assertEqual(parser.meta_data[master_key]['Title'], u"Good Morning Sister")
                self.assertEqual(parser.meta_data[master_key]['Author'],
                                 u'Gabrielle Lord, Mary Jane Frances, Carolina Mears, Jeffrey Allen, Joseph Stone, Maureen Anne Teresa Kelly, Richard Glen, Michael Door')
                self.assertEqual(parser.meta_data[master_key]['Publication Date'], u'1986')


    def testHtmlParseOnSampleR14f(self):

        file_handle = open('../input/ace/Manual/KATR.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        for master_key in sorted(parser.meta_data.iterkeys()):
            if master_key.startswith('R14f'):
                self.assertEqual(parser.meta_data[master_key]['Source'], u'Aussie Bush Yarns 1986 (2000 words)')
                self.assertEqual(parser.meta_data[master_key]['Publisher'],
                                 u"Samples Used by Permission of Neil Hulm Publishing")
                self.assertEqual(parser.meta_data[master_key]['Word Count'], u'340 words')
                self.assertEqual(parser.meta_data[master_key]['Title'], u"Yap Yap")
                self.assertEqual(parser.meta_data[master_key]['Author'], u'Neil Hulm')
                self.assertEqual(parser.meta_data[master_key]['Publication Date'], u'1986')


    def testHtmlParseOnKATW(self):

        file_handle = open('../input/ace/Manual/KATW.HTM', 'r')
        input_str = file_handle.read()

        parser = AceHTMLParser()
        parser.feed(unicode(input_str))

        self.assertEqual(len(parser.meta_data), 16)


    def testExtractDateWhereOneExists(self):
        parser = AceHTMLParser()
        self.assertTrue(len(parser.extract_date('28 January 2009')) > 0)


    def testExtractDateWhereOneDoesNotExist(self):
        parser = AceHTMLParser()
        self.assertTrue(len(parser.extract_date('28 2009')) == 0)


    def testExtractDateWhereInWrongFormat(self):
        parser = AceHTMLParser()
        self.assertTrue(len(parser.extract_date('28/12/2009')) == 0)


    @unittest.skip("This test is more of a systems test and should not be invoked unless required.")
    def testProcessAce_a(self):
        ingest = ACEIngest()
        ingest.setMetaData('../input/ace/Manual')
        ingest.ingestCorpus('../input/ace', '../output/ace')
