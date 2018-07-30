#
## Maestro's own BigBang Makefile
#

red:=$(shell tput setaf 1)
blue:=$(shell tput setaf 4)
green:=$(shell tput setaf 2)
reset:=$(shell tput sgr0)

# Props to devstack
.PHONY: all
all:
	@echo "This just saved you from a terrible mistake!"

# Destroy all generated files - but not the servers
.PHONY: clean
clean:
	@rm -rf playbooks/concerto.{yml,retry} playbooks/intermezzo.{yml,retry} && rm -rf playbooks/group/*.{yml,retry} && find group_vars -mindepth 1 -maxdepth 1 -type d -print | xargs rm -rf && echo OK!

###
###
###

# Install stuff
.PHONY: virtualenv
virtualenv:
	$(info $(blue)Making new virtualenv at ./ENV$(reset))
	@python2 -m pip install virtualenv && @python2 -m virtualenv ENV

.PHONY: pipdependencies
pipdependencies: requirements.txt
	$(info $(blue)Installing pip requirements in virtualenv$(reset))
	@ENV/bin/pip install -r $<

.PHONY: extraroles
extraroles: supplementary-roles.yml
	$(info $(blue)Installing supplementary ansible galaxy roles $(reset))
	@ENV/bin/ansible-galaxy install -r $<

.PHONY: install
install: virtualenv pipdependencies
	@echo OK!

###
###
###

# Individual role sanity check
.PHONY: tests
tests: maestro/tests
	@ENV/bin/pytest $< -vv

# Create image with default values (ubuntu 16.04)
.PHONY: image
image: playbooks/setup-image.yml
	@ENV/bin/ansible-playbook -i inventory $<

# Create server with default values (4 GB RAM, ubuntu 16.04)
.PHONY: server
server: playbooks/create-server.yml
	@ENV/bin/ansible-playbook -i inventory $<


###
###
###

# Generate
.PHONY: playbooks
playbooks: maestro.py
	ENV/bin/python2.7 $< orchestra.yml instruments.yml --stage="openstack"

# Creating the servers
.PHONY: servers
servers: playbooks/concerto.yml inventory/hosts
	ENV/bin/ansible-playbook -i inventory $<

# Running the roles
.PHONY: provision
provision: playbooks/intermezzo.yml inventory/hosts
	ENV/bin/ansible-playbook -i inventory $<

