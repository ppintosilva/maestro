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
SETUP_IMAGE_TESTFILE=playbooks/roles/setup_image/tests/test.yml
CREATE_SERVER_TESTFILE=playbooks/roles/create_server/tests/test.yml

tests: $(SETUP_IMAGE_TESTFILE) $(CREATE_SERVER_TESTFILE)
	ansible-playbook -i inventory/openstack.py $(SETUP_IMAGE_TESTFILE)
	ansible-playbook -i inventory/openstack.py $(CREATE_SERVER_TESTFILE)

# Destroy all servers - irreversible!!
clean:
	./clean.sh

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
