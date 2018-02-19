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

# Destroy all servers - irreversible!!
clean:
	./clean.sh

# Install stuff
virtualenv: /usr/bin/python2
	$(info $(blue)Making new virtualenv at ./ENV]$(reset))
	@/usr/bin/python2 -m virtualenv ENV

pipdependencies: ENV/bin/pip2.7 requirements.txt
	$(info $(blue)Installing pip requirements in virtualenv$(reset))
	@ENV/bin/pip install -r requirements.txt

galaxydependencies: ENV/bin/ansible-galaxy requirements.yml
	$(info $(blue)Installing ansible galaxy $(reset))
	@ENV/bin/ansible-galaxy install -r requirements.yml

install: virtualenv pipdependencies galaxydependencies
	$(info $(green) OK! $(reset))
	

# Individual role sanity check
tests:
	ansible-playbook -i inventory/openstack.py playbooks/roles/setup_image/tests/test.yml
	ansible-playbook -i inventory/openstack.py playbooks/roles/create_server/tests/test.yml

# Create image with default values (ubuntu 16.04)
image:
	ansible-playbook -i inventory/openstack playbooks/setup-image.yml

# Create server with default values (4 GB RAM, ubuntu 16.04)
server:
	ansible-playbook -i inventory/openstack.py playbooks/create-server.yml

# A freak accident just occurred out of nowhere
singularity:
	ansible-playbook -i inventory/openstack.py playbooks/singularity.yml

# 10^-37 seconds later it just kept getting bigger and bigger
inflation:
	ansible-playbook -i inventory/openstack.py playbooks/inflation.yml

# Wonderwall
bigbang: singularity inflation

# Dynamic inventory to static
tostatic:
	python tostatic.py -i inventory/openstack.py --config config.yml -o inventory/hosts
