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
	@rm -rf playbooks/concerto.{yml,retry} playbooks/intermezzo.{yml,retry} && find playbooks/group/ -type f -not -name '.gitkeep' -print0 | xargs -0 -r rm -rf -- && find group_vars -mindepth 1 -maxdepth 1 -type d -print0 | xargs -0 -r rm -rf -- && echo OK!

###
###
###

# Install stuff
.PHONY: virtualenv
virtualenv:
	$(info $(blue)Making new virtualenv at ./ENV]$(reset))
	@python2 -m virtualenv ENV

.PHONY: pipdependencies
pipdependencies: requirements.txt
	$(info $(blue)Installing pip requirements in virtualenv$(reset))
	@pip install -r $<

.PHONY: install
install: virtualenv pipdependencies
	@echo OK!

###
###
###

# Install extra-roles
.PHONY: extraroles
extraroles: supplementary-roles.yml
	$(info $(blue)Installing supplementary ansible galaxy roles $(reset))
	@ansible-galaxy install -r $<

# Individual role sanity check
.PHONY: tests
tests: maestro/tests
	@pytest $< -vv

# Create image with default values (ubuntu 16.04)
.PHONY: image
image: playbooks/setup-image.yml
	@ansible-playbook -i inventory $<

# Create server with default values (4 GB RAM, ubuntu 16.04)
.PHONY: server
server: playbooks/create-server.yml
	@ansible-playbook -i inventory $<


###
###
###

# Generate
.PHONY: maestro
maestro: maestro.py 	
	python2.7 $< orchestra.yml instruments.yml --stage="openstack"


# Creating the servers
.PHONY: concerto
concerto: playbooks/concerto.yml inventory/hosts
	ansible-playbook -i inventory $<

# Running the roles
.PHONY: intermezzo
intermezzo: playbooks/intermezzo.yml inventory/hosts
	ansible-playbook -i inventory $<

# All in a big pipe
.PHONY: bigbang
bigbang: playbooks concerto intermezzo
	@echo OK!
