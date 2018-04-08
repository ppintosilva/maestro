#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

from group import Group, for_each_group_below

"""
hello
"""
def get_servers_inventory(group):
    servers = []

    for i in xrange(0, group.servers, 1):
        servers.append("[{}]".format(group.get_server_name(i+1)))

    return servers


def get_group_inventory(group):
    group_inventory = ["[{}.children]".format(group.name)]

    for i in xrange(0, group.servers, 1):
        group_inventory.append(group.get_server_name(i+1))

    return group_inventory


def gen_inventory(roots):
    ini_inventory = []

    for_each_group_below(
        groups = roots,
        method = lambda group:
            ini_inventory.append("\n".join(get_servers_inventory(group)))
    )

    for_each_group_below(
        groups = roots,
        method = lambda group:
            ini_inventory.append("\n".join(get_group_inventory(group)))
    )

    return "\n\n".join(ini_inventory)
