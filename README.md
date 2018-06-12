# maestro
Orchestrate software-ready clusters on the cloud

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

## Why `maestro`

### When disaster strikes

Your very own first cluster. Maybe it was born out of necessity, maybe you were just curious, maybe you were bored or your boss told you to. Regardless of why and when it happened, it was probably a painful (but rewarding) experience. If the why was important however, watching it crumble and disappear into oblivion might have been an even more painful experience. Independently of whose fault that was (`insert escape goat's name here`), you probably had to do it all over again. And then you might have realised that you don't remember exactly how you did it and which particular piece of software was installed in this machine or that machine. If only there was a magic redo button. Hopefully **maestro** is a step forward in that direction.

### Reproducible Cluster

There is no doubt that *Reproducible Research* is a good thing. However, when it's unfeasible to execute your, or someone else's, research pipeline on a single computer, there is an extra set of dependencies that adds up on top of existing ones (data and software dependencies). These are dependencies on computing resources: processing power, storage, networking. Whether you like it or not, you may need to spin up a cluster of cloud instances, or use an existing one, to run those reproducible experiments. Having an easy way to describe and re-create the computing resources necessary to run an experiment may come a long way in facilitating *Reproducible Research*.

### *Because it's faster*

But if the reasons above are not sufficient to use **maestro**, or the underlying orchestration tools (ansible), then *because it's faster* should be a good enough reason. These and similar tools (e.g. puppet, chef, juju, saltstack) enable you to get a cluster up and running much quicker than you would otherwise.

### To learn or not to learn `ansible`

Why don't I just learn and use ansible directly then? Or a different orchestration tool for that matter? You should learn ansible. And you're using ansible when working with **maestro**. What I noticed when using ansible is that a lot of playbooks end up with similar structure. I worked out what how to replicate this structure automatically to avoid brainless copy-pasting. What **maestro** does is to generate the files necessary to let ansible setup your cluster. User input is still necessary, but you don't have to write the ansible playbooks or the hosts inventory file yourself. So, you don't have to know ansible to the same extent that an experienced user has in order to use maestro and setup your cluster on the cloud. In fact, knowing ansible is not a requirement for basic usage (and I've tried to make it that way as much as possible). However, it certainty helps that you know or at least understand the main concepts behind ansible. When you start writing your own roles, learning ansible will become inevitable. At the end of the day, **maestro** is just a wrapper for ansible. Hopefully, a useful one.

## Overview

### Group it to win it

In software systems, . So, in cloud sett it's not uncommon to have groups of machines dedicated to handling each of these components. One definitely very common setup is to divide your machines into:

- Databases -
- Processing - responsible for handling business logic. hadoop/spark cluster..
- Webservers -

And these groups os servers have quite distinct software dependencies. Database instances have server-side software installed, whilst Processing and Webservers have much lighter client libraries installed in order to query the databases.

### Main actors

### Workflow

## Installation

## Usage

List of files (file | (input/output) | description)

### `maestro.py`

### `orchestra.yml`

### `instruments.yml`

### `inventory/hosts`

### `playbooks/concerto.yml`

### `playbooks/intermezzo.yml`

### `makefile`

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
