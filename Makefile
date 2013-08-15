# Targets

pep8:
	find . -type f -name \*.py | xargs autopep8 -a -a -i

flake8:
	flake8 tea_party

test:
	python setup.py test

# Aliases

check: pyflakes
