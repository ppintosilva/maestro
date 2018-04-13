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

docker_variables_webservers = {
    "username" : "JohnDoe",
    "secret" : "ola123"
}

docker_variables_shiny = {
    "secret" : "secret123"
}

spark_variables_spark = {
    "mode" : "performance"
}

spark_variables_compute = {
    "mode" : "classic",
    "context" : "local"
}

webservers.add_role("docker", docker_variables_webservers)
shiny.add_role("docker", docker_variables_shiny)

spark.add_role("spark", spark_variables_spark)
compute.add_role("spark", spark_variables_compute)


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

    assert databases.level == 1
    assert sql.level == 2
    assert neo4j.level == 2

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
    names = []

    for_each_group_below(
        group = databases,
        method = lambda x: names.append(x.name))

    names.sort()

    expected_names = [
        "databases",
        "neo4j",
        "sql"]

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
    assert webservers.has_role("docker")
    assert shiny.has_role("docker")

    assert spark.has_role("spark")
    assert compute.has_role("spark")

    assert len(databases.roles) == 0

    assert len(webservers.roles) == 1
    assert len(shiny.roles) == 1
    assert len(spark.roles) == 1
    assert len(compute.roles) == 1

def test_inheritance_webservers():
    assert nginx.has_role("docker")

    assert len(shiny.get_role("docker").variables.values()) == 2
    assert len(webservers.get_role("docker").variables.values()) == 2

    assert  nginx.get_role("docker").variables == \
            webservers.get_role("docker").variables

    assert  shiny.get_role("docker").variables != \
            webservers.get_role("docker").variables

    assert webservers.get_role("docker").variables["username"] == "JohnDoe"
    assert webservers.get_role("docker").variables["secret"] == "ola123"
    assert shiny.get_role("docker").variables["username"] == "JohnDoe"
    assert shiny.get_role("docker").variables["secret"] == "secret123"


def test_inheritance_compute():
    assert compute_other.has_role("spark")

    assert len(shiny.get_role("docker").variables.values()) == 2
    assert len(webservers.get_role("docker").variables.values()) == 2

    assert  compute_other.get_role("spark").variables == \
            compute.get_role("spark").variables

    assert  spark.get_role("spark").variables != \
            compute.get_role("spark").variables

    assert compute.get_role("spark").variables["mode"] == "classic"
    assert compute.get_role("spark").variables["context"] == "local"
    assert spark.get_role("spark").variables["mode"] == "performance"
    assert spark.get_role("spark").variables["context"] == "local"


def test_third_layer():
    hpc1 = Group("hpc1", 0, None)
    hpc2 = Group("hpc2", 0, hpc1)
    hpc3 = Group("hpc3", 2, hpc2)

    hpc1.add_role("test", {"var1" : "a", "var2" : "b"})

    assert len(hpc1.roles) == 1
    assert len(hpc2.roles) == 1
    assert len(hpc3.roles) == 1

    assert hpc1.get_role("test").priority == 1
    assert hpc2.get_role("test").priority == 1
    assert hpc3.get_role("test").priority == 1

    assert hpc3.get_role("test").variables == {"var1" : "a", "var2" : "b"}

    hpc2.add_role("test", {"var3" : "c", "var2" : "z"})

    assert hpc2.get_role("test").priority == 2
    assert hpc3.get_role("test").priority == 2

    assert hpc3.get_role("test").variables == {"var1" : "a", "var2" : "z", "var3" : "c"}

    hpc3.add_role("test", {"var1" : 1,
                           "var2" : 2,
                           "var3" : 3})

    assert hpc3.get_role("test").priority == 3

    assert hpc3.get_role("test").variables == {"var1" : 1, "var2" : 2, "var3" : 3}
