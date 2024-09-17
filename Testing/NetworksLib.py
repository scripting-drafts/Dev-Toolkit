import os
from QALogger import Logger
from subprocess import getoutput
import pyshark
from scapy.all import *
from tqdm import tqdm


class NetworksLib:
    def __init__(self):
        self.logger = Logger().logging()
        
    def getLayer(self, p):
        for paktype in (IP, TCP, UDP, ICMP):
            try:
                p.getlayer(paktype).chksum = None
            except AttributeError:
                pass
        return p

    def fixpcap(self, input_file, output_file):
        paks = rdpcap(input_file)
        fc = map(self.getLayer, paks)
        wrpcap(output_file, fc)
        return output_file

    def check_traces_integrity(self, capture_file):
        if not "repaired_" in str(capture_file):
            repaired_capture_file = "repaired_" + str(capture_file)
            repaired_capture_file = self.fixpcap(capture_file, repaired_capture_file)
            return repaired_capture_file
        else:
            return capture_file

    def get_bitrate(self, capture_file):
        # ptime: 20ms, packets/s: 50, PTT bitrate: # REDACTED
        # ptime: 40ms, packets/s: 25, PTT bitrate: # REDACTED
        # REDACTED
        count = 0
        length = 0
        lengths = []
        counts = []

        split = capture_file.split("/")
        capture_file = self.check_traces_integrity(capture_file)

        rtp_cap = pyshark.FileCapture(capture_file, display_filter='rtp')
        for rtp_packet in tqdm(rtp_cap):
            if rtp_packet.rtp.p_type == "# REDACTED":
                if count == 0:
                    firstTime = float(str(rtp_packet.sniff_time)[-9:-1])
                    self.logger.debug(rtp_packet.sniff_time)

            # or rtp_packet.rtp.ssrc != firstSSRC:
                if float(str(rtp_packet.sniff_time)[-9:-1]) >= firstTime + 1.:
                    lengths.append(length)
                    counts.append(count)
                    length = 0
                    count = 0
                else:
                    count += 1
                    length += int(rtp_packet.length)

        self.logger.debug(lengths)

        rtp_cap.close()

        for l in lengths:
            # data-link layer is 16bytes
            lengths[lengths.index(l)] = l - counts[lengths.index(l)] * 16

        bits_lengths = []

        for l in lengths:
            bits_lengths.append(l*8)

        # logger.debug(ssrcs)
        # self.logger.debug(split[1])
        self.logger.debug("Packets/s: {}".format(counts))
        self.logger.debug("Byte lengths: {}".format(lengths))
        self.logger.debug("Bit lengths: {}".format(bits_lengths))

        count = 0
        suma = 0

        for l in bits_lengths:
            count += 1
            suma += l

        mitja = suma / count
        kbits = mitja / 1000
        self.logger.debug("Bitrate: {} Kbits/s".format(str(kbits)))
        
        return "Bitrate: {} Kbits/s".format(str(kbits))

    def packets_order_check(self, capture_file):
        ports, repeatedExists, prev_seq, isOutOfOrder, newOrderStarter, analyzedPackets, affectedRanges = [], False, None, False, False, [], []

        repaired_capture_file = self.check_traces_integrity(capture_file)
        cap = pyshark.FileCapture(repaired_capture_file, display_filter='udp')
        self.logger.debug(" > {}".format(repaired_capture_file))

        self.logger.debug("Reading ports")
        ports = [p[p.transport_layer].dstport for p in cap if type(p.transport_layer) != None and p[p.transport_layer].dstport != "53"]
        # ports = [p[p.transport_layer].dstport for p in ports if p[p.transport_layer].dstport != "53"]
        # print(ports)
        if repeatedExists == False:
            for x in range(len(ports)):
                if ports.count(ports[x]) > 1:
                    repeatedExists = True

        if repeatedExists:
            ports = set(ports)

        cap.close()

        self.logger.debug("Analyzing traces...")
        for port in ports:
            rtp_cap = pyshark.FileCapture(repaired_capture_file, display_filter='rtp', decode_as={'udp.port==' + port: 'rtp'})
            # rtp_cap.set_debug()
            for rtp_packet in rtp_cap:
                length = rtp_packet.length
                try:
                    if rtp_packet.rtp.p_type == "# REDACTED":
                        seq = int(rtp_packet.rtp.seq)
                        ssrc = rtp_packet.rtp.ssrc

                        if prev_seq == None:
                            prev_seq = seq
                            prev_ssrc = ssrc

                        elif seq < prev_seq and ssrc == prev_ssrc:
                            isOutOfOrder = True

                            if analyzedPackets[-1][-2] == False:
                                newOrderStarter = True

                        elif seq == prev_seq + 1:
                            prev_seq = seq
                            prev_ssrc = ssrc

                        elif seq != prev_seq + 1 and seq > prev_seq:
                            prev_seq = seq
                            prev_ssrc = ssrc
                            self.logger.debug("Packet loss detected after packet no. {}".format(rtp_packet.number))

                            if isOutOfOrder == True:
                                isOutOfOrder = False

                        # logger.debug(rtp_packet.number, "Packets dropped")

                        elif prev_seq == 65535 and seq == 0:
                            prev_seq = seq
                            prev_ssrc = ssrc
                        # logger.debug(rtp_packet.number, "seq_num turnover")

                        analyzedPackets.append(
                            [rtp_packet.number, seq, isOutOfOrder, newOrderStarter])
                        isOutOfOrder = False
                        newOrderStarter = False

                except AttributeError:
                    pass
            rtp_cap.close()
            prev_seq = None
        # cap.close()

        if analyzedPackets:
            for packet in analyzedPackets:
                if packet[-1] == True:
                    starter = packet
                elif packet[-1] != True and packet[-2] == True:
                    affected = packet
                elif packet[0] != analyzedPackets[0][0] and packet[-2] == False and analyzedPackets[analyzedPackets.index(packet) - 1][-2] == True:
                    last = analyzedPackets[analyzedPackets.index(packet) - 1]
                    affectedRanges.append([starter, last])
        
            for x in affectedRanges:
                if affectedRanges.count(x) > 1:
                    affectedRanges.remove(x)

            if affectedRanges:
                self.logger.debug("The following ranges are out of order:")
                for affectedRange in sorted(affectedRanges, key=lambda x: x[0], reverse=True):
                    self.logger.debug("frame {} - {} {} | seq_num - {} {}".format(
                        affectedRange[0][0], affectedRange[1][0], affectedRange[0][1], affectedRange[1][1]))
            else:
                self.logger.debug("No out-of-order packets found")
        else:
            self.logger.debug("Ports not properly filtered - No results")

    def find_packet_loss(self, capturefile):
        capture_file = self.check_traces_integrity(capturefile)
        seq_nums = getoutput("tshark -r {} -d udp.port==0:99999,rtp -R 'rtp.p_type==# REDACTED' -2 | cut -d ' ' -f12 | cut -d '=' -f2 |  cut -d ',' -f1".format(capture_file))
        pattern = "\d{5}"
        mxs = re.search(pattern, seq_nums)
        seq_nums = seq_nums[mxs.start():]
        seq_nums = seq_nums.split("\n")

        for seq_num in seq_nums:
            if seq_nums.index(seq_num) != 0:
                
                if seq_num != "65535" and seq_nums.index(seq_num) != seq_nums.index(seq_nums[-1]):
                    if int(seq_nums[seq_nums.index(seq_num) + 1]) != int(seq_num) + 1:
                        seq_before_loss = int(seq_num)
                
                if seq_num != "0" and seq_nums.index(seq_num) != seq_nums.index(seq_nums[0]):
                    if int(seq_nums[seq_nums.index(seq_num) - 1]) != int(seq_num) - 1:
                        seq_after_loss = int(seq_num)

        if 'seq_before_loss' in locals():
            if 'seq_after_loss' in locals():
                raise AssertionError("Last packet loss detected starts at {} and ends at {}".format(seq_before_loss, seq_after_loss))
            else:
                raise AssertionError("Last packet loss detected starts at {}".format(seq_before_loss))
