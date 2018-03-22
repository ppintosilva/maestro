#
## Maestro's own BigBang Makefile
#

red:=$(shell tput setaf 1)
blue:=$(shell tput setaf 4)
green:=$(shell tput setaf 2)
reset:=$(shell tput sgr0)

# Props to devstack
all:
	@echo "This just saved you from a terrible mistake!"

# Destroy all generated files - but not the servers
clean:


# Destroy all generated files and servers
armageddon:

###
###
###

# Install stuff
virtualenv: /usr/bin/python2
	$(info $(blue)Making new virtualenv at ./ENV]$(reset))
	@/usr/bin/python2 -m virtualenv ENV

pipdependencies: ENV/bin/pip2.7 requirements.txt
	$(info $(blue)Installing pip requirements in virtualenv$(reset))
	@ENV/bin/pip install -r requirements.txt

install: virtualenv pipdependencies
	$(info $(green) OK! $(reset))

###
###
###

# Install extra-roles
extraroles: ENV/bin/ansible-galaxy supplementary-roles.yml
	$(info $(blue)Installing supplementary ansible galaxy roles $(reset))
	@ENV/bin/ansible-galaxy install -r requirements.yml

# Individual role sanity check
tests: tests
	@pytest tests
	@ansible-playbook -i inventory/openstack.py playbooks/roles/setup_image/tests/test.yml
	@ansible-playbook -i inventory/openstack.py playbooks/roles/create_server/tests/test.yml

# Create image with default values (ubuntu 16.04)
image:
	@ansible-playbook -i inventory/openstack playbooks/setup-image.yml

# Create server with default values (4 GB RAM, ubuntu 16.04)
server:
	@ansible-playbook -i inventory/openstack.py playbooks/create-server.yml


###
###
###

# Generate
god: ENV/bin/python2.7 band.yml instruments.yml
	@ENV/bin/python2.7 maestro band.yml --instruments "instruments.yml"

# Creating the servers
bigbang:
	@ansible-playbook -i inventory/openstack.py playbooks/concerto.yml

# Running the roles
inflation:
	@ansible-playbook -i inventory/openstack.py playbooks/all.yml
	# For each group

	# For each host

concerto:
	god bigbang inflation
