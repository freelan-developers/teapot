# Targets

default: test

pep8:
	find . -type f -name \*.py | xargs autopep8 -a -a -i

flake8:
	flake8 tea_party

test:
	python setup.py test

coverage:
	coverage run --include "tea_party/*" tea_party/tests/tea_party_test.py
	coverage report

register:
	python setup.py register

upload:
	python setup.py sdist bdist_egg upload

# Aliases

check: flake8
