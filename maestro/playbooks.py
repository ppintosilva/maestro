#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bananas
"""

from group import Group


"""
hello
"""
def gen_include_create_group(group):
    if group.servers == 0:
        return ""

    create_group_servers = [
    "- name: Create servers of group {}".format(group.name),
    "  include_role:",
    "    name: create_server"]

    if group.has_role("create_server"):
        create_group_servers.append(
            "    vars_from: group/{}_create_server.yml".format())

    create_group_servers.append(
    "  with_items:")

    for i in xrange(0, group.servers, 1):
        create_group_servers.append(
        "    - {}".format(group.get_server_name(i+1)))

    create_group_servers.append([
    "  loop_control:",
    "    loop_var: server",
    ""])

    return "\n".join(create_group_servers)

def gen_group_wait_for(group):
    wait_for = [
    "- hosts: {}}".format(group.name),
    "  gather_facts: no",
    "  tasks:",
    "    - meta: refresh_inventory",
    ""]
    return wait_for

###

def gen_concerto(groups, provider):
    concerto = [
    "# Play 1: Create all servers"
    "- hosts: localhost",
    "  gather_facts: no",
    "  vars:",
    "  provider: {}".format(provider),
    "",
    "  tasks:",
    "  - name: Retrieve list of existing server names",
    "    os_server_facts:",
    "    when: provider == openstack",
    ""]

    for group in groups.values():
        print(str(group))
        concerto.append(gen_include_create_group(group))
        concerto.append(gen_group_wait_for(group))

    return "\n".join(concerto)

###

def gen_all_groups_playbook(groups):
    intermezzo = []

    for_each_group_below(
        groups = get_roots(groups),
        method = lambda x: intermezzo.append(
            "- import_playbook: group/{}.yml".format(x.name)))

    return "\n\n".join(intermezzo)



# Group play:
# Only the leaf groups have a defined - unique playbook.
# The playbook for parent groups is to import the playbooks of
# its children. This avoids the case where variables for the same
# role might vary between children and the playbook for the parent
# would import variables for the
def gen_individual_playbooks(group):
    pass

def write_variables(group):
    for role in group.roles:
            role_vars_filename = role.get_vars_filename(group)
            with open(role_vars_filename, 'w') as role_vars_file:
                yaml.safe_dump(role.variables,
                               role_vars_file,
                               default_flow_style=False)
