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
#                        Group and Role classes
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
        self.variables = variables

    def __str__(self):
        return "name = {name}, variables = {variables}".format(
                name = self.name,
                variables = self.variables)

    def get_vars_filename(self, group):
        return "playbooks/group/vars/{}_{}.yml".format(
                    group.name,
                    self.name)


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
#               Generate concerto.yaml and all.yaml
########################################################################
##
########################################################################

def gen_concerto(groups):
    pass
    # concerto =
    # """
    # - hosts: localhost
    #   gather_facts: no
    #
    #   roles:
    #
    # """
    #
    # for

def gen_all_groups_playbook(groups):
    intermezzo = []

    for_each_group_below(
        groups = get_roots(groups),
        method = lambda x: intermezzo.append(
            "- include: group/{}.yml".format(x.name)))

    return "\n\n".join(intermezzo)

def gen_group_play(group):
    pass

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

def read_variables(raw_variables):
    # Either a dictionary or none
    if isinstance(raw_variables, dict):
        """
        Here, I won't be checking if the elements of variables are not dictionaries or lists. I guess it's up to the user to be sensible
        at this point, unless the objective is to break the software.
        """
        variables = raw_variables

    elif raw_variables is None:
        variables = None

    else:
        raise ValueError("One or more variables are not well defined (expecting a dictionary or None)".format())

    return variables


def read_roles(dic, groups):

    group_names = get_names(groups)

    for group_name, roles in dic.iteritems():
        group_name = group_name.lower()

        if group_name == "all":
            roots = get_roots(groups)
        elif group_name not in group_names:
            raise ValueError("Group named '{}' does not exist in groups: it was not provided in groups_file or groups_text.".format(group_name))
        else:
            group = groups[group_name]

        # A single role as a string with no variables defined
        if isinstance(roles, str):
            group.add_role(role_name, None)

        # A dictionary of roles
        elif isinstance(roles, dict):

            for role_name, raw_variables in roles.iteritems():
                variables = read_variables(raw_variables)
                if group_name == "all":
                    map(lambda x: x.add_role(role_name, variables),
                        roots)
                else:
                    group.add_role(role_name, variables)

        # No roles
        elif roles is None:
            pass

        else:
            raise ValueError("Group '{}' should be followed by nothing or a role (dictionary).".format(group_name))

    return groups

########################################################################
##
########################################################################
#                        SINGLE CLI COMMAND
########################################################################
##
########################################################################

@click.command()
@click.argument(
    'band',
    nargs = 1,
    type = click.File(mode = 'r'))
@click.option(
    '--instruments',
    help = "Yaml file with roles to be executed by each group",
    default = None,
    type = click.File(mode = 'r'))
@click.option(
    '--provider',
    type = click.Choice(['openstack']),
    default = "openstack",
    help = "Name of target cloud provider")
# ---
# ---
def genesis(band,
            instruments,
            provider):
    """
    Transform a bare set of requirements into fully
    formed bands of servers ready to perform for you.

    This is a complementary tool to ansible for cloud
    orchestration. It generates ansible scripts that
    help you automate the deployment of servers and
    software on the cloud.

    Specifically, this program creates:

    (1) - a static inventory file to be used
    together with a dynamic inventory file. This allows
    you to run playbooks for groups of servers within
    the fast-changing cloud environment. This is not
    possible using a dynamic inventory file by itself,
    like, for instance, 'openstack.py'.

    (2) - playbooks for each group, populated with roles
    optionally specified in '--instruments'. If no roles
    are provided,

    BAND should be a yaml file which lists the names
    and number of servers of each group and their children.

    More detail can be found in README.md.
    """

    # Yaml parse error is thrown for us if not formatted correctly
    yaml_groups_dict = yaml.safe_load(band)

    # Read and spit out inventory
    groups = read_groups(yaml_groups_dict)

    with open('inventory/hosts', 'w') as inventory_file:
        inventory = gen_inventory(get_roots(groups))
        inventory_file.write(inventory)

    # Parse roles contents
    if instruments:
        yaml_roles_dict = yaml.safe_load(instruments)
        groups = read_roles(yaml_roles_dict, groups)

    # Write group vars to playbooks/group/vars/group_ROLE
    for group in groups.values():
        for role in group.roles:
            role_vars_filename = role.get_vars_filename(group)
            with open(role_vars_filename, 'w') as role_vars_file:
                yaml.safe_dump(role.variables,
                               role_vars_file,
                               default_flow_style=False)

    # For each group
        # Create playbooks/group/group_name.yaml

    # Create playbooks/intermezzo.yaml
    # Waits for ssh and executes all group plays in playbooks/group
    with open('playbooks/intermezzo.yml', 'w') as intermezzo_file:
        intermezzo_file.write(gen_all_groups_playbook(groups))

    # Create playbooks/concerto.yaml
    # Creates all instances
    with open('playbooks/concerto.yml', 'w') as concerto_file:
        concerto_file.write(gen_concerto(groups))

    # PRINT
    # Success! The following files were generated:
    # Run ... to do this and do that

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
