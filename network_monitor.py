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
from ryu.lib import hub
from ryu.controller.handler import set_ev_cls
from ryu.topology import event
from ryu.topology.api import get_link
from ryu.app.wsgi import ControllerBase, WSGIApplication, route, Response

from datapath_monitor import DatapathMonitor
from link_monitor import LinkMonitor

import copy
import json

from lib.topology import LinkRepository, Link
from lib.util import dpid_to_string

network_monitor_instance_name = 'network_monitor'


class NetworkMonitor(app_manager.RyuApp):

    _CONTEXTS = {
        'datapath_monitor': DatapathMonitor,
        'link_monitor': LinkMonitor,
        'wsgi': WSGIApplication
    }

    def __init__(self, *args, **kwargs):
        super(NetworkMonitor, self).__init__(*args, **kwargs)
        wsgi = kwargs['wsgi']
        wsgi.register(NetworkMonitorController,
                      {network_monitor_instance_name: self})
        datapath_monitor = kwargs['datapath_monitor']
        link_monitor = kwargs['link_monitor']
        self.datapath_timing_repository = datapath_monitor.datapath_timing_repository
        self.link_latency_repository = link_monitor.link_latency_repository
        self.bandwidth_port_stats_repository = datapath_monitor.bandwidth_port_stats_repository
        self.plr_port_stats_repository = datapath_monitor.plr_port_stats_repository
        self.link_repository = LinkRepository()

    def create_links_view(self):
        links_view = []
        for link in self.link_repository.find_bidirectional_links():
            links_view.append(
                LinkViewModel(link.src_dpid, link.dst_dpid,
                              self.compute_delay_ms(link),
                              self.compute_bandwidth_bits_per_sec(link),
                              self.compute_plr_percents(link)).__dict__)
        return links_view

    def compute_delay_ms(self, link):
        link_latency_1 = self.link_latency_repository.get_latency_between(
            link.src_dpid, link.dst_dpid).milliseconds()
        link_latency_2 = self.link_latency_repository.get_latency_between(
            link.dst_dpid, link.src_dpid).milliseconds()
        src_datapath_response_time = self.datapath_timing_repository.get_response_time(
            link.src_dpid).milliseconds()
        dst_datapath_response_time = self.datapath_timing_repository.get_response_time(
            link.dst_dpid).milliseconds()
        link_latency = (link_latency_1 + link_latency_2) / 2
        delay = link_latency - src_datapath_response_time / 2 - dst_datapath_response_time / 2
        return delay

    def compute_bandwidth_bits_per_sec(self, link):
        port_bw_1 = self.bandwidth_port_stats_repository.get_stats(
            link.src_dpid, link.src_port_no)
        port_bw_2 = self.bandwidth_port_stats_repository.get_stats(
            link.dst_dpid, link.dst_port_no)
        return (port_bw_1 + port_bw_2) / 2

    def compute_plr_percents(self, link):
        port_plr_1 = self.plr_port_stats_repository.get_stats(
            link.src_dpid, link.src_port_no)
        port_plr_2 = self.plr_port_stats_repository.get_stats(
            link.dst_dpid, link.dst_port_no)
        return (port_plr_1 + port_plr_2) / 2

    @set_ev_cls(event.EventSwitchEnter)
    def handler_switch_enter(self, ev):
        for link in copy.copy(get_link(self)):
            self.link_repository.register_link(link.src.dpid, link.src.port_no,
                                               link.dst.dpid, link.dst.port_no)


class LinkViewModel:
    def __init__(self, src_dpid, dst_dpid, delay_ms, bandwidth_bit_per_sec,
                 plr_percents):
        self.src_dpid = dpid_to_string(src_dpid)
        self.dst_dpid = dpid_to_string(dst_dpid)
        self.delay_ms = delay_ms
        self.bandwidth_bit_per_sec = bandwidth_bit_per_sec
        self.plr_percents = plr_percents


class NetworkMonitorController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(NetworkMonitorController, self).__init__(req, link, data,
                                                       **config)
        self.network_monitor = data[network_monitor_instance_name]

    @route('networkmonitor', '/networkmonitor/links', methods=['GET'])
    def get_links(self, req, **kwargs):
        links = self.network_monitor.create_links_view()
        body = json.dumps(links)
        return Response(content_type='application/json', body=body)