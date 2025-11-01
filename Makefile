.PHONY: run test clean

run:
python -m keplermind.app.main $(ARGS)

test:
pytest -q

clean:
rm -rf __pycache__ */__pycache__ *.pyc *.pyo .pytest_cache keplermind/assets/outputs/*
