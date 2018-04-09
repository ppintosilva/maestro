import os
import sys
import yaml
import pytest
from maestro.group import *

# Tree 1
databases = Group("databases", 0, None)
sql = Group("sql", 1, databases)
neo4j = Group("neo4j", 2, databases)

# Tree 2
webservers = Group("webservers", 0, None)
shiny = Group("shiny", 3, webservers)
nginx = Group("nginx", 3, webservers)

# Tree 3
compute = Group("compute", 0, None)
spark = Group("spark", 5, compute)
compute_other = Group("compute-other", 5, compute)

groups = {
    "databases" : databases,
    "sql" : sql,
    "neo4j" : neo4j,
    "webservers" : webservers,
    "shiny" : shiny,
    "nginx" : nginx,
    "compute" : compute,
    "spark" : spark
}

# Roles



def test_valid_groups():
    assert databases.servers == 0
    assert sql.servers == 1
    assert neo4j.servers == 2

    assert sql.parent == databases
    assert neo4j.parent == databases
    assert sql in databases.children
    assert neo4j in databases.children

    assert webservers.servers == 0
    assert shiny.servers == 3
    assert nginx.servers == 3

    assert shiny.parent == webservers
    assert nginx.parent == webservers
    assert shiny in webservers.children
    assert nginx in webservers.children

    assert compute.servers == 0
    assert spark.servers == 5
    assert compute_other.servers == 5

    assert spark.parent == compute
    assert spark in compute.children
    assert compute_other in compute.children

def test_get_server_name():
    assert databases.get_server_name(1) == "databases-001"
    assert databases.get_server_name(2) == "databases-002"
    assert spark.get_server_name(1) == "compute-spark-001"

    assert compute_other.get_server_name(1) == "compute-other-001"

def test_get_leaves():
    leaves = get_leaves(groups)
    leaves.sort(key = lambda x: x.name)
    assert leaves  == [neo4j, nginx, shiny, spark, sql]

def test_get_roots():
    roots = get_roots(groups)
    roots.sort(key = lambda x: x.name)
    assert roots  == [compute, databases, webservers]

def test_for_each_group_below():
    roots = get_roots(groups)
    roots.sort(key = lambda x: x.name)

    names = []

    for_each_group_below(
        groups = roots,
        method = lambda x:
            names.append(x.name)
            if x.isRoot()
            else
            names.append(x.parent.name))

    expected_names = [
        "compute",
        "compute",
        "compute",
        "databases",
        "databases",
        "databases",
        "webservers",
        "webservers",
        "webservers"]

    assert names == expected_names


def test_for_each_group_above():
    names = []

    for_each_group_above(
        group = spark,
        method = lambda x:
            names.append(x.name)
            if x.isRoot()
            else
            names.append(x.parent.name))

    expected_names = [
        "compute",
        "compute"]

    assert expected_names == names

def test_add_role():
    pass

def test_role_inheritance():
    pass
