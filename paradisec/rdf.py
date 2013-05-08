from hcsvlab_robochef.rdf.map import *


def map_type(prop, value):
  value = value.lower().strip()
  if value == 'sound':
    value = 'Audio'
  elif value == 'movingimage':
    value = 'Video'
  elif value == 'instrumental music':
    value = 'Audio'
  print value
  return ((prop, Literal(value)),)


PARADISEC = "PARADISEC"
PARADISECNS = corpus_property_namespace(PARADISEC)


paradisecMap = MetadataMapper(PARADISEC, documentMap = get_generic_doc_mapper())
paradisecMap.add('Box', mapto=DC.box)
paradisecMap.add('DCMIType', mapto=DC.type)
paradisecMap.add('ISO3166', mapto=DC.coverage)
paradisecMap.add('URI', ignore=True)
paradisecMap.add('W3CDTF', mapto=DC.created)
paradisecMap.add('accessRights', mapto=DC.accessRights)
paradisecMap.add('author', mapto=OLAC.author)
paradisecMap.add('bibliographicCitation', mapto=DC.bibliographicCitation)
paradisecMap.add('compiler', mapto=OLAC.compiler)
paradisecMap.add('consultant', mapto=OLAC.consultant)
paradisecMap.add('data_inputter', mapto=OLAC.data_inputter)
paradisecMap.add('depositor', mapto=OLAC.depositor)
paradisecMap.add('description', mapto=DC.description)
paradisecMap.add('discourse-type', mapto=OLAC.discourse_type)
paradisecMap.add('format', ignore=True)
paradisecMap.add('identifier', mapto=DC.identifier)
paradisecMap.add('interviewer', mapto=OLAC.interviewer)
paradisecMap.add('language', mapto=OLAC.language)
paradisecMap.add('linguistic-field', mapto=OLAC.linguistic_field)
paradisecMap.add('linguistic-type', mapto=OLAC.linguistic_type)
paradisecMap.add('photographer', mapto=OLAC.photographer)
paradisecMap.add('recorder', mapto=OLAC.recorder)
paradisecMap.add('researcher', mapto=OLAC.researcher)
paradisecMap.add('rights', mapto=DC.rights)
paradisecMap.add('speaker', mapto=OLAC.speaker)
paradisecMap.add('tableOfContents', ignore=True)
paradisecMap.add('title', mapto=DC.title)
paradisecMap.add('type', mapto=DC.type, mapper=map_type, ignore=True)


