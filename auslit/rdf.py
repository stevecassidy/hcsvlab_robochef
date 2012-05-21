'''
This module defines a method genrdf, which takes a metadata dictionary
as parameter and returns a rdflib Graph instance.

'''

from ausnc_ingest.rdf.map import *

AUSLIT = "AUSTLIT"
AUSLITNS = corpus_property_namespace(AUSLIT)

auslitMap = MetadataMapper(AUSLIT, documentMap = get_generic_doc_mapper())
auslitMap.add('genre', mapto=AUSLITNS.genre)
auslitMap.add('fileDesc_sourceDesc_p', mapto=AUSLITNS.source)
auslitMap.add('fileDesc_titleStmt_title', mapto=DC.title)
auslitMap.add('fileDesc_titleStmt_author', mapto=DC.contributor)
auslitMap.add('fileDesc_titleStmt_author_name', mapto=DC.contributor)
auslitMap.add('fileDesc_publicationStmt_publisher', mapto=DC.publisher)
auslitMap.add('fileDesc_publicationStmt_pubPlace', mapto=AUSLITNS.location)
auslitMap.add('fileDesc_profileDesc_creation_date', mapto=DC.created)
auslitMap.add('profileDesc_creation_date', mapto=DC.created)
auslitMap.add('fileDesc_sourceDesc_bibl_imprint_biblScope', mapto=AUSLITNS.volume)


def map_genre(prop, value):
    """Generate the genre description, for Austlit, this is 
    the same for every item"""
    
    return ((AUSNC.mode, AUSNC.written),
            (AUSNC.publication_status, AUSNC.published),
            (AUSNC.written_mode, AUSNC['print']), 
            (AUSNC.communication_setting, AUSNC.fiction),)

