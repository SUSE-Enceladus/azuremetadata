test:
	PYTHONPATH=./lib pytest

coverage:
	PYTHONPATH=./lib pytest --cov-report html --cov=lib/

