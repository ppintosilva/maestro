#
## Maestro's own BigBang Makefile
#

# Props to devstack
all:
	@echo "This just saved you from a terrible mistake!"

# Create virtualenv and install dependencies
install:
	./install.sh

# Individual role sanity check
tests:
	ansible-playbook -i inventory/openstack.py playbooks/roles/setup-image/tests/test.yml
	ansible-playbook -i inventory/openstack.py playbooks/roles/create-server/tests/test.yml

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
