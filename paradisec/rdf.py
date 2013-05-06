'''
Created on 02/05/2013

@author: ilya
'''

from hcsvlab_robochef.rdf.map import *

PARADISEC = "PARADISEC"
PARADISECNS = corpus_property_namespace(PARADISEC)

paradisecMap = MetadataMapper(PARADISEC)
paradisecMap.add('Box', mapto=DC.box)
paradisecMap.add('DCMIType', mapto=DC.type)
paradisecMap.add('ISO3166', mapto=DC.coverage)
paradisecMap.add('URI', mapto=DC.source)
paradisecMap.add('W3CDTF', mapto=DC.date )
paradisecMap.add('accessRights', mapto=DC.accessRights)
paradisecMap.add('author', mapto=OLAC.author)
paradisecMap.add('bibliographicCitation', mapto=DC.bibliographicCitation)
paradisecMap.add('compiler', mapto=OLAC.compiler)
paradisecMap.add('consultant', mapto=OLAC.consultand)
paradisecMap.add('data_inputter', mapto=OLAC.data_inputters)
paradisecMap.add('depositor', mapto=OLAC.depositor)
paradisecMap.add('description', mapto=DC.description)
paradisecMap.add('discourse-type', mapto=OLAC.discourse-type)
paradisecMap.add('format', mapto=DC.format)
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
paradisecMap.add('tableOfContents', mapto=DC.tableOfContents)
paradisecMap.add('title', mapto=DC.title)
paradisecMap.add('type', mapto=DC.type)


