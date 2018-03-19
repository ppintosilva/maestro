import os
import sys
import inspect
import click
from click.testing import CliRunner
import pytest
import yaml

########################################################################
##
########################################################################
#                              NASTY HACK
########################################################################
##
########################################################################

# I don't like this but...
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import maestro

########################################################################
##
########################################################################
#                              CONTEXT
########################################################################
##
########################################################################

# Global click testing context object
runner = CliRunner()

########################################################################
##
########################################################################
#                              WRAPPER
########################################################################
##
########################################################################

@pytest.mark.skip(reason="Just a wrapper")
def run_function(groups_file = None, groups_text = None):
    return runner.invoke(
        maestro.genesis,
        ["--groups-file",
        groups_file,
        "--groups-text",
        groups_text],
        catch_exceptions = False)


########################################################################
##
########################################################################
#                        TESTS ########################################################################
##
########################################################################

def test_use_both_config_inputs():
    with pytest.raises(ValueError):
        run_function(groups_file = __file__,
                     groups_text = "ignore_this")


def test_use_none_of_two_config_inputs():
    with pytest.raises(ValueError):
        run_function(groups_file = None,
                     groups_text = None)


def test_use_non_integer_as_group_count():
    with pytest.raises(ValueError):
        run_function(groups_file = None,
                     groups_text = "Dummy: a")


def test_use_non_positive_integer_as_group_count():
    with pytest.raises(maestro.NonPositiveGroupError):
        run_function(groups_file = None,
                     groups_text = "Dummy: 0")


def test_duplicate_group_name():
    config = \
    """
    webservers:
      shiny: 1
      nginx: 1
      apache: 1

    databases:
        apache: 1
    """

    yaml_dict = yaml.safe_load(config)

    with pytest.raises(ValueError):
        groups = maestro.read_groups(yaml_dict, dict(), None)


def test_valid_number_of_servers_in_child_groups():
    config = \
    """
    webservers:
      shiny: 1
      nginx: 1
      apache: 1
    """

    yaml_dict = yaml.safe_load(config)

    groups = maestro.read_groups(yaml_dict, dict(), None)

    assert "webservers" in groups
    assert "shiny" in groups
    assert "nginx" in groups
    assert "apache" in groups
    assert groups["shiny"].parent == groups["webservers"]
    assert groups["nginx"].parent == groups["webservers"]
    assert groups["apache"].parent == groups["webservers"]
    assert groups["webservers"].isRoot()
    assert not groups["shiny"].isRoot()
    assert not groups["nginx"].isRoot()
    assert not groups["apache"].isRoot()
    assert not groups["webservers"].isLeaf()
    assert groups["shiny"].isLeaf()
    assert groups["nginx"].isLeaf()
    assert groups["apache"].isLeaf()
    assert groups["shiny"].servers == 1
    assert groups["nginx"].servers == 1
    assert groups["apache"].servers == 1
    assert groups["webservers"].servers == 0
    assert len(groups["shiny"].children) == 0
    assert len(groups["nginx"].children) == 0
    assert len(groups["apache"].children) == 0
    assert len(groups["webservers"].children) == 3


def test_use_of_other_simple():
    config = \
    """
    webservers:
      shiny: 1
      nginx: 1
      other: 1
    """

    yaml_dict = yaml.safe_load(config)

    groups = maestro.read_groups(yaml_dict, dict(), None)

    assert groups["webservers"].servers == 1
    assert groups["shiny"].servers == 1
    assert groups["nginx"].servers == 1

#---
#---
#---

config_complex = \
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

    yaml_dict = yaml.safe_load(config_complex)

    groups = maestro.read_groups(yaml_dict, dict(), None)

    assert groups["webservers"].servers == 2
    assert groups["databases"].servers == 5
    assert groups["computing"].servers == 7
    assert groups["windows"].servers == 5
    assert groups["generic"].servers == 5


def test_for_each_group_above():
    # Order of elements is not kept
    yaml_dict = yaml.safe_load(config_complex)
    groups = maestro.read_groups(yaml_dict, dict(), None)

    roots = maestro.get_roots(groups)

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

    maestro.for_each_group_below(
        groups = roots,
        method = lambda x:
            names.append(x.name)
            if x.isRoot()
            else
            names.append(x.parent.name))

    assert expected_names == names


def test_for_each_group_below():
    # Order of elements is not kept
    yaml_dict = yaml.safe_load(config_complex)
    groups = maestro.read_groups(yaml_dict, dict(), None)

    leaves = maestro.get_leaves(groups)

    assert len(leaves) == 6

    # Need to sort alphabetically
    leaves.sort(key = lambda x: x.name)

    # In this case, parents with multiple leaves will execute once once per each children. This is not a bug, but intended. The objective of the function is not to execute once and only once on each node, but for a given node, execute upwards or downwards (at least for now).

    expected_names = [
        "computing", # computing leaf
        "webservers", # nginx leaf
        "webservers", # webserver
        "windows", # seven leaf
        "generic", # windows
        "generic", # generic
        "webservers", # shiny leaf
        "webservers", # webservers
        "databases", # sql leaf
        "databases", # databases
        "windows", # xp leaf
        "generic", # windows
        "generic"] # generic

    names = []

    maestro.for_each_group_above(
        groups = leaves,
        method = lambda x:
            names.append(x.name)
            if x.isRoot()
            else
            names.append(x.parent.name))

    assert expected_names == names


def test_gen_inventory():
    yaml_dict = yaml.safe_load(config_complex)
    groups = maestro.read_groups(yaml_dict, dict(), None)

    roots = maestro.get_roots(groups)

    inventory = maestro.gen_inventory(roots)    

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
