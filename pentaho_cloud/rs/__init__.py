import pentaho_cloud
from pentaho_cloud import PentahoServerConfig
import shutil
import base64

request_template = """<?xml version="1.0" encoding="UTF-8"?>
<server xmlns="http://docs.rackspacecloud.com/servers/api/v1.0" name="{instancename}" imageId="{imageid}" flavorId="{flavorid}">  
  <personality>
    <file path="/var/lib/cloud/seed/nocloud-net/user-data">
{base64userdata}
    </file>
    <file path="/var/lib/cloud/seed/nocloud-net/meta-data">
{base64metadata}
    </file>
    <file path="/opt/pentaho/pentaho-licenses.tar.gz">
{base64licenses}
    </file>
  </personality>
</server>"""

def mk_request_file(out_file, instance_name, image_id, flavor_id, server_cfg):
  work_dir=pentaho_cloud.mk_work_dir()
  userdata=pentaho_cloud.mk_multipart(prep_multipart_files(work_dir, server_cfg))
  license_tarball_path=pentaho_cloud.mk_license_tarball(work_dir, server_cfg.license_dir)
  f = open(license_tarball_path, 'rb')
  licenses = f.read()
  f.close()
  pentaho_cloud.rm_work_dir(work_dir)
  f = open(out_file, 'wb')
  f.write(request_template.format(base64userdata=base64.b64encode(userdata), base64metadata=base64.b64encode(' '), base64licenses=base64.b64encode(licenses), imageid=image_id, flavorid=flavor_id, instancename=instance_name))
  f.close()

def prep_multipart_files(work_dir, server_cfg):
  vars_path=pentaho_cloud.mk_vars_file(work_dir, server_cfg, 'rackspace')
  shutil.copyfile(server_cfg.res_dir + '/pentaho-init', work_dir + '/pentaho-init')
  shutil.copyfile(server_cfg.res_dir + '/util.py', work_dir + '/util.py')
  shutil.copyfile(server_cfg.res_dir + '/octet-stream-handler.py', work_dir + '/octet-stream-handler.py')
  key_helper_jar=pentaho_cloud.mk_key_helper_jar(work_dir, server_cfg.res_dir)
  # use '|' symbols since Windows paths will contain ':' symbols
  return [vars_path + '|text/x-shellscript', work_dir + '/pentaho-init|text/x-shellscript', work_dir + '/util.py|text/x-shellscript', work_dir + '/octet-stream-handler.py|text/part-handler', key_helper_jar + '|application/octet-stream']