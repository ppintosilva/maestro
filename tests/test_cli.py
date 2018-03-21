import os
import sys
import click
import pytest
from click.testing import CliRunner

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
