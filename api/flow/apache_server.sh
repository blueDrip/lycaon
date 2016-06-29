#!/bin/sh
#/home/sw/apache/bin/apachectl -k start
ps -x |grep apache | grep -v grep
if [ $? -ne 0 ]; then
    /home/sw/apache/bin/apachectl -k start
fi
/home/sw/apache/bin/apachectl -k restart
echo 'sss'
