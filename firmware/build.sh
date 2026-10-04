#!/bin/bash

CURRDIR=`pwd`

rm -rf /tmp/staging
rm -rf *.xo
mkdir /tmp/staging

cp -Lr ButiaFirmware.activity -t /tmp/staging

cd /tmp/staging/ButiaFirmware.activity
rm -rf locale
git init
git add *
git commit -m 'all files'
python3 setup.py build
python3 setup.py dist_xo

cd $CURRDIR
mv /tmp/staging/ButiaFirmware.activity/dist/*.xo .

