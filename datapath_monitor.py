from ryu.base import app_manager
from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import hub
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet

from operator import attrgetter

from lib.measurement_repositories import DatapathResponseTimeRepository, \
    BandwidthPortMeasurementData, PlrPortMeasurementData, PortStatsRepository


class DatapathMonitor(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(DatapathMonitor, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.datapath_timing_repository = DatapathResponseTimeRepository()
        self.bandwidth_port_stats_repository = PortStatsRepository()
        self.plr_port_stats_repository = PortStatsRepository()
        self.monitor_thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        dpid = ev.msg.datapath.id
        self.logger.debug('stats request received: %016x', dpid)
        self._update_switch_response_time(ev)
        body = ev.msg.body
        for stat in sorted(body, key=attrgetter('port_no')):
            self.bandwidth_port_stats_repository.add_stats(
                dpid, stat.port_no,
                BandwidthPortMeasurementData(stat.duration_sec,
                                             stat.duration_nsec, stat.rx_bytes,
                                             stat.tx_bytes))
            self.plr_port_stats_repository.add_stats(
                dpid, stat.port_no,
                PlrPortMeasurementData(stat.rx_packets, stat.tx_packets,
                                       stat.rx_errors, stat.tx_errors))

    def _monitor(self):
        while True:
            hub.sleep(1)
            for dp in self.datapaths.values():
                self._request_port_stats(dp)

    def _request_port_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        self.datapath_timing_repository.write_send_time(datapath.id)
        datapath.send_msg(req)

    def _update_switch_response_time(self, eventOFPPortStatsReply):
        dpid = eventOFPPortStatsReply.msg.datapath.id
        self.datapath_timing_repository.write_receive_time(dpid)
        self.logger.debug(
            'datapath %016x response time: %s ms', dpid,
            self.datapath_timing_repository.get_response_time(
                dpid).milliseconds())
