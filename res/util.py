#!/usr/bin/env python
# encoding: utf-8

# PRE-REQUISITES
# sudo apt-get install python-setuptools
# sudo apt-get install libxml2-dev
# sudo apt-get install libxslt1-dev
# sudo apt-get install python-dev
# sudo easy_install lxml
# tested on Ubuntu 10.04

import sys
import getopt
from lxml import etree

def enable_ssl(in_file, ssl_port):
  tree = etree.parse(in_file)
#  nodes = tree.xpath('/Server/Connector[port="' + ssl_port + '"]');
  nodes = tree.xpath('/Server/Service')
  nodes[0].insert(0, etree.Element("Connector", URIEncoding="UTF-8", port=ssl_port, protocol="HTTP/1.1", SSLEnabled="true", maxThreads="150", scheme="https", secure="true", clientAuth="false", sslProtocol="TLS"))
  f = open(in_file, 'w')
  f.write(etree.tostring(tree, encoding="utf-8", xml_declaration=True))
  f.close()

def main(argv):
  try:                                
    opts, args = getopt.getopt(argv, "s")
  except getopt.GetoptError:
    sys.exit(2)              
  for opt, arg in opts:
    if opt == '-s':
      enable_ssl(argv[1], argv[2])


if __name__ == '__main__':
  main(sys.argv[1:])
  