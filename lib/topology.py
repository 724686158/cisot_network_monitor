from lib.util import delete_duplicates_from_list


class Topology:
    def __init__(self):
        self._dpid_and_opposite_port_to_opposite_dpid = {}
        self._dpid_to_ports = {}

    def get_ports(self, dpid):
        return self._dpid_to_ports.setdefault(dpid, [])

    def register_link(self, src_dpid, src_port_no, dst_dpid, dst_port_no):
        self._dpid_and_opposite_port_to_opposite_dpid.setdefault(
            src_dpid, {})[dst_port_no] = dst_dpid
        self._dpid_and_opposite_port_to_opposite_dpid.setdefault(
            dst_dpid, {})[src_port_no] = src_dpid

        self._dpid_to_ports.setdefault(src_dpid, []).append(src_port_no)
        self._dpid_to_ports[src_dpid] = delete_duplicates_from_list(
            self._dpid_to_ports[src_dpid])
        self._dpid_to_ports.setdefault(dst_dpid, []).append(dst_port_no)
        self._dpid_to_ports[dst_dpid] = delete_duplicates_from_list(
            self._dpid_to_ports[dst_dpid])

    def get_opposite_dpid(self, dpid, opposite_port_no):
        return self._dpid_and_opposite_port_to_opposite_dpid.setdefault(
            dpid, {}).setdefault(opposite_port_no, 0)


class Link:
    def __init__(self, src_dpid, src_port_no, dst_dpid, dst_port_no):
        self.src_dpid = src_dpid
        self.src_port_no = src_port_no
        self.dst_dpid = dst_dpid
        self.dst_port_no = dst_port_no

    def __hash__(self):
        return hash(
            str(self.src_dpid) + str(self.src_port_no) + str(self.dst_dpid) +
            str(self.dst_port_no))

    def __eq__(self, other):
        return self.src_dpid == other.src_dpid and \
                self.src_port_no == other.src_port_no and \
                self.dst_dpid == other.dst_dpid and \
                self.dst_port_no == other.dst_port_no

    def __str__(self):
        return 'src_dpid=' + str(self.src_dpid) + ';' + \
                'src_port_no=' + str(self.src_port_no) + ';' + \
                'dst_dpid=' + str(self.dst_dpid) + ';' + \
                'dst_port_no=' + str(self.dst_port_no)


class LinkRepository:
    def __init__(self):
        self._links = {}

    def register_link(self, src_dpid, src_port_no, dst_dpid, dst_port_no):
        link = Link(src_dpid, src_port_no, dst_dpid, dst_port_no)
        self._links[link] = link

    def find_directed_links(self):
        return self._links.values()

    def find_bidirectional_links(self):
        s = BidirectionalLinkSet()
        for link in self.find_directed_links():
            s.add(link)
        return s.get_all()


class BidirectionalLinkSet:
    def __init__(self):
        self._directed_links = {}
        self._bidirectional_links = []

    def _get_opposit_link(self, link):
        first_direction_link = self._directed_links.setdefault(
            link.src_dpid, {}).setdefault(link.dst_dpid, None)
        if first_direction_link:
            return first_direction_link

        second_direction_link = self._directed_links.setdefault(
            link.dst_dpid, {}).setdefault(link.src_dpid, None)
        return second_direction_link

    def add(self, link):
        opposite_link = self._get_opposit_link(link)
        if opposite_link:
            self._bidirectional_links.append(link)
        else:
            self._directed_links[link.src_dpid][link.dst_dpid] = link

    def get_all(self):
        return self._bidirectional_links
