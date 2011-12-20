# Pentaho Cloud Scripts

## Disclaimer

These scripts and instructions are a starting point. They were originally written for launching Pentaho Enterprise Edition (EE) suite. They will not work out-of-the-box for Community Edition (CE). (For example, they require a directory containing the EE licenses.) In addition, the scripts depend on Pentaho Debian packages which are not publicly available. However, the Debian package Ant code is available in the trunk and you can use it to create your own packages. (See the package-deb target.) Finally, the location (pkg_url) where the Pentaho Debian packages are to be fetched must be changed in res/pentaho-init.

## Introduction

The technique used by these scripts for launching Pentaho on IaaS providers (e.g. Amazon aka AWS) is to use vanilla Ubuntu (tested with 11.04) along with the [cloud-init](https://help.ubuntu.com/community/CloudInit) package. Using this technique, all required software (e.g. Java, MySQL) is installed on first launch. As a consequence of this approach, first launch can take 10 minutes or more.

## Installing

### Windows

* Download Python 2.7.2 (http://www.python.org/getit/windows/) and run the installer
* Add folder with python.exe to PATH
* (Optional, AWS only) If launching instances on AWS, you need to install the boto library
    * Download boto 2.0 (http://code.google.com/p/boto/downloads/list)
    * Unzip the boto archive
    * Run: python setup.py install

### Linux (Debian-based)

* Run: sudo apt-get install python
* (Optional, AWS only) If launching instances on AWS, you need to install the boto library
    * Run: sudo apt-get install python-pip
    * Run: sudo pip install -U boto

## Using

### Amazon EC2

Please see the Disclaimer first! There are two ways to use these scripts to run Pentaho on EC2.

#### Supported AMIs

The methods described in this document have been tested with Ubuntu 11.04. To find a list of Ubuntu 11.04 AMIs, following these instructions.

1. Go to http://cloud.ubuntu.com/ami/.
1. Filter using the following: `Name`=`natty`, `EBS`=`ebs`.

#### Automated

1. Run `run_ec2.py`. Use `--help` for usage.

#### Manual

##### One-time Preparation

1. Login to [AWS Management Console](http://aws.amazon.com/console/) and click the `EC2` tab.
1. Create a key pair. A key pair will allow you to SSH into your instances.
    1. Click `Key Pairs` under `Networking & Security`.
    1. Click `Create Key Pair`.
    1. Enter a `Key Pair Name` and click `Create`.
    1. Save the downloaded `pem` file. This will be used every time you SSH.
    1. Click `Close`.
1. Create a security group. A security group will only allow certain traffic to your instances.
    1. Click `Security Groups` under `Networking & Security`.
    1. Click the checkbox for the `default` security group.
    1. Click the `Inbound` tab.
    1. For each of the following pairs, enter the `Port range` and `Source` then click `Add Rule`: (18080, 0.0.0.0/0), (19080, 0.0.0.0/0), (18088, 0.0.0.0/0), (18443, 0.0.0.0/0), (19443, 0.0.0.0/0).

##### Launching

1. Create the user data.

1. Run `mk_ec2_userdata.py`. Use `--help` for usage.
1. Login to [AWS Management Console](http://aws.amazon.com/console/) and click the `EC2` tab. Now click `Launch Instance`.
1. Click `Community AMIs`. Enter one of the supported AMIs from above into the filter text box. Hit Enter. Click `Select` on the desired image.
1. Enter `Number of Instances` and `Instance Type` (tested with `m1.large`).  Click `Continue`.
1. For `User Data`, click `as file`.  Browse for the file created earlier. Do not check `base64 encoded`. Enable `Termination Protection` if desired. `Shutdown Behavior` should be set to `Stop`.  Click `Continue`.
1. You can specify any number of tags. The `Name` tag is very useful when showing instances in the console. Click `Continue`.
1. Choose the key pair created earlier. Click `Continue`.
1. Choose the security group created earlier. Click `Continue`.
1. Confirm the settings and click `Launch`.

### Rackspace

Please see the Disclaimer first!

#### One-time Preparation

This technique is based on [Bootstrapping an Ubuntu Server on Rackspace Using Cloud-Init](http://olex.openlogic.com/wazi/2011/bootstrapping-an-ubuntu-server-on-rackspace-using-cloud-init-and-fog/).

In the examples below, [json.tool](http://docs.python.org/library/json.html) is used to pretty-print the JSON responses. Piping to it is optional.

1. Get an auth token.

    curl -s -D - -H "X-Auth-Key: @authKey@" -H "X-Auth-User: @authUser@" https://auth.api.rackspacecloud.com/v1.0
1. Export `X-Auth-Token` and `X-Server-Management-Url` values from the response.

    export X_AUTH_TOKEN="@authToken@"
    export X_MGMT_URL="@mgmtUrl@"
    
1. List the flavors. Choose a flavor (tested with 2GB of RAM). Note the flavor ID.

    curl -s -H "X-Auth-Token: $X_AUTH_TOKEN" $X_MGMT_URL/flavors/detail | python -mjson.tool

1. List the images. Choose an Ubuntu image (tested with 11.04). Note the image ID.

    curl -s -H "X-Auth-Token: $X_AUTH_TOKEN" $X_MGMT_URL/images | python -mjson.tool

1. Start an instance. Note the server ID, public IP address, and admin password.

    curl -s -H "X-Auth-Token: $X_AUTH_TOKEN" -H "Content-Type: application/json" -X POST -d '{"server":{"name":"pentaho","imageId":@imageId@,"flavorId":@flavorId@}}' $X_MGMT_URL/servers | python -mjson.tool

1. Check that the server status is `ACTIVE`.

    curl -s -H "X-Auth-Token: $X_AUTH_TOKEN" $X_MGMT_URL/servers/@serverId@ | python -mjson.tool

1. SSH into instance.

    ssh root@@serverIp@

1. Install cloud-init on the instance.
    
    apt-get install cloud-init

1. Create an image of running instance.

    curl -s -H "X-Auth-Token: $X_AUTH_TOKEN" -H "Content-Type: application/json" -X POST -d '{"image":{"serverId":@serverId@,"name":"pentaho"}}' $X_MGMT_URL/images | python -mjson.tool

1. Check that the image status is `ACTIVE`.

    curl -s -H "X-Auth-Token: $X_AUTH_TOKEN" $X_MGMT_URL/images/@imageId@ | python -mjson.tool

1. Delete server.

    curl -s -H "X-Auth-Token: $X_AUTH_TOKEN" -X DELETE $X_MGMT_URL/servers/@serverId@

#### Running

1. Run `mk_rs_request.py`. Use `--help` for usage. Assume the output of that command goes to `request.xml`.
1. Launch the server.

    curl -s -H "X-Auth-Token: $X_AUTH_TOKEN" -H "Content-Type: application/xml" -X POST -d @request.xml $X_MGMT_URL/servers | python -mjson.tool
