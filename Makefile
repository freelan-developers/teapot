# Targets

pep8:
	find . -type f -name \*.py | xargs autopep8 -a -a -i

pyflakes:
	pyflakes three_party

test:
	python setup.py test

# Aliases

check: pyflakes
