VIRTUALENV_DIR := venv
PIP := $(VIRTUALENV_DIR)/bin/pip

clean:
		find . -name "*.py[co]" -delete
		rm -rf ${VIRTUALENV_DIR} .serverless

venv:
		test -d ${VIRTUALENV_DIR}/bin || virtualenv ${VIRTUALENV_DIR}

deps: requirements.txt venv
		${PIP} install --upgrade pip
		${PIP} install -Ur requirements.txt

deploy: clean venv deps
		serverless deploy --verbose
