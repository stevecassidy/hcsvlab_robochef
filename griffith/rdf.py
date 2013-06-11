'''
This module defines a method genrdf, which takes a metadata dictionary
as parameter and returns a rdflib Graph instance.

TODO: * finalise mapping
      * use URIs for Classes (Upper, Lower, etc...)
      * maybe create vocabulary for COOEE register and text type
      * extract and convert item sources
'''

from hcsvlab_robochef.rdf.map import *

GRIFF = "GCSAUSE"
GRIFFNS = corpus_property_namespace(GRIFF) 


# mapper for properties of a person in COOEE
griffPerson = FieldMapper(GRIFFNS)
griffPerson.add('name', mapto=FOAF.name)

# The following fields contain sensitive data, exclude from the site
griffPerson.add('owner', ignore=True)
griffPerson.add('edit', ignore = True)
griffPerson.add('resetworkflow', ignore = True)
griffPerson.add('statechange', ignore = True)

griffDocument = get_generic_doc_mapper()

# The following fields contain sensitive data, exclude from the site
griffDocument.add('Title', mapto=DC.title)
griffDocument.add('Creator', mapto=DC.creator)
griffDocument.add('owner', ignore = True)
griffDocument.add('edit', ignore = True)
griffDocument.add('resetworkflow', ignore = True)
griffDocument.add('statechange', ignore = True)
griffDocument.add('temp_fileHandler', ignore = True)
griffDocument.add('size', ignore = True)
griffDocument.add('uuid', ignore = True)
griffDocument.add('newitem', ignore = True)
griffDocument.add('datecreated', ignore = True)
griffDocument.add('dateforindex', ignore = True)
griffDocument.add('datemodified', ignore = True)
griffDocument.add('description', ignore = True)
griffDocument.add('conversion', ignore = True)
griffDocument.add('GCSAusEUniqueID', ignore = True)

griffMap = MetadataMapper(GRIFF, griffPerson, griffDocument)
metadata_defaults(griffMap)
griffMap.add('Date transcription last modified', mapto=DC.created)
griffMap.add('Place of recording', mapto=GRIFFNS.place)
griffMap.add('Contributor of recording', mapto=OLAC.contributor)
griffMap.add('Number of pages', ignore=True)
griffMap.add('Date of recording', mapto=OLAC.recordingdate)
griffMap.add('Length of transcript', ignore=True)
griffMap.add('Length of recording', mapto=GRIFFNS.lengthOfRecording)
griffMap.add('Number of people', mapto=GRIFFNS.numberOfPeople)
griffMap.add('Creator', mapto=DC.creator)
griffMap.add('Title', mapto=DC.title)
 
def map_genre(prop, value):
    """Generate the genre description, for Griffith, this is 
    the same for every item"""
    
    return ((AUSNC.mode, AUSNC.spoken),
            (AUSNC.speech_style, AUSNC.spontaneous),
            (AUSNC.interactivity, AUSNC.dialogue),
            (AUSNC.communication_context, AUSNC.face_to_face),
            (AUSNC.audience, AUSNC.small_group),
            (OLAC.discourse_type, OLAC.interactive_discourse),)

griffMap.add('genre', mapper=map_genre)


