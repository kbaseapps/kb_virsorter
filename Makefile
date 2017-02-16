SERVICE = kb_virsorter
SERVICE_CAPS = kb_virsorter
SPEC_FILE = kb_virsorter.spec
URL = https://kbase.us/services/kb_virsorter
DIR = $(shell pwd)
LIB_DIR = lib
SCRIPTS_DIR = scripts
TEST_DIR = test
DATA_DIR = data_targz
LBIN_DIR = bin
EXECUTABLE_SCRIPT_NAME = run_$(SERVICE_CAPS)_async_job.sh
STARTUP_SCRIPT_NAME = start_server.sh
TEST_SCRIPT_NAME = run_tests.sh

.PHONY: test

default: compile

all: compile build build-startup-script build-executable-script build-test-script

compile:
	kb-sdk compile $(SPEC_FILE) \
		--out $(LIB_DIR) \
		--plclname $(SERVICE_CAPS)::$(SERVICE_CAPS)Client \
		--jsclname javascript/Client \
		--pyclname $(SERVICE_CAPS).$(SERVICE_CAPS)Client \
		--javasrc src \
		--java \
		--pysrvname $(SERVICE_CAPS).$(SERVICE_CAPS)Server \
		--pyimplname $(SERVICE_CAPS).$(SERVICE_CAPS)Impl;

build:
	chmod +x $(SCRIPTS_DIR)/entrypoint.sh

build-executable-script:
	mkdir -p $(LBIN_DIR)
	echo '#!/bin/bash' > $(LBIN_DIR)/$(EXECUTABLE_SCRIPT_NAME)
	echo 'script_dir=$$(dirname "$$(readlink -f "$$0")")' >> $(LBIN_DIR)/$(EXECUTABLE_SCRIPT_NAME)
	echo 'export PYTHONPATH=$$script_dir/../$(LIB_DIR):$$PATH:$$PYTHONPATH' >> $(LBIN_DIR)/$(EXECUTABLE_SCRIPT_NAME)
	echo 'python -u $$script_dir/../$(LIB_DIR)/$(SERVICE_CAPS)/$(SERVICE_CAPS)Server.py $$1 $$2 $$3' >> $(LBIN_DIR)/$(EXECUTABLE_SCRIPT_NAME)
	chmod +x $(LBIN_DIR)/$(EXECUTABLE_SCRIPT_NAME)

build-startup-script:
	mkdir -p $(LBIN_DIR)
	echo '#!/bin/bash' > $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)
	echo 'script_dir=$$(dirname "$$(readlink -f "$$0")")' >> $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)
	echo 'export KB_DEPLOYMENT_CONFIG=$$script_dir/../deploy.cfg' >> $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)
	echo 'export PYTHONPATH=$$script_dir/../$(LIB_DIR):$$PATH:$$PYTHONPATH' >> $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)
	echo 'uwsgi --master --processes 5 --threads 5 --http :5000 --wsgi-file $$script_dir/../$(LIB_DIR)/$(SERVICE_CAPS)/$(SERVICE_CAPS)Server.py' >> $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)
	chmod +x $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)

build-test-script:
	echo '#!/bin/bash' > $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	echo 'script_dir=$$(dirname "$$(readlink -f "$$0")")' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	echo 'export KB_DEPLOYMENT_CONFIG=$$script_dir/../deploy.cfg' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	echo 'export KB_AUTH_TOKEN=`cat /kb/module/work/token`' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	echo 'export PYTHONPATH=$$script_dir/../$(LIB_DIR):$$PATH:$$PYTHONPATH' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	echo 'cd $$script_dir/../$(TEST_DIR)' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	echo 'python -u -m unittest discover -p "*_test.py"' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	chmod +x $(TEST_DIR)/$(TEST_SCRIPT_NAME)

test:
	if [ ! -f /kb/module/work/token ]; then echo -e '\nOutside a docker container please run "kb-sdk test" rather than "make test"\n' && exit 1; fi
	bash $(TEST_DIR)/$(TEST_SCRIPT_NAME)

clean:
	rm -rfv $(LBIN_DIR)

ref-data:
	pwd
	mkdir /kb/module/virsorter_run
	curl -X GET https://ci.kbase.us/services/shock-api/node/ab30145e-082a-4844-a2dc-bfb744b5b180?download_raw > /data/PFAM_27.tar.gz
	tar -zxvf /data/PFAM_27.tar.gz -C /data
	curl -X GET https://ci.kbase.us/services/shock-api/node/b815a972-6314-4d48-9e32-ada8a575d004?download_raw > /data/Phage_gene_catalog.tar.gz
	tar -zxvf /data/Phage_gene_catalog.tar.gz -C /data
	curl -X GET https://ci.kbase.us/services/shock-api/node/c188e7a7-783c-42f3-9d6f-bbd32ef60e3d?download_raw > /data/Phage_gene_catalog_plus_viromes.tar.gz
	tar -zxvf /data/Phage_gene_catalog_plus_viromes.tar.gz -C /data

	curl -H "Authorization: OAuth $KB_AUTH_TOKEN" -X GET https://ci.kbase.us/services/shock-api/node/b38ff5b0-6fcc-40e1-b2d0-c5af1407a868?download_raw > /data/Generic_ref_file.refs
	curl -H "Authorization: OAuth $KB_AUTH_TOKEN" -X GET https://ci.kbase.us/services/shock-api/node/555a94de-593e-4d88-8fcf-d07b4e0d98cd?download_raw > /data/VirSorter_Readme.txt
	curl -H "Authorization: OAuth $KB_AUTH_TOKEN" -X GET https://ci.kbase.us/services/shock-api/node/6ddcad27-0218-4d28-b467-79b55cd6c96e?download_raw > /data/VirSorter_Readme_viromes.txt

	ls -lh /data
	echo "Printed ls -lh /data"
	touch /data/__READY__
