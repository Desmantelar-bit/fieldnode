PYTHON ?= python

.PHONY: eval eval-public mule-demo mule-demo-clean

eval:
	$(PYTHON) -m ml.eval.run

eval-public:
	$(PYTHON) -m ml.eval.public_dataset $(PUBLIC_DATASET_ARGS)

mule-demo:
	powershell -ExecutionPolicy Bypass -File scripts/mule_demo.ps1

mule-demo-clean:
	docker compose -p fieldnode-s7 -f docker-compose.mule.yml down -v
