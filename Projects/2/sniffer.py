from pcktparser import *
import os

report_file = open("/home/ali/Desktop/report.txt", "w")
packet_proto = {"ICMP": 0, "TCP": 0, "UDP": 0}
packet_ip = {}
packet_size = []


def get_stats():
    min_size = 0
    max_size = 0
    avg = 0
    count = 0
    for num in packet_size:
        avg += num
        count = count + 1
    max_size = max(packet_size)
    min_size = min(packet_size)
    return min_size, avg/count, max_size



def main():
    conn = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.ntohs(3))

    filters = (["ICMP", 1, "ICMPv6"],["UDP", 17, "UDP"], ["TCP", 6, "TCP"])
    filter = []

    if len(sys.argv) == 2:
        print("This is the filter: ", sys.argv[1])
        for f in filters:
            if sys .argv[1] == f[0]:
                filter = f

    tmp = ''
    proto_pck = ''
    src_pck = ''
    length_pck = 0
    is_fragmented = False
    frag_num = 0

    try:
        while True:
            raw_data, addr = conn.recvfrom(65536)
            dest_mac, src_mac, eth_proto, data = ethernet_frame(raw_data)



            if eth_proto == 'IPV6':
                newPacket, nextProto = ipv6Header(data, filter)
                tmp, proto_pck, src_pck, length_pck = printPacketsV6(filter, nextProto, newPacket)
                
                print("Protocol = {} \nSender IP = {} \nPacket Size = {} \n".format(proto_pck, src_pck, length_pck))
                

                if src_pck in packet_ip:
                    packet_ip[src_pck] += 1
                else:
                    packet_ip[src_pck] = 1

                if proto_pck == 1:
                    packet_proto["ICMP"] += 1
                elif proto_pck == 6:
                    packet_proto["TCP"] += 1
                elif proto_pck == 17:
                    packet_proto["UDP"] += 1

                packet_size.append(length_pck)


            elif eth_proto == 'IPV4':
                proto_pck, src_pck, length_pck, is_fragmented = printPacketsV4(filter, data, raw_data)
                
                print("Protocol = {} \nSender IP = {} \nPacket Size = {} \n".format(proto_pck, src_pck, length_pck))
                
                if src_pck in packet_ip:
                    packet_ip[src_pck] += 1
                else:
                    packet_ip[src_pck] = 1

                if proto_pck == 1:
                    packet_proto["ICMP"] += 1
                elif proto_pck == 6:
                    packet_proto["TCP"] += 1
                elif proto_pck == 17:
                    packet_proto["UDP"] += 1

                packet_size.append(length_pck)

                if is_fragmented:
                    frag_num += 1


    except KeyboardInterrupt:        
        for key, val in packet_proto.items():
            report_file.write(str([key, val]))
        
        
        report_file.write("\n")

        for key, val in packet_ip.items():
            report_file.write(str([key, val]))
        

        report_file.write("\n")
        
        report_file.write("Min, Avg, Max = ")
        report_file.write(str(get_stats()))

        report_file.write("\n")

    
        report_file.write("Number of fragmented packets: ")
        report_file.write(str(frag_num))

        report_file.close()


main()
