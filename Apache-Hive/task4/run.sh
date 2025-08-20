#!/usr/bin/env bash

hive -f task4.hdl > /dev/null

hive -e 'SELECT inn, ROUND(amavg) as amrd, ROUND(pmavg) as pmrd FROM (SELECT inn, AVG(amam) as amavg, AVG(ampm) as pmavg FROM (SELECT inn, IF(time < "13:00:00", amnt, NULL) as amam, IF(time < "13:00:00", NULL, amnt) as ampm FROM (SELECT coalesce(content.totalSum, 0) as amnt, content.userInn as inn, FROM_UNIXTIME(content.dateTime["$date"] DIV 1000, "HH:mm:ss") as time FROM mixaisealx.kktrans_orc WHERE content.userInn IS NOT NULL) as mp1) as mp2 GROUP BY inn HAVING amavg > pmavg ORDER BY amavg) as rd1 LIMIT 50'

