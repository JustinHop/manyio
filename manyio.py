#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''manyio Justin Hoppensteadt 2019 <justinrocksmadscience@gmail.com
Usage: manyio [options] [INPUT] [OUTPUT]

Options:
    -i --informat=FORMAT     Format of input  [default: auto]
    -o --outformat=FORMAT    Format of output [default: pretty]
    -D --debug               Debug output
    -F --formats             List supported formats
    -h --help                help

Arguments:
    INPUT           Input file, - or none for stdin
    OUTPUT          Output file, or none for stdout
'''

import inspect
import os
import sys
import xml.etree.ElementTree as ET
import re
import yaml
import json
import xmltodict

from collections import defaultdict, OrderedDict
from pprint import pformat
from docopt import docopt

conf = {}
INFMTS = ["auto", "json", "xml", "yaml"]
OUTFMTS = ["auto", "json", "xml", "yaml", "pretty"]

try:
    basestring
except NameError:  # python3
    basestring = str


def setup_yaml():
    """ https://stackoverflow.com/a/8661021 """

    def represent_dict_order(
        self, data): return self.represent_mapping(
        'tag:yaml.org,2002:map', data.items())
    yaml.add_representer(OrderedDict, represent_dict_order)


setup_yaml()


def debug(message):
    if conf['--debug']:
        print(inspect.stack()[1].function, ":", message)


# these next two are from stackexchange


# def etree_to_dict(t):
#     d = {t.tag: {} if t.attrib else None}
#     children = list(t)
#     if children:
#         dd = defaultdict(list)
#         for dc in map(etree_to_dict, children):
#             for k, v in dc.items():
#                 dd[k].append(v)
#         d = {t.tag: {k: v[0] if len(v) == 1 else v
#                      for k, v in dd.items()}}
#     if t.attrib:
#         d[t.tag].update(('@' + k, v)
#                         for k, v in t.attrib.items())
#     if t.text:
#         text = t.text.strip()
#         if children or t.attrib:
#             if text:
#                 d[t.tag]['#text'] = text
#         else:
#             d[t.tag] = text
#     return d
#
#
# def dict_to_etree(d):
#     def _to_etree(d, root):
#         if not d:
#             pass
#         elif isinstance(d, str):
#             root.text = d
#         elif isinstance(d, dict):
#             for k, v in d.items():
#                 assert isinstance(k, str)
#                 if k.startswith('#'):
#                     assert k == '#text' and isinstance(v, str)
#                     root.text = v
#                 elif k.startswith('@'):
#                     assert isinstance(v, str)
#                     root.set(k[1:], v)
#                 elif isinstance(v, list):
#                     for e in v:
#                         _to_etree(e, ET.SubElement(root, k))
#                 else:
#                     _to_etree(v, ET.SubElement(root, k))
#         else:
#             assert d == 'invalid type', (type(d), d)
#     assert isinstance(d, dict) and len(d) == 1
#     tag, body = next(iter(d.items()))
#     node = ET.Element(tag)
#     _to_etree(body, node)
#     return node


def process_input(input):
    indata = ""
    fmt = conf['--informat']
    if input == '-':
        for line in sys.stdin:
            indata = indata + line
    elif os.path.isfile(input):
        debug("Is File")
        with open(input, "r") as FileIn:
            indata = FileIn.read()
    if fmt:
        if re.match(r'^xml', str(fmt), re.I):
            debug("Try to process xml")
            return(xmltodict.parse(input))
            # return(etree_to_dict(ET.fromstring(indata)))
        if re.match(r'^yam?l', str(fmt), re.I):
            debug("Try to process yaml")
            return(yaml.load_all(indata))
        if re.match(r'^json', str(fmt), re.I):
            debug("Try to process json")
            return(json.loads(indata))


def process_output(fmt, data):
    debug(type(data))
    if re.match(r'^yam?l', str(fmt), re.I):
        return(yaml.dump(data))
    if re.match(r'^xml', str(fmt), re.I):
        try:
            return(ET.tostring(data.items()))
        except AttributeError:
            debug('return(ET.tostring(data.items())) didnt work')
        try:
            return(ET.tostringlist(data))
        except AttributeError:
            debug('return(ET.tostringlist(data)) didnt work')
        return(xmltodict.unparse(data))
    if re.match(r'^json', str(fmt), re.I):
        return(json.dumps(data))
    if re.match(r'^pretty', str(fmt), re.I):
        return(pformat(data))


def format_from_filename(f):
    filename = str(f)
    debug(["filename", filename])
    if re.match(r'.*\.xml$', filename, re.I):
        debug("Filetype XML")
        return('xml')
    elif re.match(r'.*\.js?(on)?$', filename, re.I):
        debug("Filetype JSON")
        return('json')
    elif re.match(r'.*\.ya?ml$', filename, re.I):
        debug("Filetype YaML")
        return('yaml')
    raise "No format from filename"


def format_from_data(data):
    try:
        debug('Trying XML')
        return(xmltodict.parse(data))
        # return(etree_to_dict(ET.fromstring(data)))
    except BaseException:
        debug('Not XML Data, trying YaML')
    try:
        return(yaml.load(data, Loader=yaml.FullLoader))
    except BaseException:
        debug('Not YaML Data, trying JSON')
    try:
        return(json.loads(data))
    except BaseException:
        debug('Not JSON Data')


def main():
    global conf
    conf = docopt(__doc__)
    debug(["conf", conf])
    if conf['--formats']:
        print("Input formats:", INFMTS)
        print("Output formats:", OUTFMTS)
        return(1)
    if conf['INPUT']:
        debug("conf INPUT exists")
        infile = str(conf['INPUT'])
        if os.path.exists(infile):
            input = ""
            with open(infile, "r") as InFile:
                input = InFile.read()
            datadict = format_from_data(input)
            debug(["datadict", datadict])
    else:
        if conf['--informat'] == "auto":
            input = ""
            for line in sys.stdin:
                input = input + line
            datadict = format_from_data(input)
            debug(["datadict", datadict])

    fmt = str(conf['--outformat'])

    if conf['OUTPUT']:
        debug('conf OUTPUT exists')

        outfile = str(conf['OUTPUT'])
        debug(["outfile", outfile])

        fmt = format_from_filename(outfile)
        debug(["fmt", fmt])

        output = process_output(fmt, datadict)
        debug(["output", output])

        try:
            with open(outfile, "w") as fileout:
                fileout.write(output)
        except TypeError:
            debug("Writing as string failed, writing as bytes")
            with open(outfile, "wb") as fileout:
                fileout.write(output)

    else:
        debug('conf OUTPUT == None')
        print(process_output(fmt, datadict))


if __name__ == "__main__":
    main()
