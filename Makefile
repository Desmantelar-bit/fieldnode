PYTHON ?= python

.PHONY: eval eval-public mule-demo mule-demo-clean test-backend test-mysql lint test-front test-firmware ci-local docs-status gateway-up cloud-up preflight load-explain

test-backend:
	$(PYTHON) manage.py migrate --noinput
	$(PYTHON) -m pytest api_tcc/tests simulators

test-mysql:
	USE_SQLITE=False $(PYTHON) manage.py migrate --noinput
	USE_SQLITE=False $(PYTHON) -m pytest api_tcc/tests/test_telemetria.py api_tcc/tests/test_health.py

lint:
	$(PYTHON) -m compileall -q api_tcc setup simulators scripts
	$(PYTHON) -m pytest --collect-only -q

test-front:
	cd frontend-next && npm ci && npm run lint && npm run type-check && npm run build

test-firmware:
	cd firmware && python -m pip install platformio==6.1.16 && copy /Y include\\secrets.example.h include\\secrets.h && pio run -e esp32dev && pio test -e native

docs-status:
	$(PYTHON) scripts/check_docs_status.py

ci-local: lint test-backend test-front docs-status

eval:
	$(PYTHON) -m ml.eval.run

eval-public:
	$(PYTHON) -m ml.eval.public_dataset $(PUBLIC_DATASET_ARGS)

mule-demo:
	powershell -ExecutionPolicy Bypass -File scripts/mule_demo.ps1

mule-demo-clean:
	docker compose -p fieldnode-s7 -f docker-compose.mule.yml down -v

gateway-up:
	@test -f .env || (echo 'Crie .env a partir de .env.example; nenhum segredo será criado automaticamente.' && exit 1)
	docker compose up -d --build
	docker compose exec -T web python manage.py migrate --noinput
	./scripts/preflight.sh

preflight:
	./scripts/preflight.sh

load-explain:
	$(PYTHON) scripts/load/explain_queries.py

cloud-up:
	./scripts/cloud_up.sh
