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
def gen_include_create_group(group, base_indentation = "    "):
    if group.servers == 0:
        return ""

    setup_image_group = [
        "{}- name: Setup image for servers of group '{}'".format(base_indentation, group.name),
        "{}  import_role:".format(base_indentation),
        "{}    name: setup_image".format(base_indentation),
        "{}    defaults_from: \"{{{{ {} }}}}\".yml".format(base_indentation, "provider")]

    setup_image_role = group.get_role("setup_image")
    if setup_image_role and setup_image_role.variables:
        setup_image_group.append("{}  vars:".format(base_indentation))
        for key, value in setup_image_role.variables.iteritems():
            setup_image_group.append("{}    {}: {}".format(base_indentation, key, value))

    setup_image = "\n".join(setup_image_group)

    create_group_servers = [
        "{}- name: Create servers of group '{}'".format(base_indentation, group.name),
        "{}  import_role:".format(base_indentation),
        "{}    name: create_server".format(base_indentation),
        "{}    defaults_from: \"{{{{ {} }}}}\".yml".format(base_indentation, "provider")]

    create_server_role = group.get_role("create_server")

    if create_server_role and create_server_role.variables:
        create_group_servers.append("{}  vars:".format(base_indentation))
        for key, value in create_server_role.variables.iteritems():
            create_group_servers.append("{}    {}: {}".format(base_indentation, key, value))


    create_group_servers.append(
    "{}  with_items:".format(base_indentation))

    for i in xrange(0, group.servers, 1):
        create_group_servers.append(
        "{}    - {}".format(base_indentation, group.get_server_name(i+1)))

    create_group_servers.append("{}  loop_control:".format(base_indentation))
    create_group_servers.append("{}    loop_var: server".format(base_indentation))
    create_group_servers.append("")

    create_group = "\n".join(create_group_servers)

    return "{}\n\n{}".format(setup_image, create_group)

def gen_group_wait_for(group):
    wait_for = [
    "# Wait play",
    "- hosts: {}".format(group.name),
    "  gather_facts: no",
    "  remote_user: {}".format("TESTE"),
    "",
    "  tasks:",
    "    - name: Wait for '{}' instances to become reachable over WinRM".format(group.name),
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

            if role.variables:
                playbook.append("      vars:")
                for key, value in role.variables.iteritems():
                    playbook.append("        - {}: {}".format(key, value))

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
