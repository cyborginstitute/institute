#!/usr/bin/python

import os.path
from institute_config import project_info
from makefile_builder import MakefileBuilder

OUTPUT_FILE = "build/makefile.projects"

THEME_NAME = "cyborg"

SPHINX_TYPE = "publish"
PROJECTS_DIR = "~/projects"

JOB = "\n\t"
TARGET = "\n"

######################################################################

def generate_build_info(project, build):
    if build == True:
        project_path = "/" + project + "/docs"
    else:
        project_path = "/" + project

    output = PROJECTS_DIR + "/output/" + project
    source = PROJECTS_DIR + project_path + "/build/" + SPHINX_TYPE
    command = PROJECTS_DIR + project_path
    base = PROJECTS_DIR + project_path + "/build/"

    if project == "institute":
        theme = ""
    else:
        theme = (PROJECTS_DIR + project_path + "/themes/" + THEME_NAME,
                 PROJECTS_DIR + "/institute/themes/" + THEME_NAME)

    item = (output, source, command, theme, base)

    return item

def project_list(build_info):
    output_list = []
    source_list = []
    theme_list = []

    for (output, source, command, theme, base) in build_info:
        output_list.append(output)
        source_list.append(source)
        theme_list.append(theme)

    return output_list, source_list, theme_list

def makefile_builders(build_info):

    m = MakefileBuilder()

    for (output, source, command, theme, base) in build_info:
        m.section_break(command)
        m.target(source, base + 'dirhtml')
        m.job('$(MAKE) -C ' + command + ' ' + SPHINX_TYPE)
        m.msg('[institute]: building ' + SPHINX_TYPE + 'build taks in ' + command)
        m.target(base + 'dirhtml')
        m.job('$(MAKE) -C ' + command + ' dirhtml')
        m.msg('[dirhtml]: building in ' + command)

        if theme == "":
            pass
        else:
            m.target(output, source)
            m.job('mkdir -p $@')
            m.msg('[build]: created $@')
            m.job('cp -R $</* $@')
            m.msg('[build]: migrated $< to $@')
            m.job('touch ' + command + '/source/index.txt')
            m.msg('[build]: touching /source/index.txt to ensure a clean build')


            m.comment('theme building instructions')
            m.target(theme[0], theme[1])
            m.job('mkdir -p $@')
            m.msg('[theme]: created $@')
            m.job('cp -R $</* $@')
            m.msg('[theme]: migrated $< to $@')
            
            m.comment('keeping the sphinx build system unified for ' + theme[0], block='second')
            m.target(command + "/makefile.docs", PROJECTS_DIR + "/institute/makefile.docs", block='second')
            m.job('cp $< $@', block='second')
            m.msg('[buildsysystem]: migrated $< to $@', block='second')

    return m.makefile

def root_path_munger(path):
    munge = path.split('/')
    munge.pop(-1)
    munge.pop(-1)
    o = os.path.join(*munge)

    return o

def makefile_interactors(outputs, sources, themes):
    stage = "stage: "

    for output in outputs:
        stage = stage + output + " "

    rebuild = "rebuild: "
    clean_all = ("clean-all:" +
                 JOB + "-rm -rf " + PROJECTS_DIR + "/output" +
                 JOB + "-rm -rf ")

    for source in sources:
        rebuild = rebuild + source + " "
        clean_all = clean_all + source + " "

    stage = stage + "\n\n"
    rebuild = rebuild + "\n\n"
    clean_all = clean_all + "\n\n"

    theme_target = "themes:"
    clean_theme = "clean-theme: " + JOB + "-rm -rf"
    buildsystem = "buildsystem:"

    for theme in [ theme for theme in themes if theme is not '' ]:
        theme_target = theme_target + " " + theme[0]
        clean_theme = clean_theme + " " + theme[0]
        if len(theme[0]) > 0: 
            buildsystem = buildsystem + root_path_munger(theme[0]) + "/makefile.docs "

       
    theme_target = theme_target + "\n\n"
    clean_theme = clean_theme + "\n\n"
    buildsystem = buildsystem + "\n\n"
    return stage, rebuild, clean_all, theme_target, clean_theme, buildsystem

########################################################################

class InstituteMakefile():
    def __init__(self):
        self.build_info = []

        for (project, build) in project_info:
            self.build_info.append(generate_build_info(project, build))

        self.builders = makefile_builders(self.build_info)
        (self.outputs, self.sources, self.themes) = project_list(self.build_info)

        (self.stage, self.rebuild, 
         self.clean_all, self.themes, 
         self.clean_theme, 
         self.buildsystem) = makefile_interactors(self.outputs, self.sources,
                                                  self.themes)

########################################################################

def main():
    makefile = InstituteMakefile()

    output = open(OUTPUT_FILE, "w")

    for line in makefile.builders:
        output.write(line)

    output.write(makefile.buildsystem)
    output.write(makefile.rebuild)
    output.write(makefile.stage)
    output.write(makefile.themes)
    output.write(makefile.clean_theme)
    output.write(makefile.clean_all)

    output.close()
    

if __name__ == "__main__":
    main()
