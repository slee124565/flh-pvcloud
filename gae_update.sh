#!/bin/bash -x

version=server

if [ -z $1 ]; then
	version=staging
else
	version=$1
fi

appcfg.py -A solar-cloud-143410 -V $version update . 
