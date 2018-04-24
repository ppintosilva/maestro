import os
import sys
import yaml
import pytest
from maestro.input import read_roles, read_groups
from maestro.playbooks import gen_concerto, gen_individual_playbook, gen_all_groups_playbook


orchestra = \
"""
databases:
  sql: 1
  mongo: 1

computing: 7
"""

groups = read_groups(yaml.safe_load(orchestra))

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
  docker:

computing:
  docker:
    username: JorgeJesus
"""

groups = read_roles(yaml.safe_load(instruments), groups)

expected_databases_playbook = \
"""- include_playbook: mongo.yml

- include_playbook: sql.yml
"""

expected_sql_playbook = \
"""- hosts: sql
  gather_facts: yes
  remote_user: "{{ username }}"
  become: yes

  tasks:

    - name: Execute role 'docker'
      include_role:
        name: docker
"""

expected_mongo_playbook = \
"""- hosts: mongo
  gather_facts: yes
  remote_user: "{{ username }}"
  become: yes

  tasks:
"""

expected_computing_playbook = \
"""- hosts: computing
  gather_facts: yes
  remote_user: "{{ username }}"
  become: yes

  tasks:

    - name: Execute role 'docker'
      include_role:
        name: docker
      vars:
        username: JorgeJesus
"""

expected_intermezzo = \
"""- include_playbook: group/databases.yml

- include_playbook: group/computing.yml"""

expected_concerto = \
"""# Play 1: Create all servers
- hosts: localhost
  gather_facts: no
  vars:
    provider: openstack

  tasks:
    - name: Retrieve list of existing server names
      os_server_facts:
      when: provider == openstack

    - name: Setup image for servers of group 'computing'
      include_role:
        name: setup_image
        defaults_from: "{{ provider }}".yml

    - name: Create servers of group 'computing'
      include_role:
        name: create_server
        defaults_from: "{{ provider }}".yml
      with_items:
        - computing-001
        - computing-002
        - computing-003
        - computing-004
        - computing-005
        - computing-006
        - computing-007
      loop_control:
        loop_var: server

    - name: Setup image for servers of group 'mongo'
      include_role:
        name: setup_image
        defaults_from: "{{ provider }}".yml

    - name: Create servers of group 'mongo'
      include_role:
        name: create_server
        defaults_from: "{{ provider }}".yml
      vars:
        image: cirros
        external_network: public
        flavor: m1.nano
      with_items:
        - databases-mongo-001
      loop_control:
        loop_var: server

    - name: Setup image for servers of group 'sql'
      include_role:
        name: setup_image
        defaults_from: "{{ provider }}".yml

    - name: Create servers of group 'sql'
      include_role:
        name: create_server
        defaults_from: "{{ provider }}".yml
      vars:
        username: l337
        flavor: m1.medium
        image: cirros
        external_network: public
      with_items:
        - databases-sql-001
      loop_control:
        loop_var: server

    - name: Refresh in-memory openstack cache
      meta: refresh_inventory

# Wait play
- hosts: computing
  gather_facts: no
  remote_user: "{{ username }}"

  tasks:
    - name: Wait for 'computing' instances to become reachable over WinRM
      wait_for_connection:
        timeout: "{{ timeout_instance_boot }}"

# Wait play
- hosts: mongo
  gather_facts: no
  remote_user: "{{ username }}"

  tasks:
    - name: Wait for 'mongo' instances to become reachable over WinRM
      wait_for_connection:
        timeout: "{{ timeout_instance_boot }}"

# Wait play
- hosts: sql
  gather_facts: no
  remote_user: "{{ username }}"

  tasks:
    - name: Wait for 'sql' instances to become reachable over WinRM
      wait_for_connection:
        timeout: "{{ timeout_instance_boot }}"

"""

def test_gen_individual_playbook():

    databases_playbook = gen_individual_playbook(groups["databases"])
    sql_playbook = gen_individual_playbook(groups["sql"])
    mongo_playbook = gen_individual_playbook(groups["mongo"])
    computing_playbook = gen_individual_playbook(groups["computing"])

    assert databases_playbook == expected_databases_playbook
    assert sql_playbook == expected_sql_playbook
    assert mongo_playbook == expected_mongo_playbook
    assert computing_playbook == expected_computing_playbook

def test_gen_intermezzo():
    intermezzo = gen_all_groups_playbook(groups)
    assert intermezzo == expected_intermezzo

def test_gen_concerto():
    concerto = gen_concerto(groups, "openstack")
    assert concerto == expected_concerto
