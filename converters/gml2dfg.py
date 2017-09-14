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

    
#strict implementation of gml "edge \n [ -> edge ["
string = re.sub(r'\s+\[', ' [', ''.join(inp.readlines()))
#remove additional route_type infos
string = re.sub(r'\s+route\_type [0-9]+', '', string)
string = re.sub(r'\s+agency None', '', string)
string = re.sub(r'\s+weight None', '', string)

##XML read string by xmlcharrefreplace -> unicode, replace all non-ascii characters
#from HTMLParser import HTMLParser
#parser = HTMLParser()
#string = parser.unescape(string)
#string = string.encode('ascii', 'ignore')

#replace labels by unique id
lbl_counter = count()
string = re.sub(r'label ".+"', lambda x: 'label "a%s"' %next(lbl_counter), string)

G = nx.parse_gml(string)
stream = stdout

stream.write('p edge %s %s\n' %(G.number_of_nodes(), G.number_of_edges()))
G = nx.convert_node_labels_to_integers(G, first_label=1)

text = r'''c
c Graphs generated from publicly available GTFS transit feeds by Johannes K. Fichte
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

def get_additional_infos(filename):
    fh = open(filename, 'rb')
    zf = zipfile.ZipFile(fh)
    try:
        data = zf.read('feed_info.txt').split('\n')
    except KeyError:
        data = zf.read('agency.txt').split('\n')
        
    fh.close()
    return data


def output_additional_feed_info(stream, filename):
    if fromfile:
        stream.write('c Origin: %s\n' %filename)
        gtfsfilename = filename.replace('gml','zip')
        try:
            with open(gtfsfilename, 'rb') as fh:
                if zipfile.is_zipfile(fh):
                    stream.write('c Feed details:\n')
                    for line in get_additional_infos(gtfsfilename):
                        stream.write('c %s\n' %line)
                    stream.write('c\n')
                else:
                    logging.error('File "%s" is not a zipfile.' % gtfsfilename)
        except IOError:
            logging.error('File "%s" does not exit.' % gtfsfilename)

output_additional_feed_info(stream,options.filename)
        
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
