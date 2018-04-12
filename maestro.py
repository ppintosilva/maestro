#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main maestro executable script.

Provides a single CLI command that accepts
user input as files and generates the inventory
file and playbooks for the list of groups and
roles provided in the input.
"""

import yaml
import click
import os
import sys

from maestro.input import read_roles, read_groups
from maestro.inventory import gen_inventory
from maestro.playbooks import gen_all_groups_playbook, gen_concerto, gen_individual_playbooks, write_variables

#sys.tracebacklimit = 0

@click.command()
@click.argument(
    'orchestra',
    nargs = 1,
    required = True,
    type = click.File(mode = 'r'))
@click.argument(
    'instruments',
    default = None,
    required = False,
    nargs = 1,
    type = click.File(mode = 'r'))
@click.option(
    '--stage',
    type = click.Choice(['openstack']),
    default = "openstack",
    help = "Name of target cloud provider")
# ---
# ---
def genesis(orchestra,
            instruments,
            theatre):
    """
    Transform a bare set of requirements into an
    orchestra of servers ready to perform for you.

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

    ORCHESTRA is a yaml file which lists the names
    and number of servers of each group and their children.

    INSTRUMENTS is a yaml file which lists the roles and
    variables of each group of servers.

    STAGE is the name of the cloud provider, one of:
    {'openstack'}

    More details can be found in README.md.
    """

    # Yaml parse error is thrown for us if not formatted correctly
    yaml_groups_dict = yaml.safe_load(orchestra)

    # Read and spit out inventory
    groups = read_groups(yaml_groups_dict)

    with open('inventory/hosts', 'w') as inventory_file:
        inventory = gen_inventory(groups)
        inventory_file.write(inventory)

    # Parse roles contents
    if instruments:
        yaml_roles_dict = yaml.safe_load(instruments)
        groups = read_roles(yaml_roles_dict, groups)

    # For each group
        # Write group vars to playbooks/group/vars/group_ROLE
        # Create playbooks/group/group_name.yaml
    for group in groups.values():
        write_variables(group)
        gen_individual_playbooks(group)

    # Create playbooks/intermezzo.yaml
    with open('playbooks/intermezzo.yml', 'w') as intermezzo_file:
        intermezzo_file.write(gen_all_groups_playbook(groups))

    # Create playbooks/concerto.yaml
    #   - Play 1: Creates all instances
    #   - Play 2: Waits for ssh
    with open('playbooks/concerto.yml', 'w') as concerto_file:
        concerto_file.write(gen_concerto(groups, theatre))

    # PRINT
    # Success! The following files were generated:
    # Run ... to do this and do that

    return groups


#
# ---
#

if __name__ == "__main__":
    if os.getuid() == 0:
	    sys.exit("Do not run this script as root.")
    genesis()
