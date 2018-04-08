import os
import sys
import yaml
import pytest
from maestro.input import read_roles, read_groups

groups = \
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

groups = read_groups(yaml.safe_load(groups), dict(), None)

###

def test_non_existing_group_name():
    config = \
    """
    webservers:
    databases:
    jerome:
    """

    yaml_dict = yaml.safe_load(config)

    with pytest.raises(ValueError):
        read_roles(yaml_dict, groups)

###

def test_bad_definition_of_role_variables():
    config = \
    """
    webservers:
    databases:
    jerome:
        - docker:
            - A
            - B
            - C
    """

    yaml_dict = yaml.safe_load(config)

    with pytest.raises(ValueError):
        read_roles(yaml_dict, groups)

###

def test_bad_definition_of_role():
    config = \
    """
    webservers:
    databases:
    jerome: 3

    """

    yaml_dict = yaml.safe_load(config)

    with pytest.raises(ValueError):
        read_roles(yaml_dict, groups)

###

def test_bad_definition_of_role_using_list_level_1():
    config = \
    """
    webservers:
    databases:
    jerome:
      - docker
      - derp

    """

    yaml_dict = yaml.safe_load(config)

    with pytest.raises(ValueError):
        read_roles(yaml_dict, groups)

###

def test_bad_definition_of_role_using_list_level_2():
    config = \
    """
    webservers:
    databases:
    jerome:
      docker:
        - var1: "a"
        - var2: "b"

    """

    yaml_dict = yaml.safe_load(config)

    with pytest.raises(ValueError):
        read_roles(yaml_dict, groups)

###

def test_list_of_roles():
    config = \
    """
    webservers:
    databases:
      docker:
        var1: 1
        var2: "2"
      mysql:
        var1: "A"
        var2: "B"
      mongo:

    windows:
      docker:
        var1: 1
        var2: "2"
      office:
        var1: "A"
        var2: "B"
      samba:

    computing:
      spark:
      sperk:
      spirk:
      spork:
      spurk:
    """

    yaml_dict = yaml.safe_load(config)
    boosted_groups = read_roles(yaml_dict, groups)

    assert len(boosted_groups["generic"].roles) == 0
    assert len(boosted_groups["webservers"].roles) == 0
    assert len(boosted_groups["databases"].roles) == 3
    assert len(boosted_groups["windows"].roles) == 3
    assert len(boosted_groups["computing"].roles) == 5

    assert (
        sorted(map(lambda x: x.name, boosted_groups["computing"].roles))
        ==
        ["spark", "sperk", "spirk", "spork", "spurk"])

    assert (
        sorted(map(lambda x: x.name, boosted_groups["databases"].roles))
        ==
        ["docker", "mongo", "mysql"])

    varnames = ['var1', 'var2']

    assert boosted_groups["databases"].get_role("docker").variables.keys() == varnames

    assert boosted_groups["databases"].get_role("mysql").variables.keys() == varnames

    assert boosted_groups["databases"].get_role("mongo").variables ==  None

    assert boosted_groups["windows"].get_role("docker").variables.keys() == varnames

    assert boosted_groups["windows"].get_role("office").variables.keys() == varnames

    assert boosted_groups["windows"].get_role("samba").variables ==  None


def test_list_role_inheritance():
    pass
