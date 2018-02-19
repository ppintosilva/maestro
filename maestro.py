#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is bananas
"""

import yaml
import click
import os

# ---

@click.group(help = "This is sparta!")
def orchestrify():
    pass

# ---

@orchestrify.command(
    name = "lead",
    short_help="Lead a band to glory.")
@click.option(
    '--config',
    required = False,
    default = "band.yml",
    help = "Server requirements config file",
    type = click.File(mode = 'r'))
def create_inventory(config):
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

    The configuration file, in yaml format, should list
    the names of major groups and their children. The
    number of servers in each group should be provided.

    \b
    Consider the following configuration:
    \b
        databases: 1
    \b
        compute: 6
            spark: 4
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
    try:
        groups = yaml.safe_load(config)
    except yaml.YAMLError as err:
        print(err)
        return

    print(groups)

# ---

if __name__ == "__main__":
    if os.getuid() == 0:
	sys.exit("Do not run this script as root.")
    orchestrify()
