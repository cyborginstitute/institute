##
## Environment Setup:
##

include makefile.docs
-include build/makefile.projects

BUILD_DIR = build
PROJECTS_DIR = ~/projects
SPHINX_TYPE = dirhtml

##
## Makefile boilerplate
##

.PHONY: push deploy setup clean rebuild clean-all help

build/makefile.projects:bin/institute_makefile.py
	python $<

help:
	@echo "Use the following targets to build and deploy the Cyborg Institute:"
	@echo ""
	@echo "	   rebuild - rebuild all institute sites."
	@echo "	   deploy - stage a deployments of the Institute content."
	@echo "	   push - move all updated content to the production environment."
	@echo "	   themes - rebuild all themes as needed"
	@echo ""
	@echo ""
	@echo "Note: all default Sphinx targets are avalible."
	@echo ""

##
## Setup and dependency establishment
##

setup:$(PROJECTS_DIR)/output/issues $(BUILD_DIR)

$(PROJECTS_DIR)/output/issues:
	mkdir -p $@
$(BUILD_DIR):
	mkdir $@

##
## Meta-worker targets for building and migration
##

push:deploy
	rsync -arz $(PUBLISHDIR) institute@foucault.cyborginstitute.net:/srv/www/cyborginstitute/public

##
## Force Rebuilders
##

clean:
	-rm -rf $(BUILD_DIR)/*
clean-deploy:
	-rm -rf $(PUBLISH_DIR)/*
