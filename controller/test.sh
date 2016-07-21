python3 -m doctest *.py

pyflakes .
mypy --silent-imports .
python3 -m pep8 --ignore=W503,E251 .
