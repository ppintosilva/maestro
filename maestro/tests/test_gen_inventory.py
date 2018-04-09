import os
import sys
import yaml
import pytest
from maestro.input import read_groups
from maestro.inventory import gen_inventory
from maestro.group import get_roots, for_each_group_below, get_leaves, for_each_group_above


config = \
    """
    databases:
      sql: 1
      neo4j-mongo: 1

    webservers: 2

    computing:
      spark: 7
      other: 1
    """

def test_gen_inventory():
    yaml_dict = yaml.safe_load(config)
    groups = read_groups(yaml_dict, dict(), None)

    inventory = gen_inventory(groups)

    assert inventory  == \
"""[databases-neo4j-mongo-001]

[neo4j-mongo.children]
databases-neo4j-mongo-001

[webservers-001]
[webservers-002]

[webservers.children]
webservers-001
webservers-002

[databases-sql-001]

[sql.children]
databases-sql-001

[computing-other-001]

[computing-other.children]
computing-other-001

[computing-spark-001]
[computing-spark-002]
[computing-spark-003]
[computing-spark-004]
[computing-spark-005]
[computing-spark-006]
[computing-spark-007]

[spark.children]
computing-spark-001
computing-spark-002
computing-spark-003
computing-spark-004
computing-spark-005
computing-spark-006
computing-spark-007

[computing.children]
spark
computing-other

[databases.children]
neo4j-mongo
sql

"""
