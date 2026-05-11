from scapy.all import sniff, IP, TCP, UDP
import threading
import time

class PacketSniffer:
    def __init__(self, max_packets=100):
        self.sniffing = False
        self.packets = []
        self.max_packets = max_packets

    def _basic_feature_dict(self, packet):
        protocol_type = "other"
        service = "other"
        flag = "SF"
        src_bytes = 0
        dst_bytes = 0

        if IP in packet:
            if TCP in packet:
                protocol_type = "tcp"
                service = "http"
                flag = "SF"
                src_bytes = int(packet[TCP].len or 0)
            elif UDP in packet:
                protocol_type = "udp"
                service = "domain"
                flag = "SF"
                src_bytes = int(packet[UDP].len or 0)
            else:
                protocol_type = "icmp"

        return {
            "duration": 0,
            "protocol_type": protocol_type,
            "service": service,
            "flag": flag,
            "src_bytes": src_bytes,
            "dst_bytes": dst_bytes,
            "land": 0,
            "wrong_fragment": 0,
            "urgent": 0,
            "hot": 0,
            "num_failed_logins": 0,
            "logged_in": 0,
            "num_compromised": 0,
            "root_shell": 0,
            "su_attempted": 0,
            "num_root": 0,
            "num_file_creations": 0,
            "num_shells": 0,
            "num_access_files": 0,
            "num_outbound_cmds": 0,
            "is_host_login": 0,
            "is_guest_login": 0,
            "count": 1,
            "srv_count": 1,
            "serror_rate": 0,
            "srv_serror_rate": 0,
            "rerror_rate": 0,
            "srv_rerror_rate": 0,
            "same_srv_rate": 0,
            "diff_srv_rate": 0,
            "srv_diff_host_rate": 0,
            "dst_host_count": 1,
            "dst_host_srv_count": 1,
            "dst_host_same_srv_rate": 0,
            "dst_host_diff_srv_rate": 0,
            "dst_host_same_src_port_rate": 0,
            "dst_host_srv_diff_host_rate": 0,
            "dst_host_serror_rate": 0,
            "dst_host_srv_serror_rate": 0,
            "dst_host_rerror_rate": 0,
            "dst_host_srv_rerror_rate": 0,
        }

    def process_packet(self, packet):
        if IP in packet:
            info = {
                "src": packet[IP].src,
                "dst": packet[IP].dst,
                "proto": packet[IP].proto,
                "timestamp": time.time(),
                "features": self._basic_feature_dict(packet),
            }
            self.packets.append(info)
            if len(self.packets) > self.max_packets:
                self.packets = self.packets[-self.max_packets :]

    def start(self):
        self.sniffing = True
        self.thread = threading.Thread(target=self._sniff, daemon=True)
        self.thread.start()

    def _sniff(self):
        sniff(prn=self.process_packet, store=False, stop_filter=lambda x: not self.sniffing)

    def stop(self):
        self.sniffing = False

    def latest_packets(self):
        return list(self.packets)
