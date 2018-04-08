import os
import sys
import yaml
import pytest
from maestro.input import read_groups
from maestro.inventory import gen_inventory
from maestro.group import get_roots, for_each_group_below, get_leaves, for_each_group_above


config = \
    """
    webservers:
      shiny: 1
      nginx: 1
      other: 2

    databases:
      sql: 1
      other: 5

    generic:
        other: 5
        windows:
            xp: 5
            seven: 5
            other: 5

    computing:
      other: 7
    """

def test_use_of_other_complex():

    yaml_dict = yaml.safe_load(config)

    groups = read_groups(yaml_dict, dict(), None)

    assert groups["webservers"].servers == 2
    assert groups["databases"].servers == 5
    assert groups["computing"].servers == 7
    assert groups["windows"].servers == 5
    assert groups["generic"].servers == 5


def test_for_each_group_above():
    # Order of elements is not kept
    yaml_dict = yaml.safe_load(config)
    groups = read_groups(yaml_dict, dict(), None)

    roots = get_roots(groups)

    assert len(roots) == 4

    # Need to sort alphabetically
    roots.sort(key = lambda x: x.name)

    # As the order of elements when yaml.safe_load is called
    # is not kept, we can't do this
    # expected_names = ["computing",
    #                   "databases",
    #                   "sql",
    #                   "generic",
    #                   "windows",
    #                   "xp",
    #                   "seven",
    #                   "webservers",
    #                   "shiny",
    #                   "nginx"]
    expected_names = [
        "computing",
        "databases",
        "databases",
        "generic",
        "generic",
        "windows",
        "windows",
        "webservers",
        "webservers",
        "webservers"]

    names = []

    for_each_group_below(
        groups = roots,
        method = lambda x:
            names.append(x.name)
            if x.isRoot()
            else
            names.append(x.parent.name))

    assert expected_names == names


def test_for_each_group_below():
    # Order of elements is not kept
    yaml_dict = yaml.safe_load(config)
    groups = read_groups(yaml_dict, dict(), None)

    leaves = get_leaves(groups)

    assert len(leaves) == 6

    # Need to sort alphabetically
    leaves.sort(key = lambda x: x.name)

    # In this case, parents with multiple leaves will execute once once per each children. This is not a bug, but intended. The objective of the function is not to execute once and only once on each node, but for a given node, execute upwards or downwards (at least for now).

    expected_names = [
        "computing", # computing leaf
        # ---
        "webservers", # nginx leaf
        "webservers", # webserver
        # --
        "windows", # seven leaf
        "generic", # windows
        "generic", # generic
        # ---
        "webservers", # shiny leaf
        "webservers", # webservers
        # ---
        "databases", # sql leaf
        "databases", # databases
        # ---
        "windows", # xp leaf
        "generic", # windows
        "generic"] # generic

    names_0 = []
    names_1 = []
    names_2 = []
    names_3 = []
    names_4 = []
    names_5 = []

    for_each_group_above(
        group = leaves[0], # computing
        method = lambda x:
            names_0.append(x.name)
            if x.isRoot()
            else
            names_0.append(x.parent.name))

    assert expected_names[0:1] == names_0

    
    for_each_group_above(
        group = leaves[1], # nginx
        method = lambda x:
            names_1.append(x.name)
            if x.isRoot()
            else
            names_1.append(x.parent.name))

    assert expected_names[1:3] == names_1

    for_each_group_above(
        group = leaves[2], # seven
        method = lambda x:
            names_2.append(x.name)
            if x.isRoot()
            else
            names_2.append(x.parent.name))

    assert expected_names[3:6] == names_2

    for_each_group_above(
        group = leaves[3], # shiny
        method = lambda x:
            names_3.append(x.name)
            if x.isRoot()
            else
            names_3.append(x.parent.name))

    assert expected_names[6:8] == names_3

    for_each_group_above(
        group = leaves[4], # sql
        method = lambda x:
            names_4.append(x.name)
            if x.isRoot()
            else
            names_4.append(x.parent.name))

    assert expected_names[8:10] == names_4

    for_each_group_above(
        group = leaves[5], # xp
        method = lambda x:
            names_5.append(x.name)
            if x.isRoot()
            else
            names_5.append(x.parent.name))

    assert expected_names[10:13] == names_5


def test_gen_inventory():
    yaml_dict = yaml.safe_load(config)
    groups = read_groups(yaml_dict, dict(), None)

    roots = get_roots(groups)

    inventory = gen_inventory(roots)

    assert inventory  == \
"""[generic-001]
[generic-002]
[generic-003]
[generic-004]
[generic-005]

[generic-windows-001]
[generic-windows-002]
[generic-windows-003]
[generic-windows-004]
[generic-windows-005]

[windows-xp-001]
[windows-xp-002]
[windows-xp-003]
[windows-xp-004]
[windows-xp-005]

[windows-seven-001]
[windows-seven-002]
[windows-seven-003]
[windows-seven-004]
[windows-seven-005]

[computing-001]
[computing-002]
[computing-003]
[computing-004]
[computing-005]
[computing-006]
[computing-007]

[webservers-001]
[webservers-002]

[webservers-nginx-001]

[webservers-shiny-001]

[databases-001]
[databases-002]
[databases-003]
[databases-004]
[databases-005]

[databases-sql-001]

[generic.children]
generic-001
generic-002
generic-003
generic-004
generic-005

[windows.children]
generic-windows-001
generic-windows-002
generic-windows-003
generic-windows-004
generic-windows-005

[xp.children]
windows-xp-001
windows-xp-002
windows-xp-003
windows-xp-004
windows-xp-005

[seven.children]
windows-seven-001
windows-seven-002
windows-seven-003
windows-seven-004
windows-seven-005

[computing.children]
computing-001
computing-002
computing-003
computing-004
computing-005
computing-006
computing-007

[webservers.children]
webservers-001
webservers-002

[nginx.children]
webservers-nginx-001

[shiny.children]
webservers-shiny-001

[databases.children]
databases-001
databases-002
databases-003
databases-004
databases-005

[sql.children]
databases-sql-001"""
