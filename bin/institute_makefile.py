#!/usr/bin/python3

OUTPUT_FILE = "build/makefile.projects"

THEME_NAME = "cyborg"

project_info = [
  # ( project, has-docs-dir ),
    ("taskfile", True),
    ("stack", True),
    ("stl", True),
    ("csc", True),
    ("cyborg-admin", False),
    ("institute", False)
]

JOB = "\n\t"
TARGET = "\n"

class Projects:
    def generate_project(projects):
        build_info = []

        for (project, build) in projects:
            if build == True:
                build = "docs/build/$(SPHINX_TYPE)"
                theme_path = "docs/themes/" + THEME_NAME
            else:
                build = "build/$(SPHINX_TYPE)"
                theme_path = "themes/" + THEME_NAME

            output = "$(PROJECTS_DIR)/output/" + project
            source = "$(PROJECTS_DIR)/" + project + "/" + build
            command = "$(PROJECTS_DIR)/" + project + " $(SPHINX_TYPE)"
            theme = ("$(PROJECTS_DIR)/" + project + "/" + theme_path +
                     ":" + "$(PROJECTS_DIR)/institute/themes/" + THEME_NAME)

            if project == "institute":
                theme = ""

            item = (output, source, command, theme)
            build_info.append(item)

        return build_info

    def project_list(build_info):
        output_list = []
        source_list = []
        theme_list = []

        for (output, source, command, theme) in build_info:
            output_list.append(output)
            source_list.append(source)
            theme_list.append(theme)

        return output_list, source_list, theme_list

    build_info = generate_project(project_info)
    outputs, sources, themes = project_list(build_info)

class Targets:
    def builders(build_info):
        makefile_contents = []

        for (output, source, command, theme) in build_info:
            item_build  = (TARGET + output + ":" + source +
                           JOB + "cp -R $< $@" +
                           TARGET + source + ":"  +
                           JOB + "$(MAKE) -C " + command)
            if theme == "":
                theme_build = ""
            else:
                theme_build = (TARGET + theme +
                               JOB + "cp -R $< $@")

            makefile_contents.append(item_build + theme_build + "\n\n")

        return makefile_contents

    def interactors(outputs, sources, themes):
        deploy = "deploy: setup "

        for output in outputs:
            deploy =  deploy + output + " "

        rebuild = "rebuild: "
        clean_all = ("clean-all:" +
                     JOB + "-rm -rf $(PROJECTS_DIR)/output" +
                     JOB + "-rm -rf ")

        for source in sources:
            rebuild = rebuild + source + " "
            clean_all = clean_all + source + " "

        deploy = deploy + "\n\n"
        rebuild = rebuild + "\n\n"
        clean_all = clean_all + "\n\n"

        theme_target = "themes: "

        for theme in themes:
            theme_target = theme_target + theme.split(":")[0] + " "

        theme_target = theme_target + "\n\n"

        return deploy, rebuild, clean_all, theme_target

class InstituteMakefile:
    project_builders = Targets.builders(Projects.build_info)

    deploy, rebuild, clean_all, themes = Targets.interactors(Projects.outputs,
                                                             Projects.sources,
                                                             Projects.themes)

########################################################################

def main():
    makefile = open(OUTPUT_FILE, "w")

    makefile.write(InstituteMakefile.rebuild)

    for line in InstituteMakefile.project_builders:
        makefile.write(line)

    makefile.write(InstituteMakefile.deploy)
    makefile.write(InstituteMakefile.themes)
    makefile.write(InstituteMakefile.clean_all)

    makefile.close()

if __name__ == "__main__":
    main()
