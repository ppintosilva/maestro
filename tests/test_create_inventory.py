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

    print groups

    assert groups["webservers"].servers == 1
    assert groups["shiny"].servers == 1
    assert groups["nginx"].servers == 1

def test_use_of_other_complex():
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

    yaml_dict = yaml.safe_load(config)

    groups = maestro.read_groups(yaml_dict, dict(), None)

    print groups

    assert groups["webservers"].servers == 2
    assert groups["databases"].servers == 5
    assert groups["computing"].servers == 7
    assert groups["windows"].servers == 5
    assert groups["generic"].servers == 5



#
# # Case fails 2:
# def test_create_inventory_fail_2():
#     config = \
#     """
#     servers: 0
#     """
#     with pytest.raises(maestro.NonPositiveGroupError) as e2:
#         maestro.create_inventory(config = config)
#         assert e2.group == "servers"
#
#
# # Case fails 3: No more than 5 levels of hierarchy allowed
# def test_create_inventory_fail_3():
#     config = \
#     """
#     openstack:
#       dbs:
#         notsql:
#           mongo:
#             child:
#               fake: 1
#     """
#     with pytest.raises(maestro.TooManyLevelsError) as e3:
#         maestro.create_inventory(config = config)
#         assert e3.rootgroup == "openstack"
