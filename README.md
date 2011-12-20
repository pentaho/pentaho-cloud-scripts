Installation
==============

Windows
-------

* Download Python 2.7.2 (http://www.python.org/getit/windows/) and run the installer
* Add folder with python.exe to PATH
* (Optional) If launching instances with pentaho_cloud, you need to install the boto library
    * Download boto 2.0 (http://code.google.com/p/boto/downloads/list)
    * Unzip the boto archive
    * Run: python setup.py install

Linux (Debian)
--------------

* Run: sudo apt-get install python
* (Optional) If launching instances with pentaho_cloud, you need to install the boto library
    * Run: sudo apt-get install python-pip
    * Run: sudo pip install -U boto
