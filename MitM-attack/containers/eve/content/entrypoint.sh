#!/bin/env bash
sleep 1

tcpdump -i eth0 -U -w /data/eve.pcap &
sleep 4

python3 ./attack.py
