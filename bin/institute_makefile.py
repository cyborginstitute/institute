#!/usr/bin/python

OUTPUT_FILE = "build/makefile.projects"

THEME_NAME = "cyborg"

SPHINX_TYPE = "publish"
PROJECTS_DIR = "~/projects"

project_info = [
  # ( project, has-docs-dir ),
    ("taskfile", True),
    ("stack", True),
    ("stl", True),
#    ("csc", True),
    ("cyborg-admin", False),
    ("institute", False)
]

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
    command = PROJECTS_DIR + project_path + " "
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
                       TARGET + output + ":" + source +
                       JOB + "mkdir -p $@" +
                       JOB + "cp -R $</* $@" +
                       TARGET + source + ":"  +
                       JOB + "$(MAKE) -C " + command + SPHINX_TYPE +
                       TARGET + source + ":"  + base + "dirhtml" + 
                       TARGET + base + "dirhtml:" +
                       JOB + "$(MAKE) -C " + command + "dirhtml" +
                       JOB + "touch $@"
                       )

        if theme == "":
            theme_build = ""
        else:
            theme_build = (TARGET + theme +
                           JOB + "mkdir -p $@" +
                           JOB + "cp -R $</* $@")

        makefile_contents.append(item_build + theme_build + "\n\n")

    return makefile_contents

def makefile_interactors(outputs, sources, themes):
    stage = "stage: "
    # stage = "stage: setup "

    for output in outputs:
        stage =  stage + output + " "

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

    for theme in themes:
        theme_target = theme_target + " " + theme.split(":")[0]
        clean_theme = clean_theme + " " + theme.split(":")[0]

    theme_target = theme_target + "\n\n"
    clean_theme = clean_theme + "\n\n"

    return stage, rebuild, clean_all, theme_target, clean_theme

########################################################################

class InstituteMakefile():
    def __init__(self):
        self.build_info = []

        for (project, build) in project_info:
            self.build_info.append(generate_build_info(project, build))


        self.builders = makefile_builders(self.build_info)
        (self.outputs, self.sources, self.themes) = \
          project_list(self.build_info)

        (self.stage, self.rebuild, self.clean_all, self.themes, self.clean_theme) = \
          makefile_interactors(self.outputs, self.sources, self.themes)

makefile = InstituteMakefile()

########################################################################

def main():
    output = open(OUTPUT_FILE, "w")

    output.write(makefile.rebuild)

    for line in makefile.builders:
        output.write(line)

    output.write(makefile.stage)
    output.write(makefile.themes)
    output.write(makefile.clean_theme)
    output.write(makefile.clean_all)

    output.close()

if __name__ == "__main__":
    main()
