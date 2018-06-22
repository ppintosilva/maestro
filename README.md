# maestro
Orchestrate groups of software-ready instances on the cloud

[//]: # (<div style="text-align:center">)

<img src="maestro.svg" alt="maestro_icon" width="200px">

---

## TL;DR

**Base Requirements**: python2.7, virtualenv, access to the cloud (authentication + networking)

**Installation**: `make install`

**Usage**:

1. `python maestro.py orchestra.yml instruments.yml`
2. `ansible-playbook -i inventory playbooks/concerto.yml`
3. (wait for servers to boot)
4. `ansible-playbook -i inventory playbooks/intermezzo.yml`

**What is happening?**

1. Generates ansible playbooks
2. Creates the servers (virtual machines) on the cloud
3. Waiting...
4. Installs/Runs stuff on the servers

**Supported cloud providers**: only *openstack* at the moment, but it's easy to extend support to other [cloud providers](#contributing).

---

# Contents
1. [What is maestro](#introduction)
2. [Why maestro](#motivation-maestro)
3. [Why ansible](#motivation-ansible)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Beyond the basics](#advanced)
7. [Troubleshooting](#troubleshooting)
8. [Contributing](#contributing)
9. [License](#license)

## What is `maestro` <a name="introduction"></a>

In short, **maestro** is a wrapper for ansible. It generates an inventory file and several playbooks from a description of the cluster, which is given by two input files:

1. **Orchestra** - lists groups: name of group, number of servers per group, and the hierarchy between groups (parents, children).

2. **Instruments** - lists ansible-roles to be executed by each group **(optional)**.

The output playbooks generated by **maestro** have two different purposes:

- Create the groups of servers on the cloud

- Install and configure software (ansible roles) for one or several groups

With the generated ansible files you can now get your cluster up and running with the necessary software, faster than before, without having to write the playbook and inventory files yourself.

## Why `maestro` <a name="motivation-maestro"></a>

### When disaster strikes

Your very own first cluster. Maybe it was born out of necessity, maybe you were just curious, maybe you were bored or your boss told you to. Regardless of why and when it happened, it was probably a painful (but rewarding) experience. If the why was important however, watching it crumble and disappear into oblivion might have been an even more painful experience. Independently of whose fault that was (`insert scapegoat's name here`), you probably had to do it all over again. And then you might have realised that you don't remember exactly how you did it and which particular piece of software was installed in this machine or that machine. If only there was a magic redo button. Hopefully **maestro** is a step forward in that direction.

### Reproducible Cluster

There is no doubt that *Reproducible Research* is a good thing. However, when it's unfeasible to execute your, or someone else's, research pipeline on a single computer, there is an extra set of dependencies that adds up on top of existing ones (data and software dependencies). These are dependencies on computing resources: processing power, storage, networking. Whether you like it or not, you may need to spin up a cluster of cloud instances, or use an existing one, to run those reproducible experiments. Having an easy way to describe and re-create the computing resources necessary to run an experiment may come a long way in facilitating *Reproducible Research*.

### *Because it's faster*

But if the reasons above are not sufficient to use **maestro**, or the underlying orchestration tools (ansible), then *because it's faster* should be a good enough reason. These and similar tools (e.g. puppet, chef, juju, saltstack) enable you to get a cluster up and running much quicker than you would otherwise.

## Why `ansible` <a name="motivation-ansible"></a>

### Group it to win it

Software systems can be structured in a number of different ways. To reduce complexity we often apply principles such as separation of concerns and create notable architectural patterns. When your system is relatively small, or in development stages, it may be ok to run all of its components on a single machine. However, when your system is deployed on the cloud, or needs to scale across several machines, it's not uncommon to have one or more servers dedicated to handling each component individually. One definitely very common setup is to split your servers into several groups:

- **Databases** - they store your data (e.g. MySql, MongoDB, Neo4j, Cassandra)
- **Computing** - they handle business logic, run your analytics/research pipeline, make pancakes (e.g. hadoop/spark cluster, your hello world program)
- **Webservers** - they expose your website, results, work to the world or company (e.g. apache, nginx, shiny)

And these groups have quite distinct software dependencies. For example, modern database systems use client-server models to decouple the components necessary to run the database daemon, from the ones necessary to query and interact with the database. *Database* servers can therefore install server-side libraries, whilst *Computing* and *Webservers* only need much lighter client-side libraries in order to interact with the database.

I find that ansible makes it easier to address servers by functionality. The inventory file lists servers and defines hierarchies among groups. This feature is extremely useful and feels natural when setting up or managing your cluster(s). You may choose to have one or more servers per group. To have servers belong to several groups. To have groups within other groups. Or choose not to. It's up to you.

### In a Galaxy not that far away

[Ansible Galaxy](https://galaxy.ansible.com/) is one of the best things about ansible. You can easily reuse content developed and thoroughly tested by other users. In addition to ansible's extensive list of native modules, Ansible Galaxy provides access to a whole new set of ansible roles for installing, configuring and deploying all kinds of software. Building **maestro** on top of ansible means that you get all the benefits of Ansible Galaxy.

### To learn or not to learn `ansible`

But why do I need **maestro**? Why don't I just learn and use ansible directly then? Or a different orchestration tool for that matter? You should learn ansible. And you're using ansible when working with **maestro**. What I noticed when using ansible is that a lot of playbooks end up with similar structure. I worked out how to replicate this structure automatically to avoid brainless copy-pasting. What **maestro** does is to generate the files necessary to let ansible setup your cluster. User input is still necessary, but you don't have to write the ansible playbooks or the hosts inventory file yourself. So, you don't have to know ansible to the same extent that an experienced user has in order to use **maestro** and setup your cluster on the cloud. In fact, knowing ansible is not a requirement for basic usage (and I've tried to make it that way as much as possible). However, it certainty helps that you know or at least understand the main concepts behind ansible. When you start writing your own roles, learning ansible will become inevitable. At the end of the day, **maestro** is just a wrapper for ansible. Hopefully, a useful one.

## Installation <a name="installation"></a>

**maestro** is implemented and tested only in python2.7.
Installing **maestro** should be pretty straightforward whether you use the Makefile or not.

**Not** using the `Makefile`:

0. Install python2.7 and virtualenv
1. Create virtualenv:
```
python2.7 -m virtualenv ENV
```
2. Install required python modules:
```
pip install -r requirements.txt
```
3. (optional) Install recommended ansible galaxy roles - a list which you can extend:
```
ansible-galaxy install -r supplementary-roles.yml
```

And if you're using the `Makefile` instead, all you need to do is `make install`. And that's it really. To be honest the makefile doesn't automate much here, but it can be useful nonetheless. Beware however that the makefile runs all of the steps above: 1 through 3 and hence creates the virtualenv and install the supplementary ansible roles for you.


## Usage <a name="usage"></a>

Everytime you use **maestro** don't forget first to:

1. Activate your virtualenv: 'source VIRTUALENV/bin/activate'
2. Set cloud provider's environment variables. In openstack this is done by sourcing the [RC file](https://docs.openstack.org/newton/install-guide-rdo/keystone-openrc.html).

**maestro** is typically used in the following fashion:

<img src="workflow.svg" alt="workflow_image" width="800px">

This means that you don't have to know a priori what your cluster looks like, that is, number of groups and number of servers per group. You can modify the description of your cluster as you go along and gain a better understanding of the requirements of your application. All you have to do is re-run `maestro.py` and the following steps if necessary. Ansible is great to guarantee the idempotency of operations and I've tried to enforce this. As an example, if you try to create a server on the cloud that already exists (matches by name) then the playbook simply skips that tasks.

Below is a list of the files that you are more likely to interact with when using maestro:

| Filename                    | Type              | Description |
| --------                    | ------------      | ----------- |
| maestro.py                  | Python Executable | Main executable - Generates Output files given Input files |
| orchestra.yml               | Input - Yaml      | Description of groups |
| instruments.yml             | Input - Yaml      | Description of roles and variables per group |
| inventory/hosts             | Output - INI      | Ansible inventory file - list of groups |
| playbooks/concerto.yml      | Output - Playbook | Playbook for booting servers on the cloud |
| playbooks/group/*           | Output - Playbook | Individual group playbooks |
| playbooks/intermezzo.yml    | Output - Playbook | Playbook for all groups |
| group_vars/*                | Output - Yaml     | Individual group variables |
| playbooks/create-server.yml | Playbook          | (EXTRA) Static playbook for creating a single server |
| playbooks/setup-image.yml   | Playbook          | (EXTRA) Static playbook for setting up a cloud image |
| inventory/openstack.py      | Python Executable | Dynamic inventory file provided by ansible for Openstack |
| maestro/*                   | Python files      | Source code and tests for *maestro.py* |

Let's look at some of these in more detail.

### `maestro.py`

```
Usage: maestro.py [OPTIONS] ORCHESTRA [INSTRUMENTS]

  ORCHESTRA is a yaml file which lists the names and number of servers of
  each group and their children.

  INSTRUMENTS is a yaml file which lists the roles and variables of each
  group of servers.

  STAGE is the name of the cloud provider, one of: {'openstack'}

Options:
  --stage [openstack]  Name of target cloud provider
  --username TEXT      Default value of ansible_ssh_user. The username for the
                       host machines.
  --help               Show this message and exit.
```

Example:

```
python maestro.py \
    --stage openstack \
    --username geronimo \
    orchestra.yml \
    instruments.yml
```

See table above for information on generated output files.

### `orchestra.yml`

The first of the two inputs describes the groups of servers in the cluster. This description is provided in yaml format. Consider the following example:

``` yaml
databases:
  sql: 1
  neo4j: 1

webservers: 2

computing:
  spark: 7
  other: 1
```

which translates into the groups:

| Group Name      | Parent        | Is Leaf | Is Root | Number of servers |
| --------        | ------------  | --------| ------- | -----------       |
| databases       | None          | No      | Yes     | 0                 |
| webservers      | None          | Yes     | Yes     | 2                 |
| computing       | None          | No      | Yes     | 0                 |
| sql             | databases     | Yes     | No      | 1                 |
| neo4j           | databases     | Yes     | No      | 1                 |
| spark           | None          | Yes     | No      | 7                 |
| computing-other | None          | Yes     | No      | 1                 |

The resulting cluster is composed of 7 distinct groups and 12 servers in total. You may notice that only leaf groups have a non-zero number of servers. This is just an implementation detail. In practice, the number of servers for each non-leaf group is equal to the sum of servers of it's children groups. So when you run a command against a group, that process is repeated along its children and children's children and so on.

The **orchestra** is responsible for generating two very important files: the *inventory* and the *concerto* playbook. The [inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) is what enables ansible to work simultaneously against multiple systems in your infrastructure. The *concerto* playbook creates the infrastructure from scratch, or adds new servers to the existing infrastructure.

When defining *orchestra.yml* be sure to check out the rules of the YAML markup language. **maestro** will throw back at you any syntax errors. There are a number of websites that provide a yaml parser for free ([for instance](http://yaml-online-parser.appspot.com/)).


### `instruments.yml`

Using *instruments* to describe the software requirements of each group is what allows you to go from a bare-bones set of machines to a fire breathing cluster. Combining *instruments* with your *orchestra* is what makes **maestro** worth the trouble and allows it to capture the full power and potential of ansible for cloud orchestration and automation. However, it's worthwhile noting that this input is **optional** and is not necessary run **maestro**. A bare-bones cluster is a perfectly reasonable starting point.

In practice, this boils down to specifying which ansible roles are executed by which group. You can write the ansible roles yourself or use ones from Ansible Galaxy. That is why Ansible Galaxy works so great here. It's basically plug-and-play. Let's provide a few examples, using the **orchestra** defined before:

``` yaml
sql:
  aaronpederson.mariadb:
    mariadb_user: geronimo
    maria_db_backup_enabled: true
    mariadb_client: true

databases:
  mongrelion.docker:
    docker_users: geronimo

spark:
  andrewrothstein.spark

webservers:
  debops.nginx:
  Oefenweb.shiny-server:

computing-other:
  myrole.helloworld:
    repeat: 3
```

Let's go over these group by group:

- **sql** - Include Role [aaronpederson.mariadb](https://galaxy.ansible.com/aaronpederson/mariadb/) with variables *mariadb_user*, *maria_db_backup_enabled* and *mariadb_client*. This is a simple example of how you can define a role for a group.
- **databases** - Include Role [mongrelion.docker](https://github.com/mongrelion/ansible-role-docker) with variable *docker_users*. This role is propagated to both it's children (sql and neo4j). One simple but effective strategy is to install docker and then deploy the desired software via containers. You may want to install docker for all groups or a selection of root/parent groups.
- **spark** - Include Role [andrewrothstein.spark](https://github.com/andrewrothstein/ansible-spark) with default variables. You can include roles without specifying any variables. Also, you don't have to specify every variable available. In either case, the defaults are used for whichever variables left unspecified.
- **webservers** - Include roles [debops.nginx](https://github.com/debops/ansible-nginx) and [Oefenweb.shiny-server](https://galaxy.ansible.com/Oefenweb/shiny-server/) with default variables. When including several roles without variables, you have to append ':' to the role name. This is a small yet important detail, which is essentially saying that each role is represented by a key-value pair, for which the value is an empty dictionary. This is different to the former case where a string was enough to represent the role (by name).
- **computing-other** - Include your own role, available at *playbooks/roles*, at the directory for roles, or at Ansible Galaxy.

Group variables defined here are written to *group_vars*. When variables are defined simultaneously for parent and child groups, ansible takes care of merging and ensuring priority. Some defaults are also written to *group_vars*, e.g. for roles *create_server* and *setup_image*. These two roles are built-in and differ from the rest. Please read the next section for more details.

### `playbooks/concerto.yml`

The concerto playbook is responsible for building your infrastructure in the cloud. After it has been generated by **maestro**, you can execute the playbook:

```
ansible-playbook -i inventory playbook/concerto.yml
```

To accomplish this, it uses two different roles that I wrote: *create_server* and *setup_image*. They are generic wrappers around [ansible's cloud modules](https://docs.ansible.com/ansible/latest/modules/list_of_cloud_modules.html) and can be found in *playbook/roles/*. As the names suggest, these modules are responsible for setting up the images necessary for the virtual machines and the vms themselves. For openstack, I used the modules *os_server*, *os_image* and *os_floating_ip*. The variables defined here are therefore an extension of the variables required for those modules. The variables may also vary between cloud-providers, although some will be required regardless of cloud-provider. I've tested and setup the default variables so that you can use them directly. The default OS image is Ubuntu 16.04.

The role *setup_image* downloads the image from the url (from [cloud images](http://cloud-images.ubuntu.com) in this case) and uploads it to the image registry in the cloud. This works well for openstack. But again, the behavior can be different for other providers.

The *create_server* role then takes the server name and image name as inputs, along others, and boots the vm. If a virtual machine with the same name exists, then the task is ignored. Cloud images can usually only be used with ssh keys. In my case setting the keypair wasn't enough because the private cloud that I was using was poorly configured and administered. Hence, **maestro** allows the public key to be injected via cloud-init instead. That is why there is a variable for passing your public key. It is important that the public key exists and the path is correct, otherwise if you're using a cloud image (as per default), you might not be able to ssh into the vm after it is created. This setup is generic and flexible enough that you can have your groups boot completely different operating systems. The role also tries to add a floating ip to the instance.

The default variables for *setup_image* on *openstack* are:

``` yaml
provider: openstack

image: "cloud-xenial64"
image_format: "qcow2"
cpu_arch: "x86_64"
distro: "ubuntu"
image_url: "http://cloud-images.ubuntu.com/xenial/current/xenial-server-cloudimg-amd64-disk1.img"
timeout_upload_image: 300
```

The default variables for *create_server* on *openstack* are:

``` yaml
provider: openstack

server:
image: "cloud-xenial64"
flavor: "m1.medium"
sec_groups: "default"
keypair:
volumes:
private_network:
external_network: "public"
username: "jsnow" # of House Stark
pubkey: "{{ lookup('file', '~/.ssh/id_rsa.pub' | expanduser) }}"
wait_for_instance: yes
timeout_instance_boot: 600
timeout_before_floating_ip:
wait_for_floating_ip: no
timeout_add_floating_ip: 120
```

You can overwrite the default values for these variables by re-defining them in the **instruments** file:

``` yaml
all:
  setup_image:
    image: ubuntu14
    image_url: "http://cloud-images.ubuntu.com/trusty/current/trusty-server-cloudimg-amd64-disk1.img"
  create_server:
    image: ubuntu14
    flavor: m1.big
    username: geronimo
```

Or you can apply the roles to individual groups instead. The concerto playbook populates the variable *'server'* automatically, so you don't have to worry about that. There are two variables that you can set using **maestro** instead of *instruments*. I only chose two variables for simplicity and I chose these two because they are the most likely to be changed: *provider* and *username*. The reason for this is that *group_vars* doesn't work in this case because the playbook is applied to localhost and not to the groups (remember: these don't actually exist before we run the playbook, creating them is its job). Thus, the concerto playbook lists these variables explicitly.

There is one **requirement** for this to work however. In **openstack** (I'm not sure about other cloud providers) **you need to have a valid networking setup (private network + router to external network)** to which the instances can attach and get connectivity. I'm considering adding an additional role/playbook for setting up this base infrastructure. This might be available on a future release.


### `playbooks/intermezzo.yml`

When *instruments* are provided, individual group playbooks are generated. These simply import the roles and variables provided by *instruments*. Again, these can be your own roles, or ones taken from Ansible Galaxy. As you could expect, the roles *create_server* and *setup_image* are ignored at this point. Additionally, only leaf groups have uniquely defined playbooks, whilst non-leaf groups simply import the individual playbooks of its children.

The *intermezzo* playbook imports the playbooks for all root groups, which corresponds to importing all individual leaf group playbooks. You can run the *intermezzo* playbook with the command:

```
ansible-playbook -i inventory playbook/intermezzo.yml
```

To instead execute the playbook for a given group named 'GROUPNAME', simply run:

```
ansible-playbook -i inventory playbook/group/GROUPNAME.yml
```

### `Makefile`

The makefile provides yet another wrapper for the commands described above. Below is a list of available targets:

| Target          | Command                                                             | Pre-requisite           |
| --------        | ------------                                                        |  --------               |
| virtualenv      | Creates a virtualenv named 'ENV'                                    | -                       |
| pipdependencies | Installs pip packages specified in requirements.txt                 | requirements.txt        |
| extraroles      | Install ansible galaxy roles specified in supplementary-roles.yml   | supplementary-roles.yml |
| install         | Runs the 3 targets above                                            | -                       |
| tests           | Runs the tests on maestro/tests with pytest                         | maestro/tests           |
| image           | Runs playbook to setup cloud image                                  | playbooks/setup-image.yml                |
| server          | Runs playbook to create server                                      | playbooks/create-server.yml              |
| playbooks       | python maestro.py orchestra.yml instruments.yml --stage="openstack" | maestro.py                               |
| servers         | ansible-playbook -i inventory playbooks/concerto.yml                | playbooks/concerto.yml , inventory/hosts |
| provision       | ansible-playbook -i inventory playbooks/intermezzo.yml              | playbooks/intermezzo.yml , inventory/hosts |
| bigbang         | Runs the 3 targets above                                            | -                                          |
| clean           | Removes all generated files          | -      |

## Beyond the basics <a name="advanced"></a>

### Instruments - Advanced Patterns

**maestro** abstracts many things about the underlying cloud environment. As with all abstractions, when something underneath the abstraction breaks, it leaks and you start observing unexpected, weird or erratic behavior. Once you figure out the root of the problem, you may need ways to configure what is underneath the abstraction. In the case of **maestro**, that is often done by changing the values for default variables. If there is a problem with *concerto* then you may need to change (and experiment with) the default variables for *create_server* and *setup_image*. If the problem lies instead with one of roles installed by Ansible Galaxy, then you need to rethink the variables for that role or, in extreme cases, write your own role or a wrapper/fix for that role.

Let's look at a concrete example. The private cloud that I've worked with while developing **maestro** has a few problems. Instances can take over 10 minutes to build and key-pairs don't work properly. The latter was addressed by injecting the public ssh key via cloud-init instead of key pair. The former however required a more nuanced approach. If you simply try to adjust the build waiting time, then you may have to pick a value that ends up being smaller or bigger than what is needed, making the process fail or last excruciatingly longer than necessary. Of course, if you just use the defaults you might be oblivious to any timeout value at all. Instead, I experimented by setting the timer to nil, submitting the job to openstack and visually monitoring its completion. Furthermore, the *create_server* module is also responsible for assigning a floating ip to the instance. So, if you try to assign a floating ip right after you submit the build instance job to openstack, it fails. An additional timeout is needed between the two. But how do you pick that value? Well, you have to experiment. For me, 10+ seconds worked pretty well and openstack can assign a floating ip to the machine while it's in building state. But, all of this is abstracted to the user by the *create_server* module. So, if any of the assumptions implicitly made by the default variables fails, then you need to be on the look out and ready to define your own defaults.

The folder *examples* provides some advanced pattern usage examples for *instruments* mostly. The *nowait* example corresponds to the one I described in the paragraph above. I'm sure there are many more usage patterns that are worth sharing and mentioning. Feel free to share yours via a pull request!

### Writing your own roles

Your cluster will really start to come alive once you start writing your own roles. These can be simple or more complex sets of tasks. You can create roles that clone a git repository and run a makefile. You can create roles that run docker compose on top of docker machines. You can create roles that bring microservices together. This really helps integrating self contained programs and applications in a larger ecosystem.

Once you've written and tested your ansible role, all you need to do is to make sure it is available to ansible. You can place it at **playbooks/roles/** or at the path for roles defined via the ansible configuration file. Refer to ansible's roles [documentation page](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html) to learn more about how to write and structure roles.

### Versioning your cluster

It makes perfect sense to version control the description of your cluster. Your cluster may start off looking like one thing and end up looking like something completely different. It's only natural to experiment and iterate over the initial set of requirements. When you're working with a distributed application, large research project or reproducible study, it is likely associated with one cluster (or several). Hence, it is associated with at least one cluster description. Then, to re-create the inventory file and playbooks necessary to reproduce the cluster, one just needs to clone/download **maestro** and run it against the description of the cluster.

Here are the files that you may want to version control:

- orchestra.yml
- instruments.yml
- requirements-roles.yml
- roles written by you and added to *instruments.yml*

where *requirements-roles.yml* contains the list of ansible galaxy roles required by your cluster. Originally this corresponds to *supplementary-roles*, but once you start adding galaxy roles to your *instruments.yml* file, then these become dependencies of the cluster, rather than just a supplementary set of roles.

You have two ways of versioning the roles that you wrote yourself. They can live on their own repository on github, for instance, or you can include them together with the three files above. This decision depends on how coupled the role and research application are. It may not make sense for that role to exist outside that application. On the other hand, if the role is self-contained and is available on github, then you may consider adding it to Ansible Galaxy and consequently to *requirements-roles.yml*.

## Troubleshooting <a name="troubleshooting"></a>

As with any other piece of software, things can break and fail to meet expectations. Below are some common problems and solutions:

#### Forgetting to set your cloud authentication credentials
You run your playbooks and you get an error message from ansible. If you're using openstack and the word *keystonerc* shows up somewhere in there, then you forgot to set your credentials by sourcing the openstack_rc file.

#### Forgetting to activate your virtual environment
If your command line does not recognize the command 'ansible' or 'ansible-playbook', then you forgot to activate your virtual environment.

#### Running an 'empty' group playbook
**maestro** generates an individual playbook for each group regardless of whether you defined any *instruments* for that group or not. When you don't define *instruments* for a leaf group, you end up with the skeleton for that group's playbook, but with an empty set of tasks. So, naturally, if you try to run that playbook, ansible will complain about an empty list of tasks. For those groups, you can use a dummy role, for instance *webofmars.dummy*, just to make sure everything runs smoothly.

#### Misspelling a role name in *instruments*
Ansible complains about not recognising a role. If that's the case, then you might misspelled the role name wrong, or forgot to install that role.

#### Improper usage of *orchestra* and *instruments*
**maestro** displays most errors regarding improper *orchestra* or *instruments* usage, including yaml syntax errors. One example of invalid usage is to name one of the root groups: 'other'.

#### Forgetting to append ':' when defining multiple roles without variables in *instruments*
Another common mistake is to forget to append the character ':' to the role name when listing multiple roles without variables for a group in *instruments*. In this case, the python yaml module will throw an exception. Ideally we wouldn't have to, but we can't mix together strings and dictionaries in the same list. I had to choose between:

``` yaml
# Option A
groupX:
  role1:
  role2:

# Option B
groupX:
  - role1:
  - role2:

# This is invalid because you have a list containing different types (strings and dictionaries)
groupX:
  - role1
  - role2
  - role3:
    var1: value1
    var2: value2
```
Thus I opted for the simpler version (Option A).


## Contributing <a name="contributing"></a>

Extending **maestro** to support other cloud providers (aws, azure, google) should be quite straightforward. Ansible already provides modules for most cloud providers, so it's just a matter of writing a thin wrapper and integrating them in the *setup_image* and *create_server* roles. This may be particularly easy for people that have worked with Ansible and these providers before. So pull requests are very welcome!

Handling multiple clusters means that you keep a pair of *orchestra* and *instruments* for each cluster. But, one can imagine generalising **maestro** to handle multiple cloud providers within the same cluster, albeit not very common. Nevertheless, this may be an interesting route of development in the future, if **maestro** gains momentum.

Any comments or feedback is welcome. Feel free to email me at ppintodasilva@gmail.com.

## License <a name="license"></a>

**maestro** is released under the Apache License, Version 2.0. For the complete license please refer to the file 'LICENSE'.
