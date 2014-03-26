
import urllib
import urllib2
from xml.dom.minidom import parse, parseString
import datetime
import codecs

# function for return dom response after parsting oai-pmh URL
def oaipmh_response(URL):
 file = urllib2.urlopen(URL)
 data = file.read()
 file.close()
 
 dom = parseString(data)
 return dom

# function for getting value of resumptionToken after parsting oai-pmh URL
def oaipmh_resumptionToken(URL):
 print "opening", URL
 file = urllib2.urlopen(URL)
 data = file.read()
 file.close()
 
 dom = parseString(data)

 token = ""

 try:
   token = dom.getElementsByTagName('resumptionToken')[0].firstChild.nodeValue
   print "START: "+str(datetime.datetime.now())
 except:
   print "No resumption token"
   token = ""

 return token

# function for writing to output files
def write_xml_file(inputData, outputFile, mode):
 oaipmhResponse = codecs.open(outputFile, mode, "utf-8")
 #xml = parseString(inputData)
 #prettyData = xml.toprettyxml('  ', '', 'utf-8')
 #prettyData=prettyData.replace("\t","")
 #prettyData=prettyData.replace('"?><','"?>\n<')
 #prettyData=re.sub(trails,"\n",prettyData)
 oaipmhResponse.write(inputData)
 oaipmhResponse.close()
 print "END: "+str(datetime.datetime.now())

#
# main code
#

# http://catalog.paradisec.org.au/oai/item?verb=ListRecords&metadataPrefix=olac

baseURL = 'http://catalog.paradisec.org.au/oai/item'
getRecordsURL = str(baseURL+'?verb=ListRecords&metadataPrefix=olac')
 
# initial parse phase
resumptionToken = oaipmh_resumptionToken(getRecordsURL) # get initial resumptionToken
print "Resumption Token: "+resumptionToken
outputFile = 'paradisec-olac-metadata-page-0.xml' # define initial file to use for writing response
write_xml_file(oaipmh_response(getRecordsURL).toxml(), outputFile, "w")
 
# loop parse phase
pageCounter = 1
while resumptionToken != "":
 print "URL ECONDED TOKEN: "+resumptionToken
 resumptionToken = urllib.urlencode({'resumptionToken':resumptionToken}) # create resumptionToken URL parameter
 print "Resumption Token: "+resumptionToken
 getRecordsURLLoop = str(baseURL+'?verb=ListRecords&'+resumptionToken)
 oaipmhXML = oaipmh_response(getRecordsURLLoop).toxml()
 outputFile = 'paradisec-olac-metadata-page-'+str(pageCounter)+".xml" # create file name to use for writing response
 write_xml_file(oaipmhXML, outputFile, "w") # write response to output file
 
 resumptionToken = oaipmh_resumptionToken(getRecordsURLLoop)
 pageCounter += 1 # increment page counter
