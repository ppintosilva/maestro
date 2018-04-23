#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bananas
"""

from group import Group, get_names, get_roots

"""
Returns a dictionary in the form:
    name , group

This is useful when you need to run code that doesn't care about
the tree-like structure of the groups (i.e. for all groups).

However, when you care about the structure of the groups,
(for instance, when generating the inventory: groups are written to the
file in a depth-first format) then only the list of root or leaf nodes
is necessary. Then the tree is transversed in the most appropriate manner
to the case: breadth-first, depth-first, top-to-bottom, bottom-to-top, etc.
"""
def read_groups(dic, groups = dict(), parent = None):

    for name, value in dic.iteritems():

        name = name.lower()
        group = Group(name, 0, parent)

        # If I'm not a leaf group then read my child groups
        if isinstance(value, dict):
            if name == "other":
                raise ValueError("Non-leaf groups named 'other' are not allowed.")

            groups = read_groups(value, groups, parent = group)

        # Else if I'm a leaf node
        elif isinstance(value, int):
            # Read number of servers
            if value > 0:
                group.servers = value
            else:
                raise ValueError("Group {} must have size greater than 0".format(group.name))

            # Wait.. I'm not really a group..
            if name == "other":
                if group.isRoot():
                    raise ValueError("Root groups named 'other' are not allowed.")
                else:
                    # Deslike this, need to think about better solution..
                    group.name = "{}-{}".format(parent.name, "other")

        else:
            raise ValueError(
                    "Each group should be either an integer or a new group. Leaf groups should be in the form: \"group_name: nservers\" ")

        if group.name in groups:
            raise ValueError(
                    "{}: Names of root groups and groups within each tree should be unique.".format(name))
        groups[group.name] = group

    return groups


"""
Read instruments.yml as roles.
"""
def read_roles(dic, groups):

    group_names = get_names(groups)

    for group_name, roles in dic.iteritems():
        group_name = group_name.lower()

        if group_name == "all":
            roots = get_roots(groups)

        elif group_name not in group_names:
            raise ValueError("Group named '{}' does not exist in groups: it was not provided in groups_file or groups_text.".format(group_name))
        else:
            group = groups[group_name]

        # A single role as a string with no variables defined
        if isinstance(roles, str):
            group.add_role(roles, None, group.level)

        # A dictionary of roles
        elif isinstance(roles, dict):

            for role_name, raw_variables in roles.iteritems():
                variables = read_variables(raw_variables)
                if group_name == "all":
                    map(lambda x: x.add_role(role_name, variables, 0),
                        roots)
                else:
                    group.add_role(role_name, variables, group.level)

        # No roles
        elif roles is None:
            pass

        else:
            raise ValueError("Group '{}' should be followed by a role (string, dictionary).".format(group_name))

    return groups

"""
Return the variables for a role
"""
def read_variables(raw_variables):
    # Either a dictionary or none
    if isinstance(raw_variables, dict):
        """
        Here, I won't be checking if the elements of variables are not dictionaries or lists. I guess it's up to the user to be sensible
        at this point, unless the objective is to break the software.
        """
        variables = raw_variables

    elif raw_variables is None:
        variables = None

    else:
        raise ValueError("One or more variables are not well defined (expecting a dictionary or None)".format())

    return variables
