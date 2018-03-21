import os
import sys
import yaml
import pytest

# I don't like this but...
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import maestro


########################################################################
##
########################################################################
#                        TESTS ########################################################################
##
########################################################################

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

groups = maestro.read_groups(yaml.safe_load(groups), dict(), None)

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
        maestro.read_roles(yaml_dict, groups)

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
        maestro.read_roles(yaml_dict, groups)

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
        maestro.read_roles(yaml_dict, groups)

###

def test_list_of_roles():
    config = \
    """
    webservers:
    databases:
        - docker:
            - var1: 1
            - var2: "2"
        - mysql:
            var1: "A"
            var2: "B"
        - mongo

    windows:
        docker:
            - var1: 1
            - var2: "2"
        office:
            var1: "A"
            var2: "B"
        samba:

    computing:
        - spark
        - sperk
        - spirk
        - spork
        - spurk
    """

    yaml_dict = yaml.safe_load(config)
    boosted_groups = maestro.read_roles(yaml_dict, groups)

    # for k,v in boosted_groups.iteritems():
    #     print(k)
    #     for role in v.roles:
    #         print(role)

    assert len(boosted_groups["generic"].roles) == 0
    assert len(boosted_groups["webservers"].roles) == 0
    assert len(boosted_groups["databases"].roles) == 3
    assert len(boosted_groups["windows"].roles) == 3
    assert len(boosted_groups["computing"].roles) == 5

    assert (
        map(lambda x: x.name, boosted_groups["computing"].roles)
        ==
        ["spark", "sperk", "spirk", "spork", "spurk"])

    assert (
        map(lambda x: x.name, boosted_groups["databases"].roles)
        ==
        ["docker", "mysql", "mongo"])

    varnames = ['var1', 'var2']

    assert boosted_groups["databases"].roles[0].variables.keys() == varnames
    assert boosted_groups["databases"].roles[1].variables.keys() == varnames
    assert boosted_groups["windows"].roles[0].variables.keys() == varnames
    assert boosted_groups["windows"].roles[2].variables.keys() == varnames
