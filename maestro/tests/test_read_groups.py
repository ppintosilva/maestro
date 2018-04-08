import os
import sys
import yaml
import pytest
from maestro.input import read_groups


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
        groups = read_groups(yaml_dict, dict(), None)


def test_valid_number_of_servers_in_child_groups():
    config = \
    """
    webservers:
      shiny: 1
      nginx: 1
      apache: 1
    """

    yaml_dict = yaml.safe_load(config)

    groups = read_groups(yaml_dict, dict(), None)

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

    groups = read_groups(yaml_dict, dict(), None)

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

    groups = read_groups(yaml_dict, dict(), None)

    assert groups["webservers"].servers == 2
    assert groups["databases"].servers == 5
    assert groups["computing"].servers == 7
    assert groups["windows"].servers == 5
    assert groups["generic"].servers == 5
