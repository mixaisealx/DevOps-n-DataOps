#!/usr/bin/env bash

hive -f task1.hdl &> /dev/null

hive -e 'select * from kktrans limit 50' 2> /dev/null

