'''
This module defines a method genrdf, which takes a metadata dictionary
as parameter and returns a rdflib Graph instance.

TODO: * finalise mapping
      * use URIs for Classes (Upper, Lower, etc...)
      * maybe create vocabulary for COOEE register and text type
      * extract and convert item sources
'''

from ausnc_ingest.rdf.map import *

BRAID = "BRAIDEDCHANNELS"
BRAIDNS = corpus_property_namespace(BRAID)


# mapper for properties of a person 
braidPerson = FieldMapper(BRAID)
braidPerson.add('name', mapto=FOAF.name)
 
braidedMap = MetadataMapper(BRAID, documentMap = get_generic_doc_mapper(), speakerMap=braidPerson) 

braidedMap.add('Date transcription last modified', mapto=DC.created)
braidedMap.add('Place of recording', mapto=BRAIDNS.place)
braidedMap.add('Contributor of recording', mapto=OLAC.contributor)
braidedMap.add('Number of pages', ignore=True)
braidedMap.add('Date of recording', mapto=OLAC.recordingdate)
braidedMap.add('Length of transcript', mapto=BRAIDNS.lengthOfTranscript)
braidedMap.add('Length of recording', mapto=BRAIDNS.lengthOfRecording)
braidedMap.add('Number of people', mapto=BRAIDNS.numberOfPeople)
braidedMap.add('Creator', mapto=DC.creator)
braidedMap.add('contributor', mapto=DC.contributor)
braidedMap.add('description', mapto=DC.description)
braidedMap.add('title', mapto=DC.title)


braidedMap.add('item_owner', ignore=True)
braidedMap.add('item_history_resetworkflow', ignore=True)
braidedMap.add('item_history_statechange', ignore=True)
braidedMap.add('item_history_newitem', ignore=True)
braidedMap.add('item_history_edit', ignore=True)
braidedMap.add('BC_identifier', ignore=True)
braidedMap.add('item_attachments_attachment_conversion', ignore=True) 
braidedMap.add('item_attachments_attachment_file', ignore=True)
braidedMap.add('item_attachments_attachment_description', ignore=True)
braidedMap.add('item_attachments_attachment_thumbnail', ignore=True)
braidedMap.add('item_attachments_attachment_uuid', ignore=True)
braidedMap.add('item_attachments_attachment_size', ignore=True)
braidedMap.add('item_datecreated', ignore=True)
braidedMap.add('item_datemodified', ignore=True)
braidedMap.add('item_dateforindex', ignore=True)
braidedMap.add('item_name', ignore=True)
braidedMap.add('item_newitem', ignore=True)
braidedMap.add('itemwordcount', ignore=True)
braidedMap.add('resource_type', ignore=True)
braidedMap.add('infile_participants', ignore=True)

def clean_notes(prop, value):
    
    result = " ".join(value)
    result = result.strip()
    if len(result) == 0:
        return [(None, None)]
    else:
        return [(AUSNC.infile_notes, Literal(result))]

braidedMap.add('infile_notes2', mapper=clean_notes)




def map_genre(prop, value):
    """Generate the genre description, for Braided Channels, this is 
    the same for every item"""
    
    return ((AUSNC.mode, AUSNC.spoken),
            (AUSNC.speech_style, AUSNC.spontaneous),
            (AUSNC.interactivity, AUSNC.interview),
            (AUSNC.communication_context, AUSNC.face_to_face),
            (AUSNC.audience, AUSNC.individual),
            (OLAC.discourse_type, OLAC.interactive_discourse),)

braidedMap.add('genre', mapper=map_genre)

