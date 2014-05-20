'''
This module defines a method genrdf, which takes a metadata dictionary
as parameter and returns a rdflib Graph instance.
'''

from hcsvlab_robochef.rdf.map import *

LLC = "llc"
LLCNS = corpus_property_namespace(LLC)


llcMap = MetadataMapper(LLC, documentMap=get_generic_doc_mapper())
metadata_defaults(llcMap)

llcMap.add('Date Given', mapto=DC.created)
llcMap.add('Recording', mapto=DC.title)

