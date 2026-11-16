SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

CLUSTER ?= secureapp
IMAGE ?= secureapp:dev
PYTHON ?= python3

.PHONY: help venv test lint build cluster-up deploy monitoring logs port-forward grafana prometheus scan-secrets clean cluster-down

help:
	@echo "Targets:"
	@echo "  venv          Create .venv and install app dependencies"
	@echo "  test          Run ruff and pytest with coverage"
	@echo "  lint          Run ruff checks"
	@echo "  build         Build the application container image"
	@echo "  cluster-up    Create/start the local k3d cluster"
	@echo "  deploy        Build, import, and deploy the application"
	@echo "  monitoring    Install Prometheus/Grafana and the dashboard"
	@echo "  port-forward  Forward the app to http://127.0.0.1:8080"
	@echo "  grafana       Forward Grafana to http://127.0.0.1:3000"
	@echo "  prometheus    Forward Prometheus to http://127.0.0.1:9090"
	@echo "  logs          Follow application logs"
	@echo "  scan-secrets  Run local secret scan"
	@echo "  cluster-down  Delete the local k3d cluster"
	@echo "  clean         Remove local Python/test caches"

venv: .venv/bin/python

.venv/bin/python:
	$(PYTHON) -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r app/requirements-dev.txt

test: venv
	.venv/bin/ruff check app
	.venv/bin/pytest --cov=secureapp --cov-report=term-missing --cov-fail-under=80

lint: venv
	.venv/bin/ruff check app

build:
	docker build --pull -t $(IMAGE) app

cluster-up:
	CLUSTER=$(CLUSTER) scripts/cluster-up.sh

deploy:
	CLUSTER=$(CLUSTER) IMAGE=$(IMAGE) scripts/deploy-local.sh

monitoring:
	CLUSTER=$(CLUSTER) scripts/deploy-monitoring.sh

logs:
	kubectl -n secureapp logs -f deployment/secureapp

port-forward:
	kubectl -n secureapp port-forward svc/secureapp 8080:80

grafana:
	kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80

prometheus:
	kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090

scan-secrets:
	scripts/scan-secrets.sh

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov app/.pytest_cache app/.ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

cluster-down:
	CLUSTER=$(CLUSTER) scripts/cluster-down.sh
