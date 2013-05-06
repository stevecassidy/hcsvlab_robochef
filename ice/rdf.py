'''
This module defines a method genrdf, which takes a metadata dictionary
as parameter and returns a rdflib Graph instance.

For the ICE corpus

TODO: 

'''

from hcsvlab_robochef.rdf.map import *

ICE = "ICE"
ICENS = corpus_property_namespace(ICE)

def uppercase_value(prop, value):
    """return an uppercased version of the value
    in a key value pair"""
    
    return ((prop, Literal(value.upper())),)

def map_gender(prop, value):
    """Map gender (M or F) to FOAF.gender (male or female)"""
    
    if value == "M":
        value = "male"
    elif value == "F":
        value = "female"
    else:
        print "Unknown value for SEX in ICE: %s" % value
        #raise Exception("Unknown value for SEX in ICE: %s" % value)
    
    return ((FOAF.gender, Literal(value)),)

iceSpeakerM = FieldMapper(AUSNC)
iceSpeakerM.add('name', mapto=FOAF.name)
iceSpeakerM.add('occupation', mapto=AUSNC.occupation)
iceSpeakerM.add('gender', mapper=map_gender)
iceSpeakerM.add('education', mapto=AUSNC.education)
iceSpeakerM.add('age', mapto=FOAF.age)
iceSpeakerM.add('surname', mapto=FOAF.lastName)
iceSpeakerM.add('forename', mapto=FOAF.firstName)

def letter_genre_mapper(prop, value):
    """Determine what kind of letter this is and 
    return a value for AUSNC.communication_setting"""
    
    if value.startswith("Personal"):
        return ((AUSNC.communication_setting, AUSNC.informal),)
    else:
        return ((AUSNC.communication_setting, AUSNC.intitutional),)


def zip_removing_none(l1, l2):
    """Behave like zip but remove any elements
    where either l1 or l2 is None"""
    
    return [(a,b) for a,b in zip(l1, l2) if a and b]


genre_properties = (AUSNC.speechStyle, AUSNC.interactivity, AUSNC.communication_context, AUSNC.communication_setting, AUSNC.audience)
genre_map = {
      # mode, speech-style, interactivity, communication-context, communication-setting, audience
     'Broadcast discussion': (AUSNC.spontaneous,  AUSNC.dialogue, AUSNC.face_to_face, AUSNC.informal, AUSNC.massed),
     "Broadcast" :           (AUSNC.spontaneous,  AUSNC.dialogue, AUSNC.face_to_face, AUSNC.informal, AUSNC.massed),
     "Broadcast interview":  (AUSNC.spontaneous,  AUSNC.dialogue, AUSNC.face_to_face, AUSNC.informal, AUSNC.massed),
     "Business transaction": (AUSNC.spontaneous,  AUSNC.dialogue, AUSNC.face_to_face, AUSNC.business, AUSNC.individual),
     "Class lesson":         (AUSNC.spontaneous,  AUSNC.dialogue, AUSNC.face_to_face, AUSNC.educational, AUSNC.small_group),
     "Class lessons":        (AUSNC.spontaneous,  AUSNC.dialogue, AUSNC.face_to_face, AUSNC.educational, AUSNC.small_group),
     "Class Lesson":         (AUSNC.spontaneous,  AUSNC.dialogue, AUSNC.face_to_face, AUSNC.educational, AUSNC.small_group),
     "Class Lessons":        (AUSNC.spontaneous,  AUSNC.dialogue, AUSNC.face_to_face, AUSNC.educational, AUSNC.small_group),
     "Dialogue:private:direct conversation": (AUSNC.spontaneous,  AUSNC.dialogue, AUSNC.face_to_face, AUSNC.informal, AUSNC.small_group),  # may be individual or small group
     "Dialogue:private:distance conversation": (AUSNC.spontaneous,  AUSNC.dialogue, AUSNC.distance, AUSNC.informal, AUSNC.individual), # medium?
     "Legal Cross-examination":                 (AUSNC.spontaneous,  AUSNC.interview, AUSNC.face_to_face, AUSNC.legal, AUSNC.small_group),
     "Monologue:public:broadcast news":         (AUSNC.scripted,  AUSNC.monologue, AUSNC.distance, None, AUSNC.massed),
     "Monologue:public:broadcast talks":        (AUSNC.scripted,  AUSNC.monologue, AUSNC.distance, None, AUSNC.massed),
     "Monologue:public:demonstration":          (AUSNC.spontaneous,  AUSNC.monologue, AUSNC.face_to_face, AUSNC.informal, AUSNC.massed),
     "Monologue:public:legal presentation":     (AUSNC.spontaneous,  AUSNC.monologue, AUSNC.face_to_face, AUSNC.legal, AUSNC.small_group),
     "Monologue:public:non-broadcast speech":   (AUSNC.scripted,  AUSNC.monologue, AUSNC.face_to_face, AUSNC.formal, AUSNC.small_group),
     "Monologue:public:spontaneous commentary": (AUSNC.spontaneous,  AUSNC.monologue, AUSNC.face_to_face, AUSNC.informal, AUSNC.small_group),
     "Monologue:public:unscripted speech":      (AUSNC.spontaneous,  AUSNC.monologue, AUSNC.face_to_face, AUSNC.formal, AUSNC.small_group),
     "Parliamentary debate":  (AUSNC.spontaneous,  AUSNC.dialogue, AUSNC.face_to_face, AUSNC.government, AUSNC.specialised),
     "Parliamentary Debates": (AUSNC.spontaneous,  AUSNC.dialogue, AUSNC.face_to_face, AUSNC.government, AUSNC.specialised),
}  


