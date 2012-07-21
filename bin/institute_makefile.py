#!/usr/bin/python

import os.path
from institute_config import project_info

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
        theme = (PROJECTS_DIR + project_path + "/themes/" + THEME_NAME +
                 ":" + PROJECTS_DIR + "/institute/themes/" + THEME_NAME)

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
    makefile_contents = []

    for (output, source, command, theme, base) in build_info:
        item_build  = (
                       TARGET + source + ":" + base + "dirhtml" +
                       JOB + "$(MAKE) -C " + command + " " + SPHINX_TYPE +
                       TARGET + source + ":"  + base + "dirhtml" +
                       TARGET + base + "dirhtml:" +
                       JOB + "$(MAKE) -C " + command + " dirhtml"
                      )

        if theme == "":
            theme_build = ""
        else:
            theme_build = (
                           TARGET + output + ":" + source +
                           JOB + "mkdir -p $@" +
                           JOB + "cp -R $</* $@" +
                           JOB + "touch " + command + "/source/index.txt" +
                           TARGET + theme +
                           JOB + "mkdir -p $@" +
                           JOB + "cp -R $</* $@" +
                           TARGET + command + "/makefile.docs:" + PROJECTS_DIR + "/institute/makefile.docs" +
                           JOB + "cp $< $@"
                          )

        makefile_contents.append(item_build + theme_build + "\n\n")

    return makefile_contents

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

    for theme in themes:
        mtheme = theme.split(":")[0]
        theme_target = theme_target + " " + mtheme
        clean_theme = clean_theme + " " + mtheme
        if len(mtheme) > 0: 
            buildsystem = buildsystem + root_path_munger(mtheme) + "/makefile.docs "

       
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

makefile = InstituteMakefile()

########################################################################

def main():
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
