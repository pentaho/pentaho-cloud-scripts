BEFORE THIS WILL WORK, YOU NEED TO PATCH THE RACKSPACE UBUNTU IMAGE TO NOT USE GZIP.  SEE SUPPORT TICKET.  THEN FIX
THIS CODE (MK_MULTIPART) TO USE ZIP OR BZIP2 INSTEAD OF GZIP.

# http://packages.ubuntu.com/oneiric/python/python-openstack-compute

import openstack.compute

def run_instances(license_dir, provider_cfg, instance_cfg):
  work_dir=pentaho_cloud.mk_work_dir()
  #print 'work_dir=%s' % work_dir
  userdata=pentaho_cloud.mk_multipart(prep_files(work_dir, license_dir, instance_cfg))
  base64userdata = base64.b64encode(userdata)
  base64metadata = base64.b64encode(' ')
  license_tarball_path=pentaho_cloud.mk_license_tarball(work_dir, license_dir)
  f = open(license_tarball_path, 'rb')
  license_tarball = f.read()
  base64licenses = base64.b64encode(license_tarball)
  f.close()
  
  rscloud = openstack.compute.Compute(username=provider_cfg.username, apikey=provider_cfg.api_key)
  
  instance_name = instance_cfg.name 
  if not instance_name:
    instance_name = 'pentaho_cloud'
  
  run_args = {}
  run_args['image'] = provider_cfg.image_id
  run_args['flavor'] = provider_cfg.flavor_id
  run_args['name'] = instance_name
  run_args['files'] = {'/var/lib/cloud/seed/nocloud-net/user-data': base64userdata, '/var/lib/cloud/seed/nocloud-net/meta-data': base64metadata, '/opt/pentaho/pentaho-licenses.tar.gz': base64licenses}
  
  server = rscloud.servers.create(**run_args)
  
  print 'instance_id'.ljust(12), 'public_ip'.ljust(50)
  print '------------'.ljust(12), '--------------------------------------------------'.ljust(50)

  print str(server.id).ljust(12), str(server.public_ip()).ljust(50)
    
  print '\nSSH to instance(s) using "ssh ubuntu@public_ip"'
    
  pentaho_cloud.rm_work_dir(work_dir)

class RsProviderCfg:
  image_id = '14108940'
  flavor_id = '4'
  username = None
  api_key = None
  
  def __init__(self, username, api_key, image_id='14108940', flavor_id='4'):
    self.username = username
    self.api_key = api_key
    self.image_id = image_id
    self.flavor_id = flavor_id
