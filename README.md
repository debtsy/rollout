# Rollout

# Getting Started

    /usr/local/bin/pip3 -q install -e "git+git@github.com:debtsy/rollout.git#egg=rollout"

# Development

If you want to develop it, replace the above install with:

    python3 setup.py develop

# Tasks

- unify the configuration. transform the old format to new.
    recursively check parent dir for config dir.
    that way you can have the folder version controlled and shared between projects, but can still be invoked from child dir.
    dir name must be .rollout. might make that configurable. or at least an env var.
    ;w
