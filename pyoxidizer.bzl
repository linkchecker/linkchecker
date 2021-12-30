def make_exe():
    dist = default_python_distribution()
    python_config = dist.make_python_interpreter_config()
    python_config.run_module = "linkcheck"
    exe = dist.to_python_executable(
        name="linkchecker",
        config=python_config,
    )
    exe.add_python_resources(exe.pip_install([CWD]))
    return exe

register_target("exe", make_exe)
resolve_targets()
