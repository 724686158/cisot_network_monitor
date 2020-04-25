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
import unittest

from lib.topology import Topology, Link, LinkRepository, BidirectionalLinkSet


class TestTopology(unittest.TestCase):
    def test_get_opposite_dpid__empty_topology(self):
        topo = Topology()

        self.assertEqual(topo.get_opposite_dpid(1, 19), 0)

    def test_get_opposite_dpid(self):
        topo = Topology()

        topo.register_link(1, 24, 2, 19)

        self.assertEqual(topo.get_opposite_dpid(1, 19), 2)
        self.assertEqual(topo.get_opposite_dpid(2, 24), 1)

    def test_get_ports__empty_topology(self):
        topo = Topology()

        self.assertEqual(topo.get_ports(1), [])

    def test_get_ports(self):
        topo = Topology()

        self.assertEqual(topo.get_ports(1), [])

        topo.register_link(1, 24, 2, 19)
        topo.register_link(1, 21, 3, 10)

        self.assertEqual(topo.get_ports(1), [24, 21])
        self.assertEqual(topo.get_ports(2), [19])
        self.assertEqual(topo.get_ports(3), [10])

    def test_register_link__multiple_times(self):
        topo = Topology()

        for _ in range(10):
            topo.register_link(1, 24, 2, 19)

        self.assertEqual(topo.get_ports(2), [19])
        self.assertEqual(topo.get_opposite_dpid(1, 19), 2)
        # check side effects
        self.assertEqual(topo.get_ports(10), [])
        self.assertEqual(topo.get_opposite_dpid(15, 4), 0)


class TestLink(unittest.TestCase):
    def test__hash__(self):
        link1 = Link(1, 19, 2, 24)
        link2 = Link(1, 19, 2, 24)
        link3 = Link(2, 14, 3, 11)

        self.assertEqual(hash(link1), hash(link2))
        self.assertEqual(hash(link3), hash(link3))
        self.assertNotEqual(hash(link1), hash(link3))
        self.assertNotEqual(hash(link2), hash(link3))

    def test__eq__(self):
        link1 = Link(1, 19, 2, 24)
        link2 = Link(1, 19, 2, 24)
        link3 = Link(2, 14, 3, 11)

        self.assertEqual(link1, link2)
        self.assertEqual(link3, link3)
        self.assertNotEqual(link1, link3)
        self.assertNotEqual(link2, link3)

    def test__str__(self):
        link = Link(1, 19, 2, 24)

        self.assertEqual(
            str(link), 'src_dpid=1;src_port_no=19;dst_dpid=2;dst_port_no=24')


class TestLinkRepository(unittest.TestCase):
    def test_find_directed_links(self):
        repo = LinkRepository()
        link1 = Link(1, 19, 2, 24)
        link2 = Link(2, 14, 3, 11)
        repo.register_link(link1.src_dpid, link1.src_port_no, link1.dst_dpid,
                           link1.dst_port_no)
        repo.register_link(link1.src_dpid, link1.src_port_no, link1.dst_dpid,
                           link1.dst_port_no)
        repo.register_link(link2.src_dpid, link2.src_port_no, link2.dst_dpid,
                           link2.dst_port_no)

        self.assertSetEqual(set(repo.find_directed_links()),
                            set([link1, link2]))

    def test_find_bidirectional_links(self):
        repo = LinkRepository()
        link1 = Link(1, 19, 2, 24)
        link2 = Link(2, 24, 1, 19)
        repo.register_link(link1.src_dpid, link1.src_port_no, link1.dst_dpid,
                           link1.dst_port_no)
        repo.register_link(link2.src_dpid, link2.src_port_no, link2.dst_dpid,
                           link2.dst_port_no)

        self.assertListEqual(repo.find_bidirectional_links(), [link2])


class TestBidirectionalLinkSet(unittest.TestCase):
    def test_add(self):
        link1 = Link(1, 19, 2, 24)
        link2 = Link(2, 24, 1, 19)

        link3 = Link(2, 21, 3, 9)

        link4 = Link(3, 10, 4, 11)
        link5 = Link(4, 11, 3, 10)

        s = BidirectionalLinkSet()
        s.add(link1)
        s.add(link2)
        s.add(link3)
        s.add(link4)
        s.add(link5)

        expected = [link2, link5]
        self.assertListEqual(s.get_all(), expected)


if __name__ == '__main__':
    unittest.main()
