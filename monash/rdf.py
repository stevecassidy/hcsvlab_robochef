'''
This module defines a method genrdf, which takes a metadata dictionary
as parameter and returns a rdflib Graph instance.

'''

from hcsvlab_robochef.rdf.map import *

# corpus identifier
MONASH = "MONASH"

def map_gender(prop, value):
    """Map gender (M or F) to FOAF.gender (male or female)"""
    
    if value == "M":
        value = "male"
    elif value == "F":
        value = "female"
    else:
        # value is unchanged
        pass
    
    return ((FOAF.gender, Literal(value)),)


monashSpkr = FieldMapper(MONASH)
monashSpkr.add("gender", mapper=map_gender)
monashSpkr.add("age", FOAF.age)

monashMap = MetadataMapper(MONASH, monashSpkr, documentMap = get_generic_doc_mapper())
metadata_defaults(monashMap) 
# ignore fields that have been copied to person descriptions
monashMap.add("SEX:", ignore=True)
monashMap.add("SCHOOL:", ignore=True)
monashMap.add("BIRTHPLACE:", ignore=True)
monashMap.add("AGE:", ignore=True)

def map_genre(prop, value):
    """Generate the genre description, for Monash, this is 
    the same for every item"""
    
    return ((AUSNC.mode, AUSNC.spoken),
            (AUSNC.speech_style, AUSNC.spontaneous),
            (AUSNC.interactivity, AUSNC.dialogue),
            (AUSNC.communication_context, AUSNC.face_to_face),
            (AUSNC.audience, AUSNC.small_group),
            (OLAC.discourse_type, OLAC.interactive_discourse),)

monashMap.add('genre', mapper=map_genre)
