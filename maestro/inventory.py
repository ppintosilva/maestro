#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

from group import Group, get_leaves, get_roots, get_non_leaves

"""
hello
"""
def get_servers_inventory(group):
    servers = []

    for i in xrange(0, group.servers, 1):
        servers.append("[{}]".format(group.get_server_name(i+1)))

    return servers


def get_leaf_children(leaf):
    inventory = ["[{}.children]".format(leaf.name)]

    for i in xrange(0, leaf.servers, 1):
        inventory.append(leaf.get_server_name(i+1))

    return inventory

def get_parent_children(group):
    inventory = ["[{}.children]".format(group.name)]

    for child in group.children:
        inventory.append(child.name)

    return inventory


def gen_inventory(groups):
    ini_inventory = []

    leaves = get_leaves(groups)

    for leaf in leaves:
        ini_inventory.append("\n".join(get_servers_inventory(leaf)))
        ini_inventory.append("\n".join(get_leaf_children(leaf)))

    non_leaves = get_non_leaves(groups)

    for non_leaf in non_leaves:
        ini_inventory.append("\n".join(get_parent_children(non_leaf)))

    ini_inventory.append("")

    return "\n\n".join(ini_inventory)
