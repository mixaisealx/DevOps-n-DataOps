#!/bin/bash

bin/kafka-console-consumer.sh  --from-beginning  --bootstrap-server localhost:9092  --property print.key=true --property print.value=false --property print.partition  --topic $1 --timeout-ms 1000 | tail -n 10 | grep "Processed a total of"
