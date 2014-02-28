#!/bin/sh

OUT=`date`
ssh -X root@192.168.1.231 date --set=\"$OUT\"
