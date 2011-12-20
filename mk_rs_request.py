#!/usr/bin/env python

import argparse
import pentaho_cloud
import pentaho_cloud.rs
from pentaho_cloud import PentahoServerConfig
import sys

parser = argparse.ArgumentParser(description='Generate Rackspace Cloud personality.')
parser.add_argument('--ssl', required=False, default=False, action='store_const', const=True, help='Enable SSL (self-signed)')
parser.add_argument('--generate-password', required=False, default=False, action='store_const', const=True, help='Generate unique password', dest='generate_password')
parser.add_argument('--version', required=True, help='Pentaho suite version (e.g. "4.0.0-GA")')
parser.add_argument('--license-dir', required=True, help='Directory containing lic files', dest='license_dir')
parser.add_argument('--instance-name', required=False, default='pentaho_cloud', help='Instance name', dest='instance_name')
parser.add_argument('--image-id', required=True, help='Image ID', dest='image_id')
parser.add_argument('--flavor-id', required=False, default='4', help='Flavor ID', dest='flavor_id')

parser.add_argument('file', metavar='file', help='File to which to write request (xml)')

args = parser.parse_args()


passwords = []
if (args.generate_password):
  passwords.append(pentaho_cloud.mk_passwd())
else:
  passwords.append('password')

if (args.generate_password):
  print 'Generated password: %s' % passwords[0]

res_dir = sys.path[0] + '/res'

pentaho_cloud.rs.mk_request_file(args.file, args.instance_name, args.image_id, args.flavor_id, PentahoServerConfig(args.version, args.license_dir, res_dir, args.ssl, passwords))
