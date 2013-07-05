##
## Environment Setup:
##
## (Note: bin/institute_makefile.py specifies similar variables seperatly)
##
include makefile.docs
-include build/makefile.projects

PROJECTS_DIR = ~/projects
PUBLISH_DIR = $(PROJECTS_DIR)/output
SPHINX_TYPE = dirhtml

##
## Makefile boilerplate
##

.PHONY: push deploy setup clean rebuild clean-all help
.DEFAULT_GOAL = help

help:
	@echo "Use the following targets to build and deploy the Cyborg Institute:"
	@echo ""
	@echo "	   rebuild	  - rebuild all institute sites."
	@echo "	   stage	  - stage a deployments of the Institute content."
	@echo "	   push		  - move all updated content to the production environment."
	@echo "	   push-stage	  - move all updated content to the live staging environment."
	@echo "	   themes	  - reimport themes to all Institute projects (as needed.)"
	@echo ""
	@echo "	   clean	  - remove $(BUILDDIR)/ and its contents."
	@echo "	   clean-all	  - remove $(PUBLISH_DIR)/ and build directories for all projects."
	@echo "	   clean-theme	  - remove theme files for all institute projects."
	@echo ""
	@echo "Note: all default Sphinx targets are avalible."

##
## Setup and dependency establishment
##

setup:issues $(BUILDDIR) github build/makefile.projects source/projects/csc.txt source/projects/taskn.txt
github:
	@python bin/configure_repos.py
build/makefile.projects:bin/institute_makefile.py
	@python $<
	@echo "[build] regenerated $@"
.PHONY:source/projects/buildfile.txt 
source/projects/%.txt:../%/README.rst
	@mkdir -p source/projects/
	@cp $< $@
	@echo "[build]: imported $@ from project README"

$(PROJECTS_DIR)/output/:makefile.projects
	mkdir -p $@
$(PROJECTS_DIR)/output/issues:
	mkdir -p $@
$(PROJECTS_DIR)/output/issues/index.html:issues/index.html
	cp $< $@
issues:$(PROJECTS_DIR)/output/issues $(PROJECTS_DIR)/output/issues/index.html
$(BUILDDIR):
	mkdir $@

##
## Meta-worker targets for building and migration
##

push:themes stage $(PUBLISH_DIR)/administration/sitemap.xml.gz $(PUBLISH_DIR)/institute/sitemap.xml.gz
	rsync -arz $(PUBLISH_DIR)/ institute@foucault.cyborginstitute.net:/home/institute/public
push-stage:themes stage
	rsync -arz $(PUBLISH_DIR)/ institute@foucault.cyborginstitute.net:/home/institute/staging
stage-push:push-stage

## 
## Sitemap Builders
##

.PHONY: sitemap $(PUBLISH_DIR)/administration/sitemap.xml.gz $(PUBLISH_DIR)/institute/sitemap.xml.gz

sitemap:
$(PUBLISH_DIR)/administration/sitemap.xml.gz:
	@python2 bin/sitemap_gen.py --config=bin/sitemap-admin.conf --testing  >/dev/null 2>&1
	@echo [build]: sitemap generated for administration
$(PUBLISH_DIR)/institute/sitemap.xml.gz:
	@python2 bin/sitemap_gen.py --config=bin/sitemap-institute.conf --testing  >/dev/null 2>&1
	@echo [build]: sitemap generated for institute

##
## Institute Site Specific publication system
##

# $(BUILDDIR)/latex/institute.tex:latex
# $(BUILDDIR)/epub/institute.epub:epub
# $(BUILDDIR)/latex/institute.pdf:$(BUILDDIR)/latex/institute.tex
# $(BUILDDIR)/publish/institute.epub:$(BUILDDIR)/epub/institute.epub
#	cp $< $@

$(BUILDDIR)/dirhtml:dirhtml
$(BUILDDIR)/publish:$(BUILDDIR)/dirhtml
	mkdir -p $@
	cp -R $</* $@
	touch $(CURDIR)/source/index.html

$(BUILDDIR)/publish/institute.pdf:$(BUILDDIR)/latex/institute.pdf
	cp $< $@

##
## Force Rebuilders
##

clean:
	-rm -rf $(BUILDDIR)/*
	-rm -rf makefile.projects
clean-stage:
	-rm -rf $(PUBLISH_DIR)/*
