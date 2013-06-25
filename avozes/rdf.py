'''
This module defines a method genrdf, which takes a metadata dictionary
as parameter and returns a rdflib Graph instance.

TODO: * finalise mapping
      * use URIs for Classes (Upper, Lower, etc...)
      * maybe create vocabulary for COOEE register and text type
      * extract and convert item sources
'''

from hcsvlab_robochef.rdf.map import *

AVOZES = "AVOZES"
AVOZESNS = corpus_property_namespace(AVOZES)


# mapper for properties of a person 
avozesPerson = FieldMapper(AVOZES)
avozesPerson.add('name', mapto=FOAF.name)
 
avozesMap = MetadataMapper(AVOZES, documentMap = get_generic_doc_mapper(), speakerMap=avozesPerson) 
metadata_defaults(avozesMap)

avozesMap.add('created', mapto=DC.created)
avozesMap.add('Place of recording', mapto=AVOZESNS.place)
avozesMap.add('Contributor of recording', mapto=OLAC.contributor)
avozesMap.add('Number of pages', ignore=True)
avozesMap.add('Date of recording', mapto=OLAC.recordingdate)
avozesMap.add('Length of transcript', mapto=AVOZESNS.lengthOfTranscript)
avozesMap.add('Length of recording', mapto=AVOZESNS.lengthOfRecording)
avozesMap.add('Number of people', mapto=AVOZESNS.numberOfPeople)
avozesMap.add('Creator', mapto=DC.creator)
avozesMap.add('contributor', mapto=DC.contributor)
avozesMap.add('description', mapto=DC.description)
avozesMap.add('title', mapto=DC.title)


avozesMap.add('item_owner', ignore=True)
avozesMap.add('item_history_resetworkflow', ignore=True)
avozesMap.add('item_history_statechange', ignore=True)
avozesMap.add('item_history_newitem', ignore=True)
avozesMap.add('item_history_edit', ignore=True)
avozesMap.add('BC_identifier', ignore=True)
avozesMap.add('item_attachments_attachment_conversion', ignore=True) 
avozesMap.add('item_attachments_attachment_file', ignore=True)
avozesMap.add('item_attachments_attachment_description', ignore=True)
avozesMap.add('item_attachments_attachment_thumbnail', ignore=True)
avozesMap.add('item_attachments_attachment_uuid', ignore=True)
avozesMap.add('item_attachments_attachment_size', ignore=True)
avozesMap.add('item_datecreated', ignore=True)
avozesMap.add('item_datemodified', ignore=True)
avozesMap.add('item_dateforindex', ignore=True)
avozesMap.add('item_name', ignore=True)
avozesMap.add('item_newitem', ignore=True)
avozesMap.add('itemwordcount', ignore=True)
avozesMap.add('resource_type', ignore=True)
avozesMap.add('infile_participants', ignore=True)

def clean_notes(prop, value):
    
    result = " ".join(value)
    result = result.strip()
    if len(result) == 0:
        return [(None, None)]
    else:
        return [(AUSNC.infile_notes, Literal(result))]

avozesMap.add('infile_notes2', mapper=clean_notes)




def map_genre(prop, value):
    """Generate the genre description, for Avozes Channels, this is 
    the same for every item"""
    
    return ((AUSNC.mode, AUSNC.spoken),
            (AUSNC.speech_style, AUSNC.spontaneous),
            (AUSNC.interactivity, AUSNC.interview),
            (AUSNC.communication_context, AUSNC.face_to_face),
            (AUSNC.audience, AUSNC.individual),
            (OLAC.discourse_type, OLAC.interactive_discourse),)

avozesMap.add('genre', mapper=map_genre)

