# Targets

default: test

pep8:
	find . -type f -name \*.py | xargs autopep8 -a -a -i

flake8:
	flake8 teapot

test:
	python setup.py test

coverage:
	coverage run --include "teapot/*" teapot/tests.py
	coverage report

register:
	python setup.py register

upload:
	python setup.py sdist upload

# Aliases

check: flake8
