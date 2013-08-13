
Scripts to harvest Paradisec metadata from their OAI-PMH feed at
http://catalog.paradisec.org.au/oai/item?verb=ListRecords&metadataPrefix=olac
and prep it for RoboCheffing.

harvester.py:
  Pulls metadata from the Paradisec catalog & produces XML files for
  each page of data retrieved.

split.py:
  Splits up the files retrieved by the harvester script to produce one xml
  per item.

This needs scripting, but can be run like:

$ python harvester.py

$ ls paradisec-olac-metadata-page-*.xml | while read file
> do
>  echo "Processing $file"
>  python split.py $file
> done
