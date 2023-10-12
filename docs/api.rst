API
====

.. module:: microvenv

.. attribute:: IN_VIRTUAL_ENV

    A boolean representing whether the running interpreter is from a virtual
    environment.

.. attribute:: DEFAULT_ENV_DIR

    The default name of the virtual envirnoment directory created by
    :func:`create`. The value is ``.venv``.

.. autoexception:: ActivationError

.. autofunction:: parse_config

.. autofunction:: activation(env_vars=os.environ)

.. function:: create(env_dir=".venv", *, scm_ignore_files={"git"})

    Create a minimal virtual environment.

    Analogous to calling :py:func:`venv.create` as
    ``venv.create(..., symlinks=True, with_pip=False)``.

    .. note:: Not available on Windows.
