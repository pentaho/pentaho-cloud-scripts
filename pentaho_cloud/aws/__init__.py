import os
import shutil
import pentaho_cloud
import time

def mk_userdata_file(out_file, server_cfg):
  work_dir=pentaho_cloud.mk_work_dir()
  userdata=pentaho_cloud.mk_multipart(prep_files(work_dir, server_cfg))
  f = open(out_file, 'wb')
  f.write(userdata)
  f.close
  pentaho_cloud.rm_work_dir(work_dir)

def prep_files(work_dir, server_cfg):
  vars_path=pentaho_cloud.mk_vars_file(work_dir, server_cfg, 'amazon')
  shutil.copyfile(server_cfg.res_dir + '/pentaho-init', work_dir + '/pentaho-init')
  shutil.copyfile(server_cfg.res_dir + '/util.py', work_dir + '/util.py')
  shutil.copyfile(server_cfg.res_dir + '/octet-stream-handler.py', work_dir + '/octet-stream-handler.py')
  license_tarball_path=pentaho_cloud.mk_license_tarball(work_dir, server_cfg.license_dir)
  # use '|' symbols since Windows paths will contain ':' symbols
  return [vars_path + '|text/x-shellscript', work_dir + '/pentaho-init|text/x-shellscript', work_dir + '/util.py|text/x-shellscript', work_dir + '/octet-stream-handler.py|text/part-handler', license_tarball_path+'|application/octet-stream']


