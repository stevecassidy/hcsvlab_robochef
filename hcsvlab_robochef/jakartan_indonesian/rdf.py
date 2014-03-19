'''
This module defines a method genrdf, which takes a metadata dictionary
as parameter and returns a rdflib Graph instance.
'''

from hcsvlab_robochef.rdf.map import *

JAKARTAN_INDONESIAN = "jakartan_indonesian"
JAKARTAN_INDONESIAN_NS = corpus_property_namespace(JAKARTAN_INDONESIAN)

# mapper for properties of a person
jakartanIndonesianSpeaker = FieldMapper(JAKARTAN_INDONESIAN)
jakartanIndonesianSpeaker.add('Date of birth/Year of birth', mapper=FOAF.birthday)
jakartanIndonesianSpeaker.add('Gender', mapper=FOAF.gender)
jakartanIndonesianSpeaker.add('Age', mapper=FOAF.age)
jakartanIndonesianSpeaker.add('Hobby', mapper=FOAF.interest)


jakartanIndonesianMap = MetadataMapper(JAKARTAN_INDONESIAN, documentMap = get_generic_doc_mapper(), speakerMap=jakartanIndonesianSpeaker)
metadata_defaults(jakartanIndonesianMap)

jakartanIndonesianMap.add('Creator', mapto=DC.creator)
jakartanIndonesianMap.add('Title', mapto=DC.title)
jakartanIndonesianMap.add('Mode', mapto=AUSNC.mode)
jakartanIndonesianMap.add('Speech Style', mapto=AUSNC.speech_style)
jakartanIndonesianMap.add('Interactivity', mapto=AUSNC.interactivity)
jakartanIndonesianMap.add('Communication Context', mapto=AUSNC.communication_context)
jakartanIndonesianMap.add('Audience', mapto=AUSNC.audience)
jakartanIndonesianMap.add('Language (ISO-639)', mapto=OLAC.language)


jakartanIndonesianMap.add('Speakers', ignore=True)
jakartanIndonesianMap.add('Transcript File', ignore=True)

