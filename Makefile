SHELL := /bin/bash

ALLURE_DIR ?= .allure
COVERAGE_DIR ?= .coverage-html

export ARGS

test: coverage check-coverage

static:
	pre-commit run --all-files

coverage:
	coverage run --concurrency=eventlet --source gateway --branch -m pytest --alluredir=$(ALLURE_DIR) tests$(ARGS)
	coverage html -d $(COVERAGE_DIR)

check-coverage:
	coverage report -m --fail-under 100

run:
	nameko run --config config.yml gateway.service:GatewayService

build-image:
	docker build -t calumwebb/gateway-service:$(TAG) .;

push-image:
	docker push calumwebb/gateway-service:$(TAG)