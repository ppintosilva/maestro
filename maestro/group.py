#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Implements the Group class and auxiliary methods.

Each instance of the Group class represents
a group of servers.

Root groups have no parent group
(except for group 'all' in ansible).
"""

class Group(object):
    def __init__(self, name, servers, parent = None):
        self.name = name
        self.servers = servers
        self.parent = parent
        self.children = []
        self.roles = []

        if not self.isRoot():
            self.parent.children.append(self)


    def __str__(self):
        return "name = {name}, servers = {servers}, parent = {parent}, children = {children}".format(
                name = self.name,
                servers = self.servers,
                parent = "None" if self.parent is None else self.parent.name,
                children = map(lambda x: x.name, self.children))

    def isRoot(self):
        return not bool(self.parent)

    def isLeaf(self):
        return len(self.children) == 0

    def add_role(self, role_name, role_variables):
        # TODO - propagate role to children (all below) and merge variables
        self.roles.append(
            Role(
                name = role_name,
                group_name = self.name,
                variables = role_variables))

    def get_role(self, role_name):
        for role in self.roles:
            if role.name == role_name:
                return role
        return None

    def has_role(self, role_name):
        for role in self.roles:
            if role.name == role_name:
                return True
        return False

    def get_server_name(self, i):
        if self.isRoot() or self.parent.name in self.name.split("-"):
            name = self.name
        else:
            name = "{}-{}".format(self.parent.name, self.name)

        return "{}-{:03d}".format(name, i)

"""
Objects of this class represent a role to be executed in a group of servers.
"""
class Role(object):


    def __init__(self, name, group_name, variables):
        self.name = name
        self.group_name = group_name
        self.variables = variables

    def __str__(self):
        return "name = {name}, group_name = {group_name}, variables = {variables}".format(
                name = self.name,
                group_name = self.group_name,
                variables = self.variables)

    def get_vars_filename(self):
        return "playbooks/group/vars/{}_{}.yml".format(
                    group_name,
                    self.name)

#############################
##
#############################
#  Auxiliary methods
#############################
##
#############################


"""
Retrieves the list of roots from a dictionary of groups
"""
def get_roots(groups):
    return [group for group in groups.values() if group.isRoot()]


"""
Retrieves the list of roots from a dictionary of groups
"""
def get_leaves(groups):
    return [group for group in groups.values() if group.isLeaf()]

"""
Retrieves the list of roots from a dictionary of groups
"""
def get_non_leaves(groups):
    return [group for group in groups.values() if not group.isLeaf()]

"""
Retrieves the list of group names from a dictionary of groups
"""
def get_names(groups):
    return [group.name for group in groups.values()]

def get_group_ancestry_stack(group):
    stack = []

    for_each_group_above(
        group = group,
        method = lambda x: stack.append(x))

    return stack

"""
Recursive wrappers for running arbitrary methods on every node in a tree-like structure (depth-first search):

    for_each_group(starting_groups,
                   method,
                   **kwargs)

    where:
    - starting_groups = the groups where the method is first run (usually, roots or leaves)

    - method

    - **kwargs = further parameters to be passed to method
"""
def for_each_group_below(groups,
                         method,
                         **kwargs):
    for group in groups:
        # Run method
        method(group, **kwargs)
        # Propagate to children
        for_each_group_below(
            group.children,
            method,
            **kwargs)


def for_each_group_above(group,
                         method,
                         **kwargs):
    # Run method
    method(group, **kwargs)
    # Propagate to parents
    if not group.isRoot():
        for_each_group_above(
            group.parent,
            method,
            **kwargs)
