# Copyright (C) 2012-2014 Bastian Kleineidam
"""
Functions to load plugin modules.

Example usage::

    modules = loader.get_package_modules('plugins')
    plugins = loader.get_plugins(modules, PluginClass)
"""
import os
import importlib.util
import pkgutil

from .fileutil import is_writable_by_others


def check_writable_by_others(filename):
    """Check if file is writable by others on POSIX systems.
    On non-POSIX systems the check is ignored."""
    if os.name != 'posix':
        # XXX on non-posix systems other bits are relevant
        return
    return is_writable_by_others(filename)


def get_package_modules(packagename, packagepath):
    """Find all valid modules in the given package which must be a folder
    in the same directory as this loader.py module. A valid module has
    a .py extension, and is importable.

    @return: all loaded valid modules
    @rtype: iterator of module
    """
    for mod in pkgutil.iter_modules(packagepath):
        if not mod.ispkg:
            try:
                name = f"..{packagename}.{mod.name}"
                yield importlib.import_module(name, __name__)
            except ImportError as msg:
                print(_("WARN: could not load module %s: %s") % (mod.name, msg))


def get_folder_modules(folder, parentpackage):
    """."""
    if check_writable_by_others(folder):
        print("ERROR: refuse to load modules from world writable folder %r" % folder)
        return
    for filename in get_importable_files(folder):
        fullname = os.path.join(folder, filename)
        modname = parentpackage + "." + filename[:-3]
        try:
            spec = importlib.util.spec_from_file_location(modname, fullname)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            yield module
        except ImportError as msg:
            print(_("WARN: could not load file %s: %s") % (fullname, msg))


def get_importable_files(folder):
    """Find all module files in the given folder that end with '.py' and
    don't start with an underscore.

    @return: module names
    @rtype: iterator of string
    """
    for fname in os.listdir(folder):
        if fname.endswith('.py') and not fname.startswith('_'):
            fullname = os.path.join(folder, fname)
            if check_writable_by_others(fullname):
                print(
                    "ERROR: refuse to load module from world writable file %r"
                    % fullname
                )
            else:
                yield fname


def get_plugins(modules, classes):
    """Find all given (sub-)classes in all modules.

    @param modules: the modules to search
    @type modules: iterator of modules
    @return: found classes
    @rtype: iterator of class objects
    """
    for module in modules:
        yield from get_module_plugins(module, classes)


def get_module_plugins(module, classes):
    """Return all subclasses of a class in the module.
    If the module defines __all__, only those entries will be searched,
    otherwise all objects not starting with '_' will be searched.
    """
    try:
        names = module.__all__
    except AttributeError:
        names = [x for x in vars(module) if not x.startswith('_')]
    for name in names:
        try:
            obj = getattr(module, name)
        except AttributeError:
            continue
        try:
            for classobj in classes:
                if issubclass(obj, classobj):
                    yield obj
        except TypeError:
            continue
