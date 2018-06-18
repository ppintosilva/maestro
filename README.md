# maestro
Orchestrate groups of software-ready instances on the cloud

[//]: # (<div style="text-align:center">)

<img src="maestro.svg" alt="maestro_icon" width="200px">

---

## TL;DR

Install `maestro`:
1. aa
2. bb
3. cc

Use `maestro`:
1. aa
2. bb
3. cc

---

## What is `maestro`

In short, **maestro** is a wrapper for ansible. It generates ansible playbooks and inventory file from a description of the cluster, which is given by two input files:

1. **Orchestra** - lists groups: name of group, number of servers per group, and the hierarchy between groups (parents, children).

2. **Instruments** - lists ansible-roles to be executed by each group **(optional)**.

The generated ansible playbooks have two purposes:

- Create the servers in each group

- Install and configure software (ansible roles) for each server

With the generated ansible files you can now get your cluster up and running with the necessary software, faster than before, without having to write the playbook and inventory files yourself.

## Why `maestro`

### When disaster strikes

Your very own first cluster. Maybe it was born out of necessity, maybe you were just curious, maybe you were bored or your boss told you to. Regardless of why and when it happened, it was probably a painful (but rewarding) experience. If the why was important however, watching it crumble and disappear into oblivion might have been an even more painful experience. Independently of whose fault that was (`insert scapegoat's name here`), you probably had to do it all over again. And then you might have realised that you don't remember exactly how you did it and which particular piece of software was installed in this machine or that machine. If only there was a magic redo button. Hopefully **maestro** is a step forward in that direction.

### Reproducible Cluster

There is no doubt that *Reproducible Research* is a good thing. However, when it's unfeasible to execute your, or someone else's, research pipeline on a single computer, there is an extra set of dependencies that adds up on top of existing ones (data and software dependencies). These are dependencies on computing resources: processing power, storage, networking. Whether you like it or not, you may need to spin up a cluster of cloud instances, or use an existing one, to run those reproducible experiments. Having an easy way to describe and re-create the computing resources necessary to run an experiment may come a long way in facilitating *Reproducible Research*.

### *Because it's faster*

But if the reasons above are not sufficient to use **maestro**, or the underlying orchestration tools (ansible), then *because it's faster* should be a good enough reason. These and similar tools (e.g. puppet, chef, juju, saltstack) enable you to get a cluster up and running much quicker than you would otherwise.

## Why `ansible`

### Group it to win it

Software systems can be structured in a number of different ways. To reduce complexity we often apply principles such as separation of concerns and create notable architectural patterns. When your system is relatively small, or in development stages, it may be ok to run all of its components on a single machine. However, when your system is deployed on the cloud, or needs to scale across several machines, it's not uncommon to have one or more servers dedicated to handling each component individually. One definitely very common setup is to split your servers into several groups:

- Databases - they store your data (e.g. MySql, MongoDB, Neo4j, Cassandra)
- Computing - they handle business logic, run your analytics/research pipeline, make pancakes (e.g. hadoop/spark cluster, your hello world program)
- Webservers - they expose your website, results, work to the world or company (e.g. apache, nginx, shiny)

And these groups have quite distinct software dependencies. For example, modern database systems use client-server models to decouple the components necessary to run the database daemon, from the ones necessary to query and interact with the database. *Database* servers can therefore install server-side libraries, whilst *Computing* and *Webservers* only need much lighter client-side libraries in order to interact with the database.

I found that ansible makes it easier to address servers by functionality. The inventory file lists servers and defines hierarchies among groups. This feature is extremely useful and fits naturally when setting up or managing your cluster(s). You may choose to have one or more servers per group. To have servers belong to several groups. To have groups within other groups. Or choose not to. It's up to you.

### In a Galaxy not that far away

[Ansible Galaxy](https://galaxy.ansible.com/) is one of the best things about ansible. You can easily reuse content developed and thoroughly tested by other users. In addition to ansible's extensive list of native modules, Ansible Galaxy provides access to a whole new set of ansible roles for installing, configuring and deploying all kinds of software. Building **maestro** on top of ansible means that you get all the benefits of Ansible Galaxy.

### To learn or not to learn `ansible`

But why do I need **maestro**? Why don't I just learn and use ansible directly then? Or a different orchestration tool for that matter? You should learn ansible. And you're using ansible when working with **maestro**. What I noticed when using ansible is that a lot of playbooks end up with similar structure. I worked out what how to replicate this structure automatically to avoid brainless copy-pasting. What **maestro** does is to generate the files necessary to let ansible setup your cluster. User input is still necessary, but you don't have to write the ansible playbooks or the hosts inventory file yourself. So, you don't have to know ansible to the same extent that an experienced user has in order to use maestro and setup your cluster on the cloud. In fact, knowing ansible is not a requirement for basic usage (and I've tried to make it that way as much as possible). However, it certainty helps that you know or at least understand the main concepts behind ansible. When you start writing your own roles, learning ansible will become inevitable. At the end of the day, **maestro** is just a wrapper for ansible. Hopefully, a useful one.

## Installation

Installing **maestro** should be pretty straightforward whether you use the available Makefile or not.

Using the `Makefile`:

1.
2.

**Not** using the `Makefile`:

1.
2.


## Usage

List of files (file | (input/output) | description)

### `maestro.py`

### `orchestra.yml`

### `instruments.yml`

### `inventory/hosts`

### `playbooks/concerto.yml`

### `playbooks/intermezzo.yml`

### `makefile`

## Advice

. Whenever we modify the *orchestra* or *instruments* we need to re-execute **maestro**.

## Beyond the basics

### Patterns

### Redefining defaults

### Supplementary roles

### Writing your own roles

### Cloud providers

### Versioning your cluster


Vars for:
  - setup_image
  - create_server

Can be specified:
  - In the roles file
  - By creating a new directory 'vars' in the roles directory and populating 'main.yml'
  - Changing the variables at 'playbooks/roles/ROLE_NAME/defaults/main.yml' - although this affects every

## License
