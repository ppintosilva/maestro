import os
import sys
import inspect
import pytest

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import maestro

# Test create_inventory function
#
#

# Case pass 1:
def test_create_inventory_success_1():
    config = \
    """
    dbs: 2

    compute: 8
      spark: 4

    webservers:
      shiny: 1
      nginx: 1
    """
    expected_inventory = \
    """
    """

    actual_inventory = maestro.create_inventory(config = config)

    assert expected_inventory == actual_inventory

# Case pass 2:
def test_create_inventory_success_2():
    config = \
    """
    servers: 2
      shiny: 1
      nginx: 1
    """
    expected_inventory = \
    """
    """

    actual_inventory = maestro.create_inventory(config = config)

    assert expected_inventory == actual_inventory

# Case pass 3:
def test_create_inventory_fail_3():
    config = \
    """
    openstack-my-cluster:
      dbs:
        sql: 1
        notsql: 1

    openstack-his-cluster:
      web:
        apache: 1
    """
    expected_inventory = \
    """
    """

    actual_inventory = maestro.create_inventory(config = config)

    assert expected_inventory == actual_inventory

# Case fails 0:
def test_create_inventory_fail_0a:
    with pytest.raises(ValueError) as e0a:
        maestro.create_inventory(
            config_file = __file__,
            config = " ignore this")

def test_create_inventory_fail_0a:
    with pytest.raises(ValueError) as e0b:
        maestro.create_inventory()

def test_create_inventory_fail_0c:
    with pytest.raises(ValueError) as e1:
        maestro.create_inventory(config = "Dummy: a")

# Case fails 1:
def test_create_inventory_fail_1():
    config = \
    """
    servers: 3
      shiny: 1
      nginx: 1
    """

    with pytest.raises(maestro.ParentGroupSumError) as e1:
        maestro.create_inventory(config = config)
        assert e1.parentgroup == "servers"


# Case fails 2:
def test_create_inventory_fail_2():
    config = \
    """
    servers: 0
    """
    with pytest.raises(maestro.NonPositiveGroupError) as e2:
        maestro.create_inventory(config = config)
        assert e2.group == "servers"


# Case fails 3: No more than 5 levels of hierarchy allowed
def test_create_inventory_fail_3():
    config = \
    """
    openstack:
      dbs:
        notsql:
          mongo:
            child:
              fake: 1
    """
    with pytest.raises(maestro.TooManyLevelsError) as e3:
        maestro.create_inventory(config = config)
        assert e3.rootgroup == "openstack"
