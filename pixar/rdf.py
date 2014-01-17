'''
This module defines a method genrdf, which takes a metadata dictionary
as parameter and returns a rdflib Graph instance.
'''

from hcsvlab_robochef.rdf.map import *

PIXAR = "pixar"
PIXARNS = corpus_property_namespace(PIXAR)


pixarMap = MetadataMapper(PIXAR, documentMap = get_generic_doc_mapper())
metadata_defaults(pixarMap)

pixarMap.add('created', mapto=DC.created)
pixarMap.add('title', mapto=DC.title)
