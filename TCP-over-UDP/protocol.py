import socket
from collections import deque
from threading import Thread, Lock, Event
from time import sleep


class UDPBasedProtocol:
    def __init__(self, *, local_addr, remote_addr):
        self.udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.remote_addr = remote_addr
        self.udp_socket.bind(local_addr)

    def sendto(self, data):
        return self.udp_socket.sendto(data, self.remote_addr)

    def recvfrom(self, n):
        msg, addr = self.udp_socket.recvfrom(n)
        return msg

    def close(self):
        self.udp_socket.close()


class MyTCPProtocol(UDPBasedProtocol):
    def __thread_sender(self):
        while self.active:
            sleep(0.01)
            with self.mutex:
                if self.sending_data_actual_offset != 0:
                    self.sending_data = self.sending_data[self.sending_data_actual_offset:]
                    self.sending_data_actual_offset = 0

                for offset in range(0, min(len(self.sending_data), self.sender_window_size), self.mtu_payload):
                    chunk = self.sending_data[offset : offset + self.mtu_payload]
                    header = (self.local_sequence_end + offset + len(chunk)).to_bytes(4, 'big')
                    self.sendto(header + chunk)

    def __thread_receiver(self):
        while self.active:
            data = self.recvfrom(1432) # Suppose, actual MTU is 1432
            if len(self.receive_queue) < 256:
                self.receive_queue.append(data)
                self.proc_event.set()

            # Else - drop packet cause can't process so much

    def __thread_receive_processor(self):
        while self.active:
            if len(self.receive_queue) == 0:
                self.proc_event.wait()
                self.proc_event.clear()
                continue
            data = self.receive_queue.popleft()
            seqend = int.from_bytes(data[:4], "big")

            datalen = len(data) - 4
            if datalen > 0: # Received data
                if self.remote_sequence_end >= seqend:
                    self.sendto(self.remote_sequence_end.to_bytes(4, 'big')) # Sending ACK
                    continue
                
                # 4 + 2 + 2 < 8 -> lbound==(end of window_incoming) -> need to add a crossover at least in 1 byte -> -1
                if self.remote_sequence_end + self.receiver_window_size + datalen - 1 < seqend:
                    continue # Drop packet because have no window space for it
                
                # Copying data to window
                lbound = seqend - self.remote_sequence_end - datalen
                rbound = seqend - self.remote_sequence_end

                if rbound <= self.receiver_window_size:
                    startoffset = 0
                    if lbound < 0:
                        startoffset = -lbound
                        lbound = 0
                    self.window_incoming[self.window_incoming_actual_offset + lbound : self.window_incoming_actual_offset + rbound] = data[4+startoffset :]
                else:
                    endlimit = rbound - self.receiver_window_size
                    rbound = self.receiver_window_size
                    self.window_incoming[self.window_incoming_actual_offset + lbound : self.window_incoming_actual_offset + rbound] = data[4 : -endlimit]
                # Setting values to mark ready bytes
                self.window_incoming_map[self.window_incoming_actual_offset + lbound : self.window_incoming_actual_offset + rbound] = b'\x01' * (rbound - lbound)
                
                if lbound > 0:
                    continue # Skip counting cause received packet does not affect starting positions of window

                max_continious_size = 0
                for x in self.window_incoming_map[self.window_incoming_actual_offset:]:
                    if (x == 1):
                        max_continious_size += 1
                    else:
                        break
                
                self.received_data.extend(self.window_incoming[self.window_incoming_actual_offset : self.window_incoming_actual_offset+max_continious_size])
                self.recv_event.set()
                self.window_incoming_actual_offset += max_continious_size
                self.remote_sequence_end += max_continious_size
                self.sendto(self.remote_sequence_end.to_bytes(4, 'big')) # Sending ACK
                
                if self.window_incoming_actual_offset >= self.receiver_window_size:
                    pad = b'\x00' * self.window_incoming_actual_offset
                    self.window_incoming = self.window_incoming[self.window_incoming_actual_offset:] + pad
                    self.window_incoming_map = self.window_incoming_map[self.window_incoming_actual_offset:] + pad
                    self.window_incoming_actual_offset = 0     
            else: # Received ACK
                sent_count = seqend - self.local_sequence_end
                if (sent_count > 0):
                    with self.mutex:
                        self.local_sequence_end = seqend
                        self.sending_data_actual_offset += sent_count

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.active = True
        self.mutex = Lock()
        self.recv_event = Event()
        self.proc_event = Event()

        self.multiplier = 82
        self.mtu_payload = 1428 # 1432 - 4
        self.window_slots = 82

        self.sender_window_size = self.mtu_payload * self.multiplier
        self.receiver_window_size = self.mtu_payload * self.window_slots

        self.local_sequence_end = 0
        self.sending_data = bytearray()
        self.sending_data_actual_offset = 0

        self.receive_queue = deque()
        self.window_incoming_actual_offset = 0
        self.window_incoming = bytearray(self.receiver_window_size * 2)
        self.window_incoming_map = bytearray(self.receiver_window_size * 2)
        self.received_data = bytearray()
        self.remote_sequence_end = 0

        sender = Thread(target = self.__thread_sender)
        receiver = Thread(target = self.__thread_receiver)
        processor = Thread(target = self.__thread_receive_processor)

        sender.daemon = True
        receiver.daemon = True
        processor.daemon = True

        sender.start()
        receiver.start() 
        processor.start()

    def send(self, data: bytes):
        datalen = len(data)
        lseqend = None
        with self.mutex:
            lseqend = self.local_sequence_end + len(self.sending_data) - self.sending_data_actual_offset
            self.sending_data.extend(data)
                
        for offset in range(0, min(datalen, self.sender_window_size), self.mtu_payload):
            chunk = data[offset : offset + self.mtu_payload]
            header = (lseqend + offset + len(chunk)).to_bytes(4, 'big')
            self.sendto(header + chunk)
        
        return datalen

    def recv(self, n: int):
        while len(self.received_data) < n:
            self.recv_event.wait()
            self.recv_event.clear()
        result = bytes(self.received_data[:n])
        self.received_data = self.received_data[n:]
        return result
    
    def close(self):
        self.active = False
        self.proc_event.set()
        super().close()


