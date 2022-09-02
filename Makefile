VENV=.venv
PYTHON_VENV=$(VENV)/bin/python3
REQUIREMENTS=requirements.txt

BACKUP_SCRIPT=backup-github.py

TOKEN_FILE?=.token
GH_USER?=P-Miranda
CLONE_DIR?=clone_dir
ARCHIVE_DIR?=archive_dir

all: backup

backup: $(PYTHON_VENV)
	$(PYTHON_VENV) $(BACKUP_SCRIPT) $(TOKEN_FILE) $(GH_USER) $(CLONE_DIR) $(BACKUP_DIR)

$(PYTHON_VENV):
	python3 -m venv $(VENV)
	$(PYTHON_VENV) -m pip install --upgrade pip
	$(PYTHON_VENV) -m pip install -r $(REQUIREMENTS)

clean-all:
	@rm -rf $(CLONE_DIR) $(ARCHIVE_DIR)
