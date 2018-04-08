import os
import sys
import yaml
import pytest
from maestro.input import read_roles, read_groups
from maestro.playbooks import gen_concerto


orchestra = \
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

groups = read_groups(yaml.safe_load(orchestra), dict(), None)

def test_gen_concerto_1():
    instruments = \
    """
    databases:
      create_server:
        image: cirros
        external_network: public
        flavor: m1.nano

    sql:
      create_server:
        image: cirros
        flavor: m1.medium
        username: l337


    """
    instruments_dict = yaml.safe_load(instruments)

    groups = read_roles(instruments_dict, groups)
    concerto = gen_concerto(boosted_groups, "openstack")

    print(concerto)
