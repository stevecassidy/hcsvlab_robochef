'''
This module defines a method genrdf, which takes a metadata dictionary
as parameter and returns a rdflib Graph instance.

'''

from hcsvlab_robochef.rdf.map import *

def map_gender(prop, value):
  '''
  Map gender (M or F) to FOAF.gender (male or female)
  '''
  if value.strip().upper() == 'M':
      value = 'male'
  elif value.strip().upper() == 'M?':
      value = 'male?'
  elif value.strip().upper() == 'F':
      value = 'female'
  elif value.strip().upper() == '':
      value = ''
  else:
      raise Exception("Unknown value for gender in MD: %s" % value)
  
  return ((FOAF.gender, Literal(value)),)

def map_genre(prop, value):
    """Generate the genre description, for MD, this is 
    the same for every item"""
    
    result = [(AUSNC.mode, AUSNC.spoken),
              (AUSNC.communication_context, AUSNC.face_to_face),
              (AUSNC.audience, AUSNC.individual),
              (OLAC.discourse_type, OLAC.interactive_discourse)]
    
    if value == 'interview':
        result += [(AUSNC.speech_style, AUSNC.spontaneous),
                   (AUSNC.interactivity, AUSNC.interview)]
    else:
        result += [(AUSNC.speech_style, AUSNC.scripted),
                   (AUSNC.interactivity, AUSNC.read)]
    
    
    return result
      
MD = "MITCHELDELBRIDGE"
      
mdSpeakerM = FieldMapper(AUSNC)
mdSpeakerM.add('gender', mapper=map_gender)
mdSpeakerM.add('birthplace', mapto=AUSNC.birthplace)
mdSpeakerM.add('state', mapto=AUSNC.state)
mdSpeakerM.add('fathers_bithplace', mapto=AUSNC.fathers_birthplace)
mdSpeakerM.add('fathers_occupation', mapto=AUSNC.fathers_occupation)
mdSpeakerM.add('mothers_birthplace', mapto=AUSNC.mothers_birthplace)

mdMap = MetadataMapper(MD, mdSpeakerM, documentMap = get_generic_doc_mapper()) 
metadata_defaults(mdMap)
mdMap.add('genre', mapper=map_genre)




