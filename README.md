# maestro
Orchestrate software-ready clusters on the cloud

[//]: # (<div style="text-align:center">)

<img src="maestro.svg" alt="maestro_icon" width="200px">

---

## 0. TL;DR

1. aa
2. bb
3. cc

---

## Why `maestro`

### When disaster strikes

Your very own first cluster. Maybe it was born out of necessity, maybe you were curious, maybe you were just bored, or maybe your boss told you to. Regardless of why and when it happened, it was probably a painful (but rewarding) experience. If the why was important however, watching it crumble and disappear into oblivion might have been an even more painful experience. Independently of whose fault that was (`insert escape goat's name here`), you probably had to do it all over again. And then you might have realised that you don't remember exactly how you did it and which particular piece of software was installed in this machine or that machine. If only there was a magic redo button. Hopefully **maestro** is a step forward in that direction.

### Reproducible Cluster

There is no doubt that *Reproducible Research* is a good thing. However, when it's unfeasible to execute your, or someone else's, research pipeline on a single computer, there is an extra set of dependencies that adds up on top of existing ones (e.g. data and software dependencies). These are dependencies on computing resources: processing power, storage, networking. Whether you like it or not, you may need to spin up a cluster of cloud instances, or use an existing one, to run those reproducible experiments. Having a way to reproduce the computing resources necessary to run an experiment may come a long way in facilitating *Reproducible Research*.

### *Because it's faster*

But if these are not sufficient reasons to use **maestro**, or the underlying orchestration tools (ansible), then *because it's faster* should be a good enough reason. These and similar tools (e.g. puppet, chef, juju, saltstack) enable you to get a cluster up and running much quicker than you would otherwise.

## Overview

### Group it to win it

A very common cluster setup to have

## Installation

## Usage

### `maestro.py`

### `orchestra.yml`

### `instruments.yml`

### `inventory/hosts`

### `playbooks/concerto.yml`

### `playbooks/intermezzo.yml`

### `makefile`

## Beyond the basics

### Supplementary Roles

### Writing your own Roles

### Cloud Providers

### Versioning your cluster


Vars for:
  - setup_image
  - create_server

Can be specified:
  - In the roles file
  - By creating a new directory 'vars' in the roles directory and populating 'main.yml'
  - Changing the variables at 'playbooks/roles/ROLE_NAME/defaults/main.yml' - although this affects every

## License
