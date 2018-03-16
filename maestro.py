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
    Root groups have no parent group.
    """

    def __init__(self, name, servers, parent = None):
        self.name = name
        self.servers = servers
        self.parent = parent
        self.servers_names = ""

    def __str__(self):
        if self.parent is None:
            return "name = {}, servers = {}, parent = None".format(
                self.name, self.servers)
        else:
            return "name = {}, servers = {}, parent = {}".format(
                self.name, self.servers, self.parent.name)

    def isRoot(self):
        if self.parent is None:
            return True
        else:
            return False

########################################################################
##
########################################################################
#                        Read groups method
########################################################################
##
########################################################################


def read_groups(dic, groups = list(), parent = None):

    for name, value in dic.iteritems():
        #print("name: {}, value: {}".format(name, value))
        group = Group(name, 0, parent)

        if isinstance(value, dict):
            groups, childgroup = read_groups(value, groups, parent = group)
            group.servers += childgroup.servers

        elif isinstance(value, int):
            if value > 0:
                group.servers = value
            else:
                raise NonPositiveGroupError("Group {} must have size greater than 0".format(group.name), group)

        else:
            raise ValueError(
                    "The value of each group should be either an integer or a new group. Leaf groups should be in the form: \"group_name: nservers\" ")

        groups.append(group)

    return groups, group


########################################################################
##
########################################################################
#                        SINGLE CLI COMMAND
########################################################################
##
########################################################################

# ---
# ---
# ---
# ---

# @click.option(
#     '--interactive',
#     'mode',
#     flag_value = 'interactive',
#     default = True,
#     help = "Run in interactive mode (questions will be asked throughout the process)"
# )
# @click.option(
#     '--automatic',
#     'mode',
#     flag_value = 'automatic',
#     default = False,
#     help = "Run in automatic mode (no questions will be asked and inputs should be provided through options)"
# )
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
    print(groups_file)
    print(groups_text)
    # Is there a better way?
    if not groups_file and not groups_text:
        raise ValueError("Group requirements must be provided from a file or string, using one of the two available options: --groups-file | --groups_text")
    elif groups_file and groups_text:
        raise ValueError("Two group requirements were provided: --groups-file was used together with --groups-text. Only one option should be used.")
    elif groups_file:
        contents = groups_file
    else:
        contents = groups_text

    # Yaml parse error is thrown for us if not formatted correctly
    yaml_dict = yaml.safe_load(contents)

    # Read and spit out inventory
    groups = read_groups(yaml_dict)[0]

    # i = 0
    # for group in groups:
    #     print("Group {}: {}".format(i, str(group)))
    #     i += 1

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
