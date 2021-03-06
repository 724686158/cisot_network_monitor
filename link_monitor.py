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
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import in_proto
from ryu.lib.packet import ethernet
from ryu.lib import hub
from ryu.topology import event
from ryu.topology.api import get_link

import copy
import time

from lib.topology import Topology
from lib.measurement_repositories import LinkLatencyRepository
from lib.packets import TestPacket, ReceivedTestPacket


class LinkMonitor(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    SRC_MAC = '00:00:00:00:00:00'
    DST_MAC = 'ff:ff:ff:ff:ff:ff'
    ETH_TYPE = 0x0815

    def __init__(self, *args, **kwargs):
        super(LinkMonitor, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.link_latency_repository = LinkLatencyRepository()
        self.topology = Topology()
        self.monitor_thread = hub.spawn(self._monitor)

    def _monitor(self):
        while True:
            time.sleep(5)
            for dp in self.datapaths.values():
                for port in self.topology.get_ports(dp.id):
                    self.send_test_packet(dp, TestPacket(port), port)
            self.logger.debug(self.link_latency_repository)

    def send_test_packet(self, datapath, packet_payload, out_port):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        pkt = packet.Packet()
        pkt.add_protocol(
            ethernet.ethernet(src=self.SRC_MAC,
                              dst=self.DST_MAC,
                              ethertype=self.ETH_TYPE))
        pkt.add_protocol(str(packet_payload).encode())
        pkt.serialize()

        actions = [parser.OFPActionOutput(out_port)]
        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER,
                                  actions=actions,
                                  data=pkt.data)
        self.logger.debug('sending msg %s to  %016x; out_port %d',
                          packet_payload, datapath.id, out_port)
        datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        dst = eth_pkt.dst
        src = eth_pkt.src
        self.logger.debug("packet in from %016x; src=%s dst=%s", datapath.id,
                          src, dst)
        if src == self.SRC_MAC and dst == self.DST_MAC:
            payload = pkt.protocols[-1]
            self.logger.debug("test packet received")
            payload_string = payload.decode()
            self.logger.debug("payload: %s", payload_string)
            pkt = TestPacket.from_string(payload_string)
            dst_dpid = datapath.id
            src_dpid = self.topology.get_opposite_dpid(dst_dpid, pkt._src_port)
            rpkt = ReceivedTestPacket(src_dpid, dst_dpid, pkt._send_ts)
            self.link_latency_repository.parse_test_packet(rpkt)

    @set_ev_cls(event.EventSwitchEnter)
    def handler_switch_enter(self, ev):
        for link in copy.copy(get_link(self)):
            self.topology.register_link(link.src.dpid, link.src.port_no,
                                        link.dst.dpid, link.dst.port_no)

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
        self.datapaths[datapath.id] = datapath

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
