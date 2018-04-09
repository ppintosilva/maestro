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

    databases:
      sql: 1
      other: 5

    generic:
        windows:
            xp: 5
            seven: 5

    computing: 7
    """

def test_gen_inventory():
    yaml_dict = yaml.safe_load(config)
    groups = read_groups(yaml_dict, dict(), None)

    inventory = gen_inventory(groups)

    assert inventory  == \
"""[windows-xp-001]
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

[webservers-nginx-001]

[webservers-shiny-001]

[databases-other-001]
[databases-other-002]
[databases-other-003]
[databases-other-004]
[databases-other-005]

[databases-sql-001]

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
databases-sql-001

[webservers.children]
nginx
shiny

[generic.children]
windows

[windows.children]
xp
seven"""
