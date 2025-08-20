#!/usr/bin/env bash

hive -f task3.hdl > /dev/null

hive -e 'SELECT te3.inn, te3.cday, te3.sm FROM (SELECT te2.inn as inn, te2.cday as cday, te2.sm as sm, ROW_NUMBER() OVER (PARTITION BY te2.inn ORDER BY te2.sm DESC) as rn FROM (SELECT tet.inn as inn, tet.cday as cday, SUM(tet.sm) as sm FROM (SELECT FROM_UNIXTIME(content.dateTime["$date"] DIV 1000, "dd") as cday, coalesce(content.totalSum, 0) as sm, content.userInn as inn FROM mixaisealx.kktrans_orc WHERE content.userInn IS NOT NULL) as tet GROUP BY tet.cday,tet.inn) as te2) as te3 WHERE te3.rn=1'

