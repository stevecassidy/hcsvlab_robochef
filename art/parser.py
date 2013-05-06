from pyparsing import *
from hcsvlab_robochef.annotations.annotation import *
from hcsvlab_robochef.annotations.annotated_text import *


# Define grammar for ART source data
speakerTokens = alphas + nums + ":,-"
speakerTokenGrammar = Suppress("[") + Group(OneOrMore(Word(speakerTokens))) + Suppress("]")
speakerTurnDefn = speakerTokenGrammar.setResultsName("name") + (SkipTo((speakerTokenGrammar ^ StringEnd()), False).setResultsName("value"))
completeGrammar = OneOrMore(speakerTurnDefn)

        
def parseCompleteDocument(source):
    """
    This function parses the entire ART sample document and splits the speaker turns into a list of turn and content.
    For example [P1] Some content.
    is split into ['P1', 'Some content.']
    
    This function is used to parse the master document into a list used to generate the samples
    """
    # Though technically there should only be one match we use the for loop
    # as it makes the code easier to read.
    for match in completeGrammar.searchString( source ):
        return match
    
    
def correctionParser():
    """ In the art corpus, a correction is annotated with a {} surrounding the corrected text """
    return Suppress(u"{") \
        + (CharsNotIn(u" ,}").setParseAction(lambda s, loc, toks: AnnotatedText('', [annotation.Annotation("correction",toks[0], 0, 0)]))) \
        + Suppress(u"}")
      
      
def artpauseParser():
    """ This parser absorbs the pause meta data which is <,> """
    return (Suppress(u"<") + Suppress(u",") + Suppress(u">")).setParseAction(lambda s, loc, toks: AnnotatedText(" ",[annotation.Annotation("pause", None, 0, 0)]))
    
    
def interjectionParser():
    """ This parser absorbs the pause meta data which is <words> """
    return Suppress(u"<") \
        + (CharsNotIn(u">").setParseAction(lambda s, loc, toks: AnnotatedText("", [annotation.Annotation("interjection",toks[0], 0, 0)]))) \
        + Suppress(u">")

