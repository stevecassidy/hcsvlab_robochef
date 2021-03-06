'''
Created on 30/04/2013

@author: ilya
'''

from sys import argv
from xml.dom.minidom import *


def write_xml(node):
    doc = Document()
    new_node = node.cloneNode(True)
    identifiers = new_node.getElementsByTagName('dc:identifier')
    name = identifiers.item(0).firstChild.nodeValue.strip()
    doc.appendChild(new_node)
    outfile = open(name + '.xml', 'w')
    outfile.write(doc.toxml('utf-8'))

def main(dom):
#    for node in dom.getElementsByTagName('metadata'):
#        write_xml(node)
    for node in dom.getElementsByTagName('record'):
        ident = node.getElementsByTagName('header').item(0).getElementsByTagName('identifier').item(0).firstChild.nodeValue
        rights = node.getElementsByTagName('dc:rights')[0].firstChild.nodeValue

        # only take paradisec items and those where the rights are 'Open'
        if 'paradisec' in ident and 'Open' in rights:
            write_xml(node.getElementsByTagName('metadata').item(0))
        else:
            print "Rejecting", ident

if __name__ == '__main__':
    if len(argv) == 2:
        dom = parse(open(argv[1]))
        main(dom)