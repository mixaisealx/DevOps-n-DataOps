#!/usr/bin/env bash

hive -f task5.hdl > /dev/null

hive -e 'SELECT inn FROM (SELECT content.userInn as inn, subtype as tp, LEAD(subtype) OVER (PARTITION BY content.userInn ORDER BY content.dateTime["$date"]) as ntp FROM mixaisealx.kktrans_orc WHERE content.userInn IS NOT NULL AND (subtype="receipt" OR subtype="closeShift" OR subtype="openShift")) as wnd WHERE (tp="reciept" AND ntp="openShift") OR (tp="closeShift" AND ntp="receipt") GROUP BY inn LIMIT 50'

