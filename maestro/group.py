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

        if self.isRoot():
            self.level = 1
        else:
            self.parent.children.append(self)
            self.level = self.parent.level + 1


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

    def add_role(self, role_name, role_variables, priority = None):
        if priority is None:
            priority = self.level

        role = self.get_role(role_name)
        if role is not None:
            if role.variables is None:
                role.variables = role_variables
            elif role_variables is not None:
                # Bit itchy but will do for now..
                if priority >= role.priority:
                    role.priority = priority
                    role.variables = merge_variables(role.variables, role_variables)
                else:
                    role.variables = merge_variables(role_variables, role.variables)
        else:
            self.roles.append(
            Role(
                name = role_name,
                variables = role_variables,
                priority = priority))
        # Propagate to children
        for child in self.children:
            child.add_role(role_name, role_variables, priority)


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

    def get_vars_filename(self, role_name):
        return "group_vars/{}/{}.yml".format(
                    self.name,
                    role_name)
        return None

    def print_roles(self):
        for role in self.roles:
            print(str(role))

"""
Objects of this class represent a role to be executed in a group of servers.
"""
class Role(object):


    def __init__(self, name, variables, priority):
        self.name = name
        self.variables = variables
        self.priority = priority

    def __str__(self):
        return "name = {name}, variables = {variables}".format(
                name = self.name,
                variables = self.variables)

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
def for_each_group_below(group,
                         method,
                         **kwargs):
    # Run method
    method(group, **kwargs)
    for child in group.children:
        # Propagate to children
        for_each_group_below(
            child,
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


def merge_variables(no_precedence, precedence):
    result = no_precedence.copy()   # start with x's keys and values
    result.update(precedence)    # modifies z with y's keys and values & returns None
    return result
