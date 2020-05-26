#
# Copyright (c) 2020 by Ilya Tsyganov, Ryazan State Radio Engineering University.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import arp
from ryu.lib.packet import icmp


class IpTableEntry:
    def __init__(self, adjacent_dpid, mac_address, ip_address):
        self.adjacent_dpid = adjacent_dpid
        self.mac_address = mac_address
        self.ip_address = ip_address


class MacDetector(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(MacDetector, self).__init__(*args, **kwargs)
        self.ip_table = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install the table-miss flow entry.
        match = parser.OFPMatch()
        actions = [
            parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                   ofproto.OFPCML_NO_BUFFER)
        ]
        self.add_flow(datapath, 0, match, actions)

        self.logger.debug('datapath %016x registered', datapath.id)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        icmp_pkt = pkt.get_protocol(icmp.icmp)
        arp_pkt = pkt.get_protocol(arp.arp)
        if arp_pkt:
            self._handle_arp(arp_pkt, eth_pkt, datapath, in_port)

    def _handle_arp(self, arp_pkt, eth_pkt, datapath, in_port):
        if arp_pkt.opcode != arp.ARP_REQUEST:
            return

        dst_mac = arp_pkt.dst_mac
        src_mac = arp_pkt.src_mac
        dst_ip = arp_pkt.dst_ip
        src_ip = arp_pkt.src_ip
        self.logger.debug(
            "ARP packet from %016x; src_mac=%s dst_mac=%s, src_ip=%s, dst_ip=%s",
            datapath.id, src_mac, dst_mac, src_ip, dst_ip)

        if arp_pkt.src_ip not in self.ip_table:
            self.ip_table[src_ip] = IpTableEntry(datapath.id, src_mac, src_ip)

        if arp_pkt.dst_ip in self.ip_table:
            host = self.ip_table[arp_pkt.dst_ip]
            self.reply_arp(datapath, in_port, host, arp_pkt, eth_pkt)
            return

    def build_arp_replay_pkt(self, ethertype, src_mac, dst_mac, src_ip,
                             dst_ip):
        pkt = packet.Packet()
        pkt.add_protocol(
            ethernet.ethernet(ethertype=ethertype, dst=dst_mac, src=src_mac))
        pkt.add_protocol(
            arp.arp(opcode=arp.ARP_REPLY,
                    src_mac=src_mac,
                    src_ip=src_ip,
                    dst_mac=dst_mac,
                    dst_ip=dst_ip))
        return pkt

    def reply_arp(self, datapath, in_port, host, arp_pkt, eth_pkt):
        arp_reply_pkt = self.build_arp_replay_pkt(eth_pkt.ethertype,
                                                  host.mac_address,
                                                  arp_pkt.src_mac,
                                                  host.ip_address,
                                                  arp_pkt.src_ip)

        self.send_packet(datapath, in_port, arp_reply_pkt)

    def send_packet(self, datapath, out_port, pkt):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        pkt.serialize()
        data = pkt.data

        actions = [parser.OFPActionOutput(port=out_port)]
        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER,
                                  actions=actions,
                                  data=data)

        datapath.send_msg(out)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [
            parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)
        ]
        mod = parser.OFPFlowMod(datapath=datapath,
                                priority=priority,
                                match=match,
                                instructions=inst)
        datapath.send_msg(mod)