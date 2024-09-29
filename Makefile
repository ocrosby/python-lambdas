# Makefile

# Define the virtual environment directory
VENV_DIR = venv

# Define the Python executable within the virtual environment
PYTHON = $(VENV_DIR)/bin/python

# Define the pip executable within the virtual environment
PIP = $(VENV_DIR)/bin/pip

# Create the virtual environment
$(VENV_DIR)/bin/activate:
	python -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install .

# Install the project dependencies
install: $(VENV_DIR)/bin/activate
	$(PIP) install .

# Run invoke tasks
invoke: install
	$(PYTHON) -m invoke $(filter-out $@,$(MAKECMDGOALS))

# Clean the project
clean: $(VENV_DIR)/bin/activate
	$(PYTHON) -m invoke clean

# Build the project
build: $(VENV_DIR)/bin/activate
	$(PYTHON) -m invoke build

# Deploy the project
deploy: $(VENV_DIR)/bin/activate
	$(PYTHON) -m invoke deploy

# Prevent make from treating task names as files
.PHONY: install invoke clean build deploy