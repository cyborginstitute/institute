#!/usr/bin/python

import os
import subprocess
from institute_config import project_info

project_path = os.path.expanduser("~/projects") + "/"
repo_source = " gitosis@foucault.cyborginstitute.net:"

clone_queue = []
update_queue = []
github_queue = []
general_queue = []

def init_queues(project_info):
    for project, config in project_info:
        project_dir = project_path + project
        if os.path.isdir(project_dir):
            update_queue.append((project, project_dir))
            github_check(project, project_dir)
        else:
            clone_queue.append((project, repo_source + project + ".git"))
            github_queue.append((project, project_dir))


def git_operation(name, op="pull"):
    command = "git " + op + " >/dev/null"

    subprocess.call(command, shell=True)
    print("[repo] " + name + " " + op + " complete")

def github_check(project, project_dir, add_remote=False):
    os.chdir(project_dir)
    remotes = subprocess.check_output("git remote", shell=True).decode()

    if not "github" in remotes:
        github_queue.append((project, project_dir))
    else:
        general_queue.append((project, project_dir))

def worker():
    for name, command in clone_queue:
        os.chdir(project_path)
        git_operation(name, "clone" + command)
    for project, project_dir in github_queue:
        os.chdir(project_dir)
        git_operation("adding github remote to " + project,
                      "remote add github git@github.com:cyborginstitute/" +
                      project + ".git")
    for name, project_dir in update_queue:
        os.chdir(project_dir)
        git_operation(name)
    for name, project_dir in general_queue:
        os.chdir(project_dir)
        git_operation("pushing changes to gitub for " + name,
                      "push github")

def main():
    init_queues(project_info)
    worker()
    print("[repo] universe up to date")

if __name__ == "__main__":
    main()
