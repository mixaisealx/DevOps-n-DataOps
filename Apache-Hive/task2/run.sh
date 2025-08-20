#!/usr/bin/env bash

hive -f task2.hdl > /dev/null

hive -e 'SELECT content.userInn as inn, SUM(content.totalSum) as sm FROM mixaisealx.kktrans_orc WHERE subtype="receipt" GROUP BY content.userInn ORDER BY sm DESC LIMIT 1'

