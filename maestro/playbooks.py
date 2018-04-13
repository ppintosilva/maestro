#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bananas
"""

from group import Group, get_leaves, for_each_group_below, get_roots
import yaml


"""
hello
"""
def gen_include_create_group(group):
    if group.servers == 0:
        return ""

    create_group_servers = [
    "    - name: Create servers of group '{}'".format(group.name),
    "      import_role:",
    "        name: create_server"]

    if group.has_role("create_server"):
        create_group_servers.append(
            "        vars_from: group/{}_create_server.yml".format(group.name))

    create_group_servers.append(
    "      with_items:")

    for i in xrange(0, group.servers, 1):
        create_group_servers.append(
        "      - {}".format(group.get_server_name(i+1)))

    create_group_servers.append("      loop_control:")
    create_group_servers.append("        loop_var: server")
    create_group_servers.append("")

    return "\n".join(create_group_servers)

def gen_group_wait_for(group):
    wait_for = [
    "# Wait play",
    "- hosts: {}".format(group.name),
    "  gather_facts: no",
    "  remote_user: {}".format("TESTE"),
    "",
    "  tasks:",
    "    - name: Wait for group instances to become reachable over WinRM",
    "      wait_for_connection:",
    "        timeout: {}".format("TESTE"),
    ""]

    return "\n".join(wait_for)

###

def gen_concerto(groups, provider):
    concerto = [
    "# Play 1: Create all servers",
    "- hosts: localhost",
    "  gather_facts: no",
    "  vars:",
    "    provider: {}".format(provider),
    "",
    "  tasks:",
    "    - name: Retrieve list of existing server names",
    "      os_server_facts:",
    "      when: provider == openstack",
    ""]

    leaves = get_leaves(groups)

    for leaf in leaves:
        concerto.append(gen_include_create_group(leaf))

    concerto.append("    - name: Refresh in-memory {} cache".format(provider))
    concerto.append("      meta: refresh_inventory")
    concerto.append("")

    for leaf in leaves:
        concerto.append(gen_group_wait_for(leaf))

    concerto.append("")

    return "\n".join(concerto)

###

def gen_all_groups_playbook(groups):
    intermezzo = []

    roots = get_roots(groups)

    # The playbooks of roots are: import playbooks of children .. all the way to leaf nodes
    for root in roots:
        intermezzo.append(
                "- import_playbook: group/{}.yml".format(root.name))

    return "\n\n".join(intermezzo)


def gen_individual_playbook(group):
    if group.isLeaf():
        playbook = [
        "- hosts: {}".format(group.name),
        "  gather_facts: yes",
        "  remote_user: {}".format("TESTE"),
        "  become: yes",
        "",
        "  tasks:"]

        for role in group.roles:
            if role.name == "create_server" or role.name == "setup_image":
                continue
            playbook.append("    - name: Execute role '{}'".format(role.name))
            playbook.append("      import_role:")
            playbook.append("        name: {}".format(role.name))
            playbook.append("        vars_from: {}".format(group.get_vars_filename(role.name)))
            playbook.append("")

    else:
        playbook = []

        for child in group.children:
            playbook.append("- import_playbook: {}.yml".format(child.name))
            playbook.append("")

    return "\n".join(playbook)


def write_variables(group):
    for role in group.roles:
        if role.variables is None:
            continue
        role_vars_filename = group.get_vars_filename(role.name)
        with open(role_vars_filename, 'w') as role_vars_file:
            yaml.safe_dump(role.variables,
                           role_vars_file,
                           default_flow_style=False)
