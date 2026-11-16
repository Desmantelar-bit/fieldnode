PYTHON ?= python

.PHONY: eval eval-public

eval:
	$(PYTHON) -m ml.eval.run

eval-public:
	$(PYTHON) -m ml.eval.public_dataset $(PUBLIC_DATASET_ARGS)
