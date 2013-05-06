'''
This module defines a method genrdf, which takes a metadata dictionary
as parameter and returns a rdflib Graph instance.

'''
from hcsvlab_robochef.rdf.map import *
from hcsvlab_robochef.rdf.namespaces import *

# corpus identifier
ACE = "ACE"
ACENS = corpus_property_namespace(ACE)

ACE_GENRES = {'A': Literal('Press Reportage'),
              'B': Literal('Press Editorials'),
              'C': Literal('Press Reviews'),
              'D': Literal('Religion'),
              'E': Literal('Skills, trades and hobbies'),
              'F': Literal('Popular lore'),
              'G': Literal('Belles lettres, biography, essays'),
              'H': Literal('Miscellaneous'),
              'J': Literal('Learned and scientific writings'),
              'K': Literal('General fiction'),
              'L': Literal('Mystery and detective fiction'),
              'M': Literal('Science fiction'),
              'N': Literal('Adventure and western fiction (bush)'),
              'P': Literal('Romance and love story'),
              'R': Literal('Humour'),
              'S': Literal('Historical fiction'),
              'W': Literal("Women's fiction"),
              }

def zip_removing_none(l1, l2):
    """Behave like zip but remove any elements
    where either l1 or l2 is None"""
    
    return [(a,b) for a,b in zip(l1, l2) if a and b]


def ace_genre_mapper(prop, value):
    """Map genre onto two properties, retain
    ACE:genre but also add a generic AUSNC:genre property"""
    
    
    if ACE_GENRES.has_key(value):
        ace_genre = ACE_GENRES[value]
    else:
        ace_genre = Literal(value)
        
    written_properties = (AUSNC.publication_status, AUSNC.communication_setting, AUSNC.audience)
    # and now map to the generic genres
    if value in ('A', 'B', 'C'):
        genre = (AUSNC.published, AUSNC.popular, AUSNC.mass_market)
    elif value in ('K', 'L', 'M', 'N', 'P', 'R', 'S', 'W'):
        genre = (AUSNC.published, AUSNC.fiction, AUSNC.mass_market)
    elif value in ('D', 'E', 'F'):
        genre = (AUSNC.published, AUSNC.popular, AUSNC.mass_market)
    elif value in ('G', 'J'):
        genre = (AUSNC.published, AUSNC.educational, AUSNC.specialised)
    else: # H
        genre = (AUSNC.published, None, None)
    
    result = [(AUSNC.mode, AUSNC.written), 
              (AUSNC.written_mode, AUSNC["print"]),
              (ACENS.genre, ace_genre)]
    result.extend(zip_removing_none(written_properties, genre))
     
    
    return result
    

aceMap = MetadataMapper(ACE, documentMap = get_generic_doc_mapper())
aceMap.add('genre', mapto=ACENS.genre, mapper=ace_genre_mapper)
aceMap.add('Source', mapto=AUSNC.source)
aceMap.add('Title', mapto=DC.title)
aceMap.add('Author', mapto=DC.contributor)  
aceMap.add('Publisher', mapto=DC.publisher)  # is this right??
aceMap.add('PublicationDate', mapto=DC.created)
aceMap.add('Word Count', ignore=True)

