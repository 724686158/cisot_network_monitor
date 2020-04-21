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
        self.datapath_timing_repository = kwargs[
            'datapath_monitor'].datapath_timing_repository
        self.link_latency_repository = kwargs[
            'link_monitor'].link_latency_repository
        self.link_repository = LinkRepository()
        self.monitor_thread = hub.spawn(self._log)

    def _log(self):
        while True:
            hub.sleep(5)
            self.logger.info(json.dumps(self.create_links_view()))

    def create_links_view(self):
        links_view = []
        for link in self.link_repository.find_bidirectional_links():
            links_view.append(
                LinkViewModel(link.src_dpid, link.dst_dpid,
                              self.compute_delay_ms(link)).__dict__)
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

    @set_ev_cls(event.EventSwitchEnter)
    def handler_switch_enter(self, ev):
        for link in copy.copy(get_link(self)):
            self.link_repository.register_link(link.src.dpid, link.src.port_no,
                                               link.dst.dpid, link.dst.port_no)


class LinkViewModel:
    def __init__(self, src_dpid, dst_dpid, delay):
        self.src_dpid = src_dpid
        self.dst_dpid = dst_dpid
        self.delay_ms = delay


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