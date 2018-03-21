#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is bananas
"""

import yaml
import click
import os
import sys

#sys.tracebacklimit = 0

########################################################################
##
########################################################################
#                       Custom exceptions
########################################################################
##
########################################################################


class NonPositiveGroupError(ValueError):
    '''Raise when a non positive integer is passed as group size'''
    def __init__(self, message, group, *args):
        self.message = message # without this you may get DeprecationWarning
        # Special attribute you desire with your Error,
        # perhaps the value that caused the error?:
        self.group = group
        # allow users initialize misc. arguments as any other builtin Error
        super(NonPositiveGroupError, self).__init__(message, group, *args)


########################################################################
##
########################################################################
#                        Group class
########################################################################
##
########################################################################


class Group(object):
    """
    Object representing a group of servers.

    Root groups have no parent group
    (except for group 'all' in ansible).
    """

    def __init__(self, name, servers, parent = None, children = list()):
        self.name = name
        self.servers = servers
        self.parent = parent
        self.children = children
        self.roles = []

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
        self.roles.append(Role(role_name, role_variables))


class Role(object):
    """
    Object representing a role to be executed in a group of servers.
    """

    def __init__(self, name, variables):
        self.name = name
        # A n-length dictionary
        self.variables = variables

    def __str__(self):
        return "name = {name}, variables = {variables}".format(
                name = self.name,
                variables = self.variables)


########################################################################
##
########################################################################
#                        Group structure helpers
########################################################################
##
########################################################################

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
Retrieves the list of group names from a dictionary of groups
"""
def get_names(groups):
    return [group.name for group in groups.values()]

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


def for_each_group_above(groups,
                         method,
                         **kwargs):
    for group in groups:
        # Run method
        method(group, **kwargs)
        # Propagate to parents
        if not group.isRoot():
            for_each_group_above(
                [group.parent],
                method,
                **kwargs)

def for_each_server(groups,
                    method,
                    **kwargs):
    for i in xrange(0, group.servers, 1):
        # Run method
        method(group, **kwargs)

########################################################################
##
########################################################################
#                        Read groups method
########################################################################
##
########################################################################

"""
Returns a dictionary in the form:
    name , group

This is useful when you need to run code that doesn't care about
the tree-like structure of the groups.

However, when you care about the structure of the groups,
(for instance, when generating the inventory: groups are written to the
file in a depth-first format) then only the list of root or leaf nodes
is necessary. Then the tree is transversed in the most appropriate manner
to the case: breadth-first, depth-first, top-to-bottom, bottom-to-top, etc.
"""
def read_groups(dic, groups = dict(), parent = None):

    for name, value in dic.iteritems():

        group = Group(name, 0, parent, list())

        # If I'm not a leaf group then read my child groups
        if isinstance(value, dict):
            if name == "other":
                raise ValueError("Groups named 'other' are not allowed.")

            groups = read_groups(value, groups, parent = group)

        # Else if I'm a leaf node
        elif isinstance(value, int):
            # Read number of servers
            if value > 0:
                group.servers = value
            else:
                raise NonPositiveGroupError("Group {} must have size greater than 0".format(group.name), group)

            # Wait.. I'm not really a group..
            if name == "other":
                if group.isRoot():
                    raise ValueError("Groups named 'other' are not allowed.")
                else:
                    group.parent.servers += value
                    continue

        else:
            raise ValueError(
                    "Each group should be either an integer or a new group. Leaf groups should be in the form: \"group_name: nservers\" ")

        # Append me to my parent's children
        if not group.isRoot():
            group.parent.children.append(group)

        if name in groups:
            raise ValueError(
                    "Group names should be unique.")
        groups[name] = group

    return groups


########################################################################
##
########################################################################
#               Generate inventory in INI style from roots
########################################################################
##
########################################################################

def get_server_name(group, i):
    if group.isRoot():
        name = group.name
    else:
        name = "{}-{}".format(group.parent.name, group.name)

    return "{}-{:03d}".format(name, i)


def get_servers_inventory(group):
    servers = []

    for i in xrange(0, group.servers, 1):
        servers.append("[{}]".format(get_server_name(group, i+1)))

    return servers


def get_group_inventory(group):
    group_inventory = ["[{}.children]".format(group.name)]

    for i in xrange(0, group.servers, 1):
        group_inventory.append(get_server_name(group, i+1))

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

########################################################################
##
########################################################################
#                          Read Roles
########################################################################
##
########################################################################

def read_role(role):
    # A role can be:
        # A string (no variables)
        # A dictionary
        # A string (with no variables)

    if isinstance(role, str):
        role_name = role
        raw_variables = None

    elif isinstance(role, dict):
        if len(role.keys()) != 1 or len(role.values()) != 1:
            raise ValueError("This should not happen")

        role_name = role.keys()[0]
        raw_variables = role.values()[0]

    else:
        raise ValueError("Role '{}' is not defined as a string or a dictionary (as it should) but something else instead {}.".format(role_name, type(role)))

    return (role_name, raw_variables)


def read_variables(raw_variables):
    # Variables can be:
        # A n-List of 1-entry dictionaries
        # A n-entry dictionary
    if isinstance(raw_variables, list):
        # Transform the n-list of 1 entry dictionaries to a n-entry dictionary
        # Raise exception if every element in list is not a dictionary
        variables = {}
        for variable in raw_variables:
            if not isinstance(variable, dict):
                raise ValueError("Variable '{}' in role '{}' is not defined correctly. It should be defined as 'varname: value'.".format(variable, role_name))
            variables.update(variable)

    elif isinstance(raw_variables, dict):
        """
        Here, I won't be checking if the elements of variables are not dictionaries or lists. I guess it's up to the user to be sensible
        at this point, unless the objective is to break the software.
        """
        variables = raw_variables

    elif raw_variables is None:
        variables = None

    else:
        raise ValueError("This should not happen. One or more variables are not well defined (expecting a dictionary, list of dictionaries or None)".format())

    return variables


def read_roles(dic, groups):

    group_names = get_names(groups)

    for group_name, roles in dic.iteritems():

        if group_name not in group_names:
            raise ValueError("Group named '{}' does not exist in groups: it was not provided in groups_file or groups_text.".format(group_name))

        group = groups[group_name]

        # List of roles
        if isinstance(roles, list):

            for role in roles:
                role_name , raw_variables = read_role(role)
                variables = read_variables(raw_variables)
                group.add_role(role_name, variables)

        # Dictionary of roles
        elif isinstance(roles, dict):

            for role_name, raw_variables in roles.iteritems():
                variables = read_variables(raw_variables)
                group.add_role(role_name, variables)

        # Nothing - explicitely listing this conditional branch for workflow readability
        elif roles is None:
            pass

        else:
            raise ValueError("Group '{}' is not followed by a role or list of roles (dictionary, list of dictionaries or empty).".format(group_name))

    return groups

########################################################################
##
########################################################################
#                        SINGLE CLI COMMAND
########################################################################
##
########################################################################

@click.command()
@click.option(
    '--groups-file',
    help = "Host group requirements - file",
    type = click.File(mode = 'r'))
@click.option(
    '--groups-text',
    help = "Host group requirements - string",
    type = click.STRING)
@click.option(
    '--roles-file',
    help = "Roles to be run by each group - file",
    type = click.File(mode = 'r'))
@click.option(
    '--roles-text',
    help = "Roles to be run by each group - string",
    type = click.STRING)
# ---
# ---
def genesis(groups_file, groups_text, roles_file, roles_text):
    """
    Lead your band to glory!

    Transform a bare set of band requirements
    into a fully formed band ready to perform.

    This creates a static inventory file to be used
    together with a dynamic inventory file. This allows
    you to run playbooks for groups of servers within
    the fast-changing cloud environment. This is not
    possible using openstack.py solely as an inventory
    file.

    The configuration string, or file in yaml format,
    should list the names of major groups and their
    children. The number of servers in each group
    must also be provided.

    \b
    Consider the following configuration:
    \b
        databases: 1
    \b
        compute:
          spark: 4
          other: 2
    \b
        webservers:
          shiny: 1
          nginx: 1
    \b
    The result is as follows:
    \b
        Group     | Parent Group | Servers
        -----      ------------   -------
        databases     all             1
        compute       all             6
        spark         compute         4
        webservers    all             2
        shiny         webservers      1
        nginx         webservers      1

    The compute group has 6 servers, of which 4 are
    part of subgroup spark and the other 2 have no subgroup.
    If all instances of a parent group are also part of a
    subgroup then the total doesn't have to be provided
    (as in the case of webservers).

    However, if the parent group total is provided and
    the number of servers in its children groups doesn't
    sum up to correctly then the application will exit with error.
    """

    # Is there a better way?
    if not groups_file and not groups_text:
        raise ValueError("Group requirements must be provided from a file or string, using one of the two available options: --groups-file | --groups_text")
    elif groups_file and groups_text:
        raise ValueError("Two group requirements were provided: --groups-file was used together with --groups-text. Only one option should be used.")
    elif groups_file:
        groups_contents = groups_file
    else:
        groups_contents = groups_text

    # Yaml parse error is thrown for us if not formatted correctly
    yaml_groups_dict = yaml.safe_load(groups_contents)

    # Read and spit out inventory
    groups = read_groups(yaml_groups_dict)

    with open('inventory/hosts', 'w') as inventory_file:
        inventory = gen_inventory(get_roots(groups))
        inventory_file.write(inventory)

    # Read roles and vars if available
    if roles_file and roles_text:
        raise ValueError("Two roles/vars were provided: --roles-file was used together with --roles-text. Only one option should be used.")
    elif roles_file:
        roles_contents = roles_file
    elif roles_text:
        roles_contents = roles_text
    else:
        roles_contents = None

    # Parse roles contents
    if roles_contents:
        yaml_roles_dict = yaml.safe_load(roles_contents)
        roles = read_roles(yaml_roles_dict, groups)


    # Create playbooks/concerto.yaml

    # Create playbooks/group/all.yaml

    # For each group
        # Create playbooks/group/group_name.yaml
        # Create playbooks/group/vars/group_name.yaml

    # For each server
        # Create playbooks/host/host_name.yaml
        # Create playbooks/host/vars/host_name.yaml



    return groups


########################################################################
##
########################################################################
#                        MAIN
########################################################################
##
########################################################################


if __name__ == "__main__":
    if os.getuid() == 0:
	    sys.exit("Do not run this script as root.")
    genesis()