def genre_mapper(prop, value):
    """Map genre into our eight way feature set"""
    
    if genre_map.has_key(value):
        return zip_removing_none(genre_properties, genre_map[value])
    else:
        return None

def broadcast_mapper(prop, value):
    """Map the tv_or_radio property to communication-medium"""
    
    if value == "radio":
        return ((AUSNC.communication_medium, AUSNC.radio),)
    else:
        return ((AUSNC.communication_medium, AUSNC.television),)

written_properties = (AUSNC.publication_status, AUSNC.communication_setting, AUSNC.audience)
written_categories = {
    "W1A": (AUSNC.unpublished, AUSNC.educational, AUSNC.individual),  # student essays
    "W1B": (AUSNC.unpublished, None, AUSNC.individual),  # letters, personal or business
    "W2A": (AUSNC.published, AUSNC.educational, AUSNC.specialised),  # Academic writing, published
    "W2B": (AUSNC.published, AUSNC.popular, AUSNC.mass_market),  # magazine articles
    "W2C": (AUSNC.published, AUSNC.popular, AUSNC.mass_market),  # newspaper articles
    "W2D": (AUSNC.published, AUSNC.popular, AUSNC.mass_market),  # handbooks and guides
    "W2E": (AUSNC.published, AUSNC.popular, AUSNC.mass_market),  # newspaper articles
    "W2F": (AUSNC.published, AUSNC.fiction, AUSNC.mass_market),  # popular fiction
    }


def category_mapper(prop, value):
    """A mapper for the category that we use to
    insert category metadata into each item for those
    that have no genre etc. information"""
     
    result = []
    if value.startswith('W'):
        result.extend([(AUSNC.mode, AUSNC.written), (AUSNC.written_mode, AUSNC["print"])]) 
        result.extend(zip_removing_none(written_properties, written_categories[value]))
    else:
        result.extend([(AUSNC.mode, AUSNC.spoken)])
      
    return result


def genre_subject_mapper(prop, value):
    """Map the genre subject info in W1A which has eg.
    Untimed Student Essay - Computational Linguistics
    which we split into two properties"""
    
    (genre, subject) = value.split('-')
    
    
    return ((AUSNC.mode, AUSNC.written),
            (AUSNC.publication_status, AUSNC.unpublished),
            (AUSNC.written_mode, AUSNC["print"]),
            (AUSNC.communication_setting, AUSNC.educational),
            (AUSNC.audience, AUSNC.individual),
            (AUSNC.genre, Literal(genre.strip())),
            (DC.subject, Literal(subject.strip())))

iceM = MetadataMapper(ICE, iceSpeakerM, documentMap = get_generic_doc_mapper())
iceM.add('table_category', mapper=genre_mapper)
iceM.add('table_letter_genre', mapper=letter_genre_mapper)
iceM.add('table_date_of_recording', mapto=DC.created)
iceM.add('date_of_publication', mapto=DC.created)
iceM.add('table_number_of_speakers', ignore=True)
iceM.add('table_place_of_recording', mapto=ICENS.recordingplace)
iceM.add('table_tv_or_radio', mapper=broadcast_mapper)
iceM.add('table_subject', mapto=DC.subject)
iceM.add('table_source_title', mapto=DC.title)
iceM.add('table_program', mapto=DC.title)
iceM.add('table_free_comments', mapto=AUSNC.comment)
iceM.add('table_recorder', mapto=OLAC.recorder)
iceM.add('publisher', mapto=DC.publisher)


iceM.add('table_identifier', ignore=True)
iceM.add('table_wordcount', ignore = True)
iceM.add('table_number_of_subtexts', ignore=True)
iceM.add('category', mapper=category_mapper)
iceM.add('table_subtext_number', ignore=True)    # only used a few times
iceM.add('number_of_subtexts', ignore=True)# with two spellings, not useful info
iceM.add('table_version', ignore=True) # sometimes has the value 'proof heard', not useful
iceM.add('table_textcode', ignore=True)# used once
iceM.add('table_audience', ignore=True)# used once
iceM.add('table_audience_size', ignore=True)# used once

iceM.add('table_genre_subject', mapper=genre_subject_mapper)

# some written samples have an author
iceM.add('author', mapto=DC.creator)



    #===========================================================================
    # ICE properties not dealt with and their frequencies
    #
    # 73 table_channel
    # 105 table_communicative_situation
    # 10 table_consent
    # 26 table_mode
    # 20 table_number_of_participants 
    #  7 table_organising_body
    # 356 table_wordcount
    #===========================================================================

