PY ?= python
.PHONY: all data test index experiments demo agent
all: data test index experiments demo
data:
	$(PY) scripts/generate_dataset.py && $(PY) scripts/build_questions.py
test:
	$(PY) -m pytest -q tests
index:
	$(PY) -m rag.build --out indexes/default
experiments:
	$(PY) -m eval.run_experiments
demo:
	$(PY) -m agent.scripted_demo
agent:
	$(PY) -m agent.run_agent --demo
