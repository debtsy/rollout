# Rollout
o

    asdklfj

# Development

    python3 setup.py install  # installs dependencies
    python3 setup.py develop  # installs live version for editing

# Tasks

- unify the configuration. transform the old format to new.
    recursively check parent dir for config dir.
    that way you can have the folder version controlled and shared between projects, but can still be invoked from child dir.
    dir name must be .rollout. might make that configurable. or at least an env var.
    ;w
