from ausnc_ingest.annotations import annotated_text
from ausnc_ingest.annotations import annotation_parsers
from ausnc_ingest.annotations import ca_annotation_parsers
from ausnc_ingest.annotations import cap

from ausnc_ingest.annotations.annotation import Annotation, AnnotationCollection


# classes 
AnnotatedText = annotated_text.AnnotatedText

# methods
concatAnnotatedText = annotated_text.concat
slurpParser         = annotation_parsers.slurpParser
exactParser         = annotation_parsers.exactParser
aceCorrectionParser = annotation_parsers.aceCorrectionParser
markupParser        = annotation_parsers.markupParser
everythingParser    = annotation_parsers.everythingParser
oneOrMoreParsers    = annotation_parsers.oneOrMoreParsers
speakerParser       = annotation_parsers.speakerParser
knownSpeakerParser  = annotation_parsers.knownSpeakerParser
monashOverlapParser = annotation_parsers.monashOverlapParser
monashLaughterParser= annotation_parsers.monashLaughterParser
cooeeParagraphParser= annotation_parsers.cooeeParagraphParser
redactParser        = annotation_parsers.redactParser
unknownParser       = ca_annotation_parsers.unknownParser
micropauseParser    = ca_annotation_parsers.micropauseParser
pauseParser         = ca_annotation_parsers.pauseParser
elongationParser    = ca_annotation_parsers.elongationParser
uncertaintyParser   = ca_annotation_parsers.uncertaintyParser
intonationParser    = ca_annotation_parsers.intonationParser
dubiousOrNonsenseParser    = ca_annotation_parsers.dubiousOrNonsenseParser
softParser          = ca_annotation_parsers.softParser
speedParser         = ca_annotation_parsers.speedParser
latchedParser       = ca_annotation_parsers.latchedParser

# package functions
def unittests():
  res = annotated_text.unittests()
  res.addTest(annotation_parsers.unittests())
  res.addTest(ca_annotation_parsers.unittests())
  res.addTest(cap.unittests())
  return res
