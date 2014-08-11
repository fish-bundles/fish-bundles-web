# This file is part of fish-hooks.
# https://github.com/heynemann/fish-hooks

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Bernardo Heynemann heynemann@gmail.com
#

# lists all available targets
list:
	@sh -c "$(MAKE) -p no_targets__ | awk -F':' '/^[a-zA-Z0-9][^\$$#\/\\t=]*:([^=]|$$)/ {split(\$$1,A,/ /);for(i in A)print A[i]}' | grep -v '__\$$' | grep -v 'make\[1\]' | grep -v 'Makefile' | sort"
# required for list
no_targets__:

# install all dependencies (do not forget to create a virtualenv first)
setup:
	@pip install -U -e .\[tests\]

run:
	@fish-hooks-api

# test your application (tests in the tests/ directory)
test: unit

unit:
	@coverage run --branch `which nosetests` -vv --with-yanc -s tests/
	@coverage report -m --fail-under=80

# show coverage in html format
coverage-html: unit
	@coverage html -d cover

migration:
	@cd fishhooks/ && alembic revision -m "$(DESC)"

drop:
	@-cd fishhooks/ && alembic downgrade base
	@$(MAKE) drop_now

drop_now:
	@mysql -u root -e "DROP DATABASE IF EXISTS fishhooks; CREATE DATABASE IF NOT EXISTS fishhooks"
	@echo "DB RECREATED"

drop_test:
	@-cd tests/ && alembic downgrade base
	@mysql -u root -e "DROP DATABASE IF EXISTS test_fishhooks; CREATE DATABASE IF NOT EXISTS test_fishhooks"
	@echo "DB RECREATED"

data db:
	@cd fishhooks/ && alembic upgrade head

data_test:
	@cd tests/ && alembic upgrade head

# run tests against all supported python versions
tox:
	@tox

#docs:
	#@cd fishhooks/docs && make html && open _build/html/index.html
