'''
This module defines a method genrdf, which takes a metadata dictionary
as parameter and returns a rdflib Graph instance.

TODO: * finalise mapping
      * use URIs for Classes (Upper, Lower, etc...)
      * maybe create vocabulary for COOEE register and text type
      * extract and convert item sources
'''

from ausnc_ingest.rdf.map import *

COOEE = "COOEE"
COOEENS = corpus_property_namespace(COOEE)

# Map place definitions to dbpedia URIs
PLACE_TRANSLATION = {
    'A': DBPEDIA.Australia,
    'A-QLD': DBPEDIA.Queensland,
    'A-SA': DBPEDIA.South_Australia,
    'A-VDL': DBPEDIA["Van_Diemen%27s_Land"],
    'A-VIC': DBPEDIA.Victoria,
    'A-Vic': DBPEDIA.Victoria,
    'A-WA': DBPEDIA.Western_Australia,
    'A-NSW': DBPEDIA.New_South_Wales,
    'nsw': DBPEDIA.New_South_Wales,
    'CAN': DBPEDIA.Canada,
    'GB': DBPEDIA.Great_Britain,
    'GB-E': DBPEDIA.England,
    'GB-SC': DBPEDIA.Scotland,
    'GB-W': DBPEDIA.Wales,
    'IND': DBPEDIA.India,
    'India': DBPEDIA.India,
    'NI': DBPEDIA.Northern_Ireland,
    'NZ': DBPEDIA.New_Zealand,
    'SA': DBPEDIA.South_Africa,
    'SI': DBPEDIA.Southern_Ireland,
    'Ireland': DBPEDIA.Ireland,
    'USA': DBPEDIA.United_States,
    'Germany': DBPEDIA.Germany,
    'Norfolk Island': DBPEDIA.Norfolk_Island,
    'Portugal': DBPEDIA.Portugal,
    'Italy': DBPEDIA.Italy,
    'At Sea': DBPEDIA.At_Sea,
    'Azores': DBPEDIA.Azores,
    'British Guiana': DBPEDIA.British_Guiana,
    'A/GB': DBPEDIA.Australia,  # This here applies to The Constitution
                                # 1900. (Let's assume it's origin is in
                                # Australia :) )
    'x': DBPEDIA.Unknown,
    '?': DBPEDIA.Unknown,
    }

# DBPedia has URL's for these classes. However, it needs to be checked, whether
# the definitions match.
# dbpedia:Upper_class, dbpedia:Upper_middle_class,
# dbpedia:Lower_middle_class, dbpedia:Working_class (dbpedia:Lower_class)
CLASS_TRANSLATION = {
    'I': Literal(u'Upper Class: Nobility, university education, government '
                 u'service; Parliaments and Committees'),
    'II': Literal(u'Upper Middle Class: educated citizens, gentlemen'),
    'III': Literal(u'Lower Middle Class: free settlers with little education'),
    'IV': Literal(u'Lower Class: convicts, labourers, uneducated people, '
                  u'servants'),
    'x': Literal(u'Unknown'),
    }

# COOEE Register
REGISTER_TRANSLATION = {
    'SB': Literal(u'Speech Based'),
    'PrW': Literal(u'Private Written'),
    'PcW': Literal(u'Public Written'),
    'GE': Literal(u'Government English'),
    'gen': Literal(u'Government English'),
    }

# COOEE Text type
TEXTTYPE_TRANSLATION = {
    'MI': Literal(u'Minutes'),
    'PL': Literal(u'Play'),
    'SP': Literal(u'Speeches'),
    'DI': Literal(u'Diaries'),
    'PC': Literal(u'Private Correspondence'),
    'MM': Literal(u'Memoirs'),
    'NB': Literal(u'Newspapers & Broadsides'),
    'NV': Literal(u'Narratives'),
    'OC': Literal(u'Official Correspondence'),
    'RP': Literal(u'Reports'),
    'VE': Literal(u'Verse'),
    'IC': Literal(u'Imperial Correspondence'),
    'LG': Literal(u'Legal English'),
    'PP': Literal(u'Petitions & Proclamations'),
    }


