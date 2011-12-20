import boto
import boto.ec2.blockdevicemapping
import time
import os
import pentaho_cloud
import pentaho_cloud.aws
from pentaho_cloud import PentahoServerConfig

def run_instances(provider_cfg, server_cfg):
  work_dir=pentaho_cloud.mk_work_dir()
  #print 'work_dir=%s' % work_dir
  userdata=pentaho_cloud.mk_multipart(pentaho_cloud.aws.prep_files(work_dir, server_cfg))
  ec2 = boto.connect_ec2(provider_cfg.access_key_id, provider_cfg.secret_access_key)
  
  # create key pair if necessary
  if len(ec2.get_all_key_pairs(filters={'key-name' : 'pentaho_cloud'})) == 0:
    key_pair = ec2.create_key_pair('pentaho_cloud')  # only needs to be done once
    kdir = os.path.expanduser('~/.pentaho_cloud')
    if not os.path.exists(kdir):
      os.mkdir(kdir)
    key_pair.save(os.path.expanduser(kdir))
    
  # create security group if necessary
  if len(ec2.get_all_security_groups(filters={'group-name' : 'pentaho_cloud'})) == 0:
    ec2.create_security_group('pentaho_cloud', 'Security group created by pentaho_cloud')
    ports = [22, 18080, 18088, 18143, 18443, 19080, 19443]
    for p in ports:
      ec2.authorize_security_group(group_name='pentaho_cloud', ip_protocol='tcp', from_port=p, to_port=p, cidr_ip='0.0.0.0/0')
  
  # get block device mapping associated with image
  images = ec2.get_all_images([provider_cfg.image_id])
  if len(images) != 1:
    raise Exception('Exactly one result not returned for image id %' % provider_cfg.image_id)
  
  image = images[0]
  
  run_args = {}
  run_args['min_count'] = provider_cfg.instance_count
  run_args['max_count'] = provider_cfg.instance_count
  run_args['image_id'] = provider_cfg.image_id
  run_args['key_name'] ='pentaho_cloud'
  run_args['security_groups'] = ['pentaho_cloud']
  run_args['instance_type'] = provider_cfg.instance_type
  run_args['user_data'] = userdata
  run_args['instance_initiated_shutdown_behavior'] = 'stop'
  run_args['disable_api_termination'] = True
  if provider_cfg.placement:
    run_args['placement'] = provider_cfg.placement
  # override the block device mapping
  block_dev_map = boto.ec2.blockdevicemapping.BlockDeviceMapping()
  block_dev = boto.ec2.blockdevicemapping.EBSBlockDeviceType()
  block_dev.size = '20' # GiB
  block_dev.snapshot_id = image.block_device_mapping[image.root_device_name].snapshot_id
  block_dev.delete_on_termination = False
  block_dev_map[image.root_device_name] = block_dev
  run_args['block_device_map'] = block_dev_map
  
  reservation = ec2.run_instances(**run_args)
  
  print 'Waiting on instance(s) to get public DNS name(s)...'
  
  block_until_ready(ec2, reservation.id)
  
  short_names = False
  if len(get_instances(ec2, reservation.id)) == 1:
    short_names = True
  
  instance_name = provider_cfg.instance_name
  if not instance_name:
    instance_name = 'pentaho_cloud'
  
  aws_instances = []
  for i in get_instances(ec2, reservation.id):
    instance_tags = {}
    if (short_names):
      instance_tags['Name'] = instance_name
    else:
      instance_tags['Name'] = instance_name + '_' + str(i.ami_launch_index)
    instance_tags['Created by pentaho_cloud'] = ''
    ec2.create_tags([i.id], instance_tags)
    
    volume_tags = {}
    volume_tags['Created by pentaho_cloud'] = ''
    if (short_names):
      volume_tags['Name'] = instance_name + '_volume'
    else:
      volume_tags['Name'] = instance_name + '_' + str(i.ami_launch_index) + '_volume'
    ec2.create_tags([i.block_device_mapping[i.root_device_name].volume_id], volume_tags)

    aws_instances.append(AwsInstance(i.ami_launch_index, i.id, i.public_dns_name))
    
  pentaho_cloud.rm_work_dir(work_dir)
  return aws_instances

def block_until_ready(ec2, reservation_id):
  #print 'resid: %s' % reservation_id
  while True:
    ready = True
    for i in get_instances(ec2, reservation_id):
      if (not i.public_dns_name):
        ready = False
        break
    if not ready:
      time.sleep(5)
    else:
      break
  
def get_instances(ec2, reservation_id):
  attempts = 0
  while (attempts < 10):
    # tried get_all_instances with filter by reservation-id with mixed results
    for r in ec2.get_all_instances():
      if (r.id == reservation_id):
        return r.instances
    time.sleep(5)
    attempts += 1
  raise Exception('never got reservation')

class AwsProviderConfig:
  server_name = None
  image_id = 'ami-e358958a' # 'ami-e358958a' is Ubuntu 11.04 i386
  instance_type = 'm1.small'
  access_key_id = None
  secret_access_key = None
  placement = None
  server_count = 1
  
  def __init__(self, access_key_id, secret_access_key, instance_name=None, image_id='ami-e358958a', instance_type='m1.small', placement=None, instance_count=1):
    self.access_key_id = access_key_id
    self.secret_access_key = secret_access_key
    self.instance_name = instance_name
    self.image_id = image_id
    self.instance_type = instance_type
    self.placement = placement
    self.instance_count = instance_count
    
class AwsInstance:
  index = 0
  instance_id = None
  public_dns_name = None
  
  def __init__(self, index, instance_id, public_dns_name):
    self.index = index
    self.instance_id = instance_id
    self.public_dns_name = public_dns_name