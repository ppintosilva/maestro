import os
import sys
import inspect
import click
from click.testing import CliRunner
import pytest

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

# def test_valid_number_of_servers_in_child_groups():
#     config = \
#     """
#     webservers:
#       shiny: 1
#       nginx: 1
#       apache: 1
#     """
#
#     yaml_dict = yaml.safe_load(config)
#
#     groups = maestro.read_groups(yaml_dict)[0]
#
#     assert "webservers" in groups
#     assert "shiny" in groups
#     assert "nginx" in groups
#     assert "apache" in groups
#     assert  in groups

#
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
