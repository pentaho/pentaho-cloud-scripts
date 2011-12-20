#!/usr/bin/env python

import argparse
import pentaho_cloud
import pentaho_cloud.aws
from pentaho_cloud import PentahoServerConfig
import sys

parser = argparse.ArgumentParser(description='Generate Pentaho user-data for AWS.')
parser.add_argument('--ssl', required=False, default=False, action='store_const', const=True, help='Enable SSL (self-signed)')
parser.add_argument('--generate-passwords', required=False, default=False, action='store_const', const=True, help='Generate unique password per server (within a reservation)', dest='generate_passwords')
parser.add_argument('--version', required=True, help='Pentaho suite version (e.g. "4.0.0-GA")')
parser.add_argument('--license-dir', required=True, help='Directory containing lic files', dest='license_dir')

parser.add_argument('file', metavar='file', help='File to which to write user-data (gzip)')

args = parser.parse_args()

passwords = []
for i in range(20): # amazon only allows 20 instances per reservation by default
  if (args.generate_passwords):
    passwords.append(pentaho_cloud.mk_passwd())
  else:
    passwords.append('password')

res_dir = sys.path[0] + '/res'

pentaho_cloud.aws.mk_userdata_file(args.file, PentahoServerConfig(args.version, args.license_dir, res_dir, args.ssl, passwords))

if (args.generate_passwords):
  password_file_path = '%s_passwords.txt' % args.file
  password_file = open(password_file_path, 'w')
  for password in passwords:
    password_file.write('%s\n' % password)
  password_file.close()
  print 'Passwords written to %s' % password_file_path