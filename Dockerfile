# Minimal container that installs the package (core + dev tools) and can run the
# test suite. No GPU / deep-learning stack is needed. CI builds this image and runs
# `pytest -m "not slow"` inside it as a clean-environment smoke test.
FROM python:3.11-slim

# PyTables (the `tables` wheel) needs the HDF5 runtime; install it from apt.
RUN apt-get update \
 && apt-get install -y --no-install-recommends libhdf5-dev gcc \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN python -m pip install --upgrade pip \
 && python -m pip install --no-cache-dir -e ".[dev]"

# Default: run the fast test suite.
CMD ["pytest", "-m", "not slow"]
