#!/usr/bin/env python
#
# Copyright 2017
# Johannes K. Fichte, TU Wien, Austria
#
# runsolver_wrapper.py is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
# runsolver_wrapper.py is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.  You should have received a
# copy of the GNU General Public License along with
# runsolver_wrapper.py.  If not, see <http://www.gnu.org/licenses/>.

import cStringIO
import getpass
from itertools import count
import logging
import networkx as nx
from optparse import OptionParser
import re
import select
from sys import stderr, stdin, stdout
from time import gmtime, strftime
import zipfile

from compression import open_transparent


fromfile=True
if select.select([stdin,],[],[],0.0)[0]:
    inp=stdin
    fromfile=False
else:
    parser = OptionParser()
    parser.add_option('-f', '--file', dest='filename',
                  help='Input file', metavar='FILE')
    (options, args) = parser.parse_args()
    if not options.filename:
        stderr.write('Missing filename')
        parser.print_help(stderr)
        stderr.write('\n')
        exit(1)
    inp = open_transparent(options.filename)
    fromfile=True

def parse_and_run(f, graph):
    #string = re.sub(r'label ".+"', lambda x: 'label "a%s"' %next(lbl_counter), string)
    vertex_expr = re.compile("^vertex\(\"(?P<label>.+)\"\,.+\,.+\)\.")
    edge_expr = re.compile("^edge\(\"(?P<start>.+)\"\s*\,\s*\"(?P<end>.+)\"\)\.")
    for line in f:
        if line.startswith('%'):
            continue
        v = re.match(vertex_expr, line)
        if v: 
            label=v.group('label')
            #skip it so far
            continue
        e = re.match(edge_expr, line)
        if e:
            start,end=e.groups(['start','end'])
            graph.add_edge(start,end)
        continue

G = nx.Graph()
parse_and_run(inp, G)

stream = stdout
stream.write('p edge %s %s\n' %(G.number_of_nodes(), G.number_of_edges()))
G = nx.convert_node_labels_to_integers(G, first_label=1)

text = r'''c
c Graphs generated from publicly available GTFS transit feeds by Johannes K. Fichte
c
c Known Bugs:
c - Does not handle multiple names for the same stop, e.g., 
c     Stop 17 - Main North Rd - East side / Stop 17 Main North Rd - West side
c     will result in two separate stops
c
c
c References
c [1] https://en.wikipedia.org/wiki/General_Transit_Feed_Specification or
c [2] https://developers.google.com/transit/gtfs/
c [3] https://github.com/daajoe/transit_graphs/blob/master/transitfeeds-tw.pdf
c [4] https://github.com/daajoe/gtfs2graphs
c
c GTFS feeds extracted using gtfs2graphs [4]
c
'''
stream.write(text)
stream.write('c Author: %s (%s)\n' %(getpass.getuser(),strftime("%Y-%m-%d %H:%M:%S", gmtime())))
        
for u,v in G.edges():
    stream.write('%s %s\n' %(u,v))


if fromfile:
    inp.close()

try:
    stdout.close()
except:
    pass

try:
    stderr.close()
except:
    pass