DISCOURSE_TYPES = {
    'MI': OLAC.oratory,           # Literal(u'Minutes'), Not sure, most are courtroom or parliamentary records
    'PL': OLAC.drama,             # Literal(u'Play'),
    'SP': OLAC.oratory,           # Literal(u'Speeches'),
    'DI': OLAC.narrative,         # Literal(u'Diaries'),
    'PC': AUSNC.letter,           # Literal(u'Private Correspondence'),
    'MM': OLAC.narrative,         # Literal(u'Memoirs'),
    'NB': AUSNC.newspaperArticle, # Literal(u'Newspapers & Broadsides'),
    'NV': OLAC.narrative,         # Literal(u'Narratives'),
    'OC': AUSNC.letter,           # Literal(u'Official Correspondence'),
    'RP': OLAC.report,            # Literal(u'Reports'),
    'VE': AUSNC.verse,            # Literal(u'Verse'),
    'IC': AUSNC.letter,           # Literal(u'Imperial Correspondence'),
    'LG': AUSNC.legal,            # Literal(u'Legal English'),
    'PP': OLAC.oratory,           # Literal(u'Petitions & Proclamations'), SC: not sure about this but seems to fit
    }

def texttype_mapper(prop, val):
    """Map the text type onto the generic discourse_type property
    and the cooee specific texttype"""
    
    val = val.upper()
     
    tt = TEXTTYPE_TRANSLATION.get(val, Literal(val)) 
    gg = DISCOURSE_TYPES.get(val, Literal(val))
    
    return ((COOEENS.texttype, tt), 
            (AUSNC.discourse_type, gg))


def gender_mapper(prop, val):
    """Gender is 'm', 'f', 'x' or 'fam', """
        
    if val == 'f':
        return ((prop, Literal('female')),)
    elif val == 'm':
        return ((prop, Literal('male')),)
    elif val == 'x':
        # unknown gender
        return ((None, None),)
    elif val == 'fam':
    # not really a gender so what should we do? 
        return ((prop, Literal('family')),)
    else: 
        return ((prop, Literal(val)),)


# mapper for properties of a person in COOEE
cooeePerson = FieldMapper(COOEE)
cooeePerson.add('name', mapto=FOAF.name)
cooeePerson.add('birth', mapto=BIO.birth)
cooeePerson.add('gender', mapto=FOAF.gender, mapper=gender_mapper)
cooeePerson.add('origin', mapto=BIO.place, mapper=dictmapper(PLACE_TRANSLATION))
cooeePerson.add('age', mapto=FOAF.age)
cooeePerson.add('status', mapto=COOEENS.status, mapper=dictmapper(CLASS_TRANSLATION))
cooeePerson.add('arrival', mapto=COOEENS.arrival)
cooeePerson.add('abode', mapto=COOEENS.abode)
cooeePerson.add('place', mapto=BIO.place, mapper=dictmapper(PLACE_TRANSLATION))

cooeeMap = MetadataMapper(COOEE, cooeePerson, documentMap = get_generic_doc_mapper())
cooeeMap.add('table_text_year_of_writing', mapto=DC.created)
cooeeMap.add('table_text_place_of_writing', mapto=SCHEMA.localityName, mapper=dictmapper(PLACE_TRANSLATION))
cooeeMap.add('table_text_register', mapto=COOEENS.register, mapper=dictmapper(REGISTER_TRANSLATION))
cooeeMap.add('table_text_type', mapto=COOEENS.texttype, mapper=texttype_mapper)
cooeeMap.add('table_text_number_of_words', mapto=AUSNC.words)

cooeeMap.add('table_source', mapto=DC.source)
cooeeMap.add('table_pages', mapto=BIBO.pages)

# ignore these in-item fields since they duplicate info from the tables
# we could check that they are the same 
cooeeMap.add('item_gender', ignore=True)
cooeeMap.add('item_place', ignore=True)
cooeeMap.add('item_abode', ignore=True)
cooeeMap.add('item_register', ignore=True)
cooeeMap.add('item_age', ignore=True)
cooeeMap.add('item_texttype', ignore=True)
cooeeMap.add('item_status', ignore=True)
cooeeMap.add('table_text_number_of_words', ignore = True)
cooeeMap.add('item_o', mapto=COOEENS.o) # don't know what this is, values are a, b, i, o, u



# TODO: need to encode these relations somehow
cooeeMap.add('table_addressee', mapto=COOEENS.addressee, mapper=cooeePerson)
cooeeMap.add('table_author', mapto=DC.creator, mapper=cooeePerson)

