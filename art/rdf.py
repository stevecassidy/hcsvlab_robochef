from hcsvlab_robochef.rdf.map import *

ART = "ART"

def uppercase_value(prop, value):
    """return an uppercased version of the value
    in a key value pair"""
    
    return ((prop, Literal(value.upper())),)

def map_gender(prop, value):
    """Map gender (M or F) to FOAF.gender (male or female)"""
    
    value = value.strip()
    if value == "M":
        value = "male"
    elif value == "F":
        value = "female"
    else:
        print "Unknown value for SEX in ART: %s" % value
    
    return ((FOAF.gender, Literal(value)),)


artSpeakerM = FieldMapper(ART)
artSpeakerM.add('name', mapto=FOAF.name)
artSpeakerM.add('gender', mapper=map_gender)
artSpeakerM.add('age', mapto=FOAF.age)

artMapper = MetadataMapper(ART, artSpeakerM, documentMap = get_generic_doc_mapper())