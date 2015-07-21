from hcsvlab_robochef.braided.ingest import *
from hcsvlab_robochef.braided import ingest
import unittest
import rdflib

SPKR = rdflib.term.URIRef(u'http://ns.ausnc.org.au/schemas/annotation/ice/speaker')

def unittests():
  #res = doctest.DocTestSuite(ingest)
  #res.addTest(unittest.makeSuite(UnitTest))
  res = unittest.makeSuite(UnitTest)
  return res


class UnitTest(unittest.TestCase):

  def setUp(self):
      self.braided = BraidedIngest()

  def testSimpleMetaData(self):
      res = self.braided.parseFile("TITLE \n22 June 2011\nsome note\n\nbodytext")
      self.assertEqual(res["infile_title"], "TITLE")
      self.assertEqual(res["infile_date"], "22 June 2011")
      self.assertEqual(res["infile_notes"], "some note")
      self.assertEqual(res["body"], "bodytext")

  def testSlightlyMoreComplexMetaData(self):
      res = self.braided.parseFile("    TITLE      \n22 July 1987\n many notes \n see, more notes \n another\n\nbodytext")
      self.assertEqual(res["infile_title"], 'TITLE')
      self.assertEqual(res["infile_date"], "22 July 1987")
      self.assertEqual(res["infile_notes"], "many notes see, more notes another")
      self.assertEqual(res["body"], "bodytext")

  def test1ca050MetaData(self):
      meta = """INTERVIEW WITH JUNE JACKSON
                         5 June 2000
                      Updated 04/01/10
                Timecode from Tape 16_BC_DV
                       Topics in Bold

             bodytext
             """
      res = self.braided.parseFile(meta)
      self.assertEqual(res["infile_title"], "INTERVIEW WITH JUNE JACKSON")
      self.assertEqual(res["infile_date"], "5 June 2000")
      self.assertEqual(res["infile_notes"], "Updated 04/01/10 Timecode from Tape 16_BC_DV Topics in Bold")

  def test0bb92MetaData(self):
      meta = """                     INTERVIEW WITH GLADYS CROSS
                                           22 June 2000
                                        Refers to tape 56_BVC_SP
                                              Topics in Bold
                                         TF = Trish GC = Gladys

	     bodytext
             """
      res = self.braided.parseFile(meta)
      self.assertEqual(res["infile_title"], "INTERVIEW WITH GLADYS CROSS")
      self.assertEqual(res["infile_date"], "22 June 2000")
      self.assertEqual(res["infile_notes"], "Refers to tape 56_BVC_SP Topics in Bold")
      self.assertEqual(res['infile_participants'][0], {"TF":"Trish", "GC":"Gladys"})

  def testfd96cc22Annotations(self):
      raw = """                 WITH LIZ DEBNEY
                             Recorded 4 June 2000
                               Updated 16/12/09.
                           TC is from tape 11_BC_DV
                                  Topics in Bold

                            I = Interviewer              R = Respondent

            bodytext
            """
      res = self.braided.parseFile(raw)
      self.assertEqual(res["infile_title"], "WITH LIZ DEBNEY")

  def testSimpleAnnotation(self):
      at = self.braided.parse_annotations("I  This is Tape 16 ")
      self.assertEqual(at[0].text, "This is Tape 16")

  def testMoreComplexAnnotations(self):
      at = self.braided.parse_annotations("I  This is Tape 16\n\nR  And this is something else")
      self.assertEqual(at[0].text, "This is Tape 16\n\nAnd this is something else")
      self.assertEqual(at[0].anns[0].tipe, SPKR)
      self.assertEqual(at[0].anns[0]["val"], "I")
      self.assertEqual(at[0].anns[0].start, 0)
      self.assertEqual(at[0].anns[0].end, 16)
      self.assertEqual(at[0].anns[1].tipe, SPKR)
      self.assertEqual(at[0].anns[1]["val"], "R")
      self.assertEqual(at[0].anns[1].start, 17)
      self.assertEqual(at[0].anns[1].end, 43)

  def test1ca050Annotations(self):
      raw = """          INTERVIEW WITH JUNE JACKSON
                              5 June 2000
                           Updated 04/01/10
                     Timecode from Tape 16_BC_DV
                            Topics in Bold

I   This is Tape 16 of camera tape, still on DAT Tape 8, and the DAT time
                code is 24.44, 5 June 2000, Trish FitzSimons on sound, Erica Addis on
                camera, interviewing June Jackson in the Boulia Post Office and this is
                the second tape of June's interview.

                TAPE 16_BC_DV

                So we were talking about your great-grandmother in Charters Towers. Just
                quickly sketch in your life for me in Charters Towers and then we'll get you
                back to the Channel Country.

R   Education
                00:01:14:10    I attended a State School in Charters Towers, then we went to
                high school at a boarding school in Townsville, came back to Charters
                Towers, went to a couple of properties governessing for a few years and was
                on my way to the Territory to governess when I found out that the lady
                whose children I was going to teach, she had died of leukaemia, so I then
                stayed here with my Mum and sister instead of travelling on.

I   So in governessing, how did you view your future? Like, what were your
                dreams as a young woman?
            """
      parts = self.braided.parseFile(raw)
      at = self.braided.parse_annotations(parts["body"])

      self.assertEqual(at[0].text[:12], "This is Tape")


      # first speaker
      self.assertEqual(at[0].anns[0].start, 0)
      self.assertEqual(at[0].anns[0].tipe, SPKR)
      self.assertEqual(at[0].anns[0]["val"], "I")
      turn = at[0].text[at[0].anns[0].start:at[0].anns[0].end]
      self.assertEqual(turn[:12], "This is Tape")
      self.assertEqual(turn[-12:], "el Country.\n")
      self.assertEqual(at[0].anns[0].end, 556)

      # second speaker
      self.assertEqual(at[0].anns[1].start, 557)
      self.assertEqual(at[0].anns[1].tipe, SPKR)
      self.assertEqual(at[0].anns[1]["val"], "R")
      turn = at[0].text[at[0].anns[1].start:at[0].anns[1].end]
      self.assertEqual(turn[:12], "Education\n  ")
      self.assertEqual(turn[-12:], "velling on.\n")
      self.assertEqual(at[0].anns[1].end, 1092)


      # third speaker
      self.assertEqual(at[0].anns[2].start, 1093)
      self.assertEqual(at[0].anns[2].tipe, SPKR)
      self.assertEqual(at[0].anns[2]["val"], "I")
      turn = at[0].text[at[0].anns[2].start:at[0].anns[2].end]
      self.assertEqual(turn[:12], "So in govern")
      self.assertEqual(turn[-12:], "young woman?")

      self.assertEqual(at[0].anns[2].end, 1204)

  def testfd96cc22Annotations(self):
      raw = """I  Okay, so the time code is 33 seconds, it's now 3945 here. This is Tape 11 camera.
        We're still in tape 5 DAT. We're interviewing Liz Debney in the lounge
        room at Glen Ormiston, 4 June 2000.
            """
      at = self.braided.parse_annotations(raw)

      self.assertEqual(at[0].text[:4], "Okay")

  def testfc8bd031(self):
    raw = """     INTERVIEW WITH ISABEL TARRAGO & SHIRLEY FINN
                       3 September 2000
               Timecode refers to tape 68_BC_SP
                         Topics in Bold
            TF = Trish              IT = Isabel SF = Shirley

TF   So this is DAT tape number 25, we're still in Betacam number 68. This
     is the second DAT, third Betacam, interviewing Isabel Tarrago and
     Shirley Finn.

IT   I'm amazed I've done pretty well without coughing.

TF   So Isabel, from your end, you weren't at home, were you, when your family
     left? What's your memory of ...?

IT   Oh, yeah. I had just come home from school, didn't I?

SF   No, I don't think you were.

IT   Yeah, I remember packing that red Ford.

SF   Oh, okay.

IT   The old truck.

SF   Yeah, the red truck. Yes.

IT   Race Relations/Aboriginal Labour

     20:19:15:14      The red truck. And I remember the ... I've got a photograph,
     we've got a photograph of that. And Mum ... we didn't have very much and
     I remember I was all excited because I didn't know all this other stuff was
     going on. I was too young, basically, and I just thought we were going for a
     holiday, and I thought Jimborella, wow!

SF   Big swimming hole.

IT   Big swimming hole.          We had big fun because that's where all the
     corroborees, ceremonies, were and I had a ball because see all the women
     used to look after me and I could just have ... it was just paradise for me.
     And I thought, 'Oh, we're going up' and all I was worried about was my old
     dog. The old black dog.

SF   Yes.
          """
    parts = self.braided.parseFile(raw)
    self.assertEqual(parts["infile_title"], "INTERVIEW WITH ISABEL TARRAGO & SHIRLEY FINN")

    at = self.braided.parse_annotations(parts["body"])

  def testf3a4d841(self):
    raw = """                            INTERVIEW WITH PAM WATSON
                                 4 September 2000
                         Timecode refers to tape 74_BC_SP
                                   Topics in Bold
               TF = Trish   PW = Pam Watson         JH = Julie Hornsey

TF    So this is Betacam No. 74 which is the third Betacam of an interview with
      Pam Watson. It's still um DAT Tape No. 27 and it's 1 hour 2 minutes
      and 25 seconds and this is the 4th September 2000 for the Channels of
      History project.
      74_BC_SP missing t/script 03:01:16:20 - 03:08:06:06
      Some written notes on the printed transcript
PW    That those ideas are hard to under - er er questions because they're so general.
TF    Yes. I know.
PW    Oh um.
TF    03:08:12:08       When I asked David about why it was that you know,
      Mooraberrie having being thickly populated with Aboriginal people they then
      had all disappeared by the time Alice went back, he said it was because the
      family could then get finance. Which is a very - if it's true, you know, it
      suggests that -
PW    I know.
TF    That early on the Duncans were absolutely dependent. You know David said
      yeah, couldn't have existed without Aboriginal people but -
PW    Right.
TF    But once they were established and could get finance, then it was like there
      was a preference for white workers.
PW    Right.
TF    Which, I mean Alice is not necessarily - Alice is speaking from her
      perspective, but it throws an interesting light -
PW    Yes.


DAT 27 AND 28, PART SIDE B
4 September 2000
TF   ... of an interesting life
          """
    parts = self.braided.parseFile(raw)
    self.assertEqual(parts["infile_title"], "INTERVIEW WITH PAM WATSON")

    at = self.braided.parse_annotations(parts["body"])

  def testad09ff2d(self):
    raw = """                               Interview with Anne Kidd
          Transfer from VHS (Betacam Tape No. 12) 15 June 2000
                       TF = Trish, AK = Anne, JH = Julie
              Updated 15/01/10 Timecode refers to tapes 27_BC_SP
                                  Topics in Bold


TF   We're interviewing Anne Kidd on the um steps of - this is what? The
     Community Hall?

AK   Community Hall.

TF   The Community Hall in Windorah.             It's the 15th June 2000.      Trish
     FitzSimons on sound. Julie Hornsey on camera. OK. So are you, yep.

JH   Are you going to be sitting back?
          """
    parts = self.braided.parseFile(raw)
    self.assertEqual(parts["infile_title"], "Interview with Anne Kidd")

    at = self.braided.parse_annotations(parts["body"])
    self.assertEqual(at[0].text[:5], "We're")


if __name__=='__main__':

    unittest.main()
