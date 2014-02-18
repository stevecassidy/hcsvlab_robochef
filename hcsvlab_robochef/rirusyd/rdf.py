'''
This module defines a method genrdf, which takes a metadata dictionary
as parameter and returns a rdflib Graph instance.
'''

from hcsvlab_robochef.rdf.map import *

RIR = "rirusyd"
RIRNS = corpus_property_namespace(RIR)


rirMap = MetadataMapper(RIR, documentMap = get_generic_doc_mapper())
metadata_defaults(rirMap)

rirMap.add('Created', mapto=DC.created)
rirMap.add('Title', mapto=DC.title)
rirMap.add('Source', mapto=DC.source)
