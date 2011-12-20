#!/usr/bin/env python

import argparse
import pentaho_cloud
import pentaho_cloud.aws
import pentaho_cloud.aws.connect
from pentaho_cloud import PentahoServerConfig
from pentaho_cloud.aws.connect import AwsProviderConfig
import os
import sys

parser = argparse.ArgumentParser(description='Launch Pentaho on AWS.')
parser.add_argument('--access-key-id', required=True, help='AWS Access Key ID', dest='access_key_id')
parser.add_argument('--secret-access-key', required=True, help='AWS Secret Access Key', dest='secret_access_key')
parser.add_argument('--instance-name', required=False, default='pentaho_cloud', help='AWS Secret Access Key', dest='instance_name')
parser.add_argument('--instance-count', required=False, default=1, help='Number of instances to launch', dest='instance_count')
parser.add_argument('--instance-type', required=False, default='m1.small', help='Instance type', dest='instance_type')
parser.add_argument('--availability-zone', required=False, help='Availability Zone in which to run the instance', dest='availability_zone')
parser.add_argument('--image-id', required=False, default='ami-e358958a', help='AMI ID')
parser.add_argument('--ssl', required=False, default=False, action='store_const', const=True, help='Enable SSL (self-signed)')
parser.add_argument('--generate-passwords', required=False, default=False, action='store_const', const=True, help='True to generate passwords (unique per server)', dest='generate_passwords')
parser.add_argument('--version', required=True, help='Pentaho suite version (e.g. "4.0.0-GA")')
parser.add_argument('--license-dir', required=True, help='Directory containing lic files', dest='license_dir')

args = parser.parse_args()

passwords = []
for i in range(20): # amazon only allows 20 instances per reservation by default
  if (args.generate_passwords):
    passwords.append(pentaho_cloud.mk_passwd())
  else:
    passwords.append('password')

res_dir = sys.path[0] + '/res'

aws_instances = pentaho_cloud.aws.connect.run_instances(AwsProviderConfig(args.access_key_id, args.secret_access_key, instance_count=args.instance_count, instance_name=args.instance_name, instance_type=args.instance_type, placement=args.availability_zone, image_id=args.image_id), PentahoServerConfig(args.version, args.license_dir, res_dir, args.ssl, passwords))

print '#'.rjust(2), 'instance_id'.ljust(12), 'public_dns_name'.ljust(50), 'password'.ljust(8)
print '--'.rjust(2), '------------'.ljust(12), '--------------------------------------------------'.ljust(50), '--------'.ljust(8)
for idx, instance in enumerate(aws_instances):
  print str(instance.index).rjust(2), str(instance.instance_id).ljust(12), str(instance.public_dns_name).ljust(50), str(passwords[idx].ljust(8))
    
print '\nSSH using private key %s and user "ubuntu"' % os.path.expanduser('~/.pentaho_cloud/pentaho_cloud.pem')
print '\nTo do:'
print '  Record this information!'
print "  Delete volumes after instance termination!"




