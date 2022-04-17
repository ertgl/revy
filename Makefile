.DEFAULT_GOAL=""


VIRTUALENV_PATH=.venv


API_DOCS_PATH=docs/source/api


venv:
	test -d $(VIRTUALENV_PATH) || virtualenv $(VIRTUALENV_PATH) -p python3


venv.clean:
	rm -rf $(VIRTUALENV_PATH)


deps.install:
	pip install -r requirements/requirements-dev.txt
	pip install -r requirements/requirements.txt
	pip install -r requirements/requirements-docs.txt
	pip install -r requirements/requirements-django.txt
	pip install -r requirements/requirements-samples.txt


link:
	pip install -e .


prepare: deps.install link


django.migrations:
	cd dev/django/ && python manage.py makemigrations revy --no-header


django.migrate:
	cd dev/django/ && python manage.py migrate


django: django.migrations django.migrate


typecheck:
	mypy . --namespace-packages --explicit-package-bases


mypy.clean:
	rm -rf .mypy_cache


test.core:
	python -m unittest discover -s tests/ -p 'test_*.py' --verbose


test.samples.django.accounting:
	cd samples/django/accounting && \
		rm -f db.sqlite3 && \
		rm -f ledger/migrations/*.py && \
		touch ledger/migrations/__init__.py && \
		python manage.py makemigrations ledger --no-header && \
		python manage.py migrate && \
		python manage.py test ledger


test.samples.django.swappable:
	cd samples/django/swappable && \
		rm -f db.sqlite3 && \
		rm -f revisions/migrations/*.py && \
		touch revisions/migrations/__init__.py && \
		yes "1" | yes "1" | python manage.py makemigrations revisions --no-header && \
		python ../../../dev/django/misc/prepare_swappable_migration.py && \
		python manage.py migrate && \
		python manage.py test revisions


test.samples.django: django test.samples.django.accounting test.samples.django.swappable


test.samples: test.samples.django


.PHONY: test
test: typecheck test.core test.samples


.PHONY: docs
docs:
	mkdir -p $(API_DOCS_PATH)
	sphinx-apidoc src/revy -f -M -o $(API_DOCS_PATH)
	python docs/source/_postprocessors/_run.py
	cd docs && make html


.PHONY: docs.clean
docs.clean:
	cd docs && make clean
	rm -rf $(API_DOCS_PATH)


clean: venv.clean mypy.clean docs.clean
