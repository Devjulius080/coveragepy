# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""Determine facts about the environment."""

import os
import platform
import sys

# Operating systems.
WINDOWS = sys.platform == "win32"
LINUX = sys.platform.startswith("linux")
OSX = sys.platform == "darwin"

# Python implementations.
CPYTHON = (platform.python_implementation() == "CPython")
PYPY = (platform.python_implementation() == "PyPy")
JYTHON = (platform.python_implementation() == "Jython")
IRONPYTHON = (platform.python_implementation() == "IronPython")

# Python versions. We amend version_info with one more value, a zero if an
# official version, or 1 if built from source beyond an official version.
PYVERSION = sys.version_info + (int(platform.python_version()[-1] == "+"),)

if PYPY:
    PYPYVERSION = sys.pypy_version_info

# Python behavior.
class PYBEHAVIOR:
    """Flags indicating this Python's behavior."""

    # Does Python conform to PEP626, Precise line numbers for debugging and other tools.
    # https://www.python.org/dev/peps/pep-0626
    pep626 = CPYTHON and (PYVERSION > (3, 10, 0, 'alpha', 4))

    # Is "if __debug__" optimized away?
    if PYPY:
        optimize_if_debug = True
    else:
        optimize_if_debug = not pep626

    # Is "if not __debug__" optimized away? The exact details have changed
    # across versions.
    if pep626:
        optimize_if_not_debug = 1
    elif PYPY:
        if PYVERSION >= (3, 9):
            optimize_if_not_debug = 2
        elif PYVERSION[:2] == (3, 8):
            optimize_if_not_debug = 3
        else:
            optimize_if_not_debug = 1
    else:
        if PYVERSION >= (3, 8, 0, 'beta', 1):
            optimize_if_not_debug = 2
        else:
            optimize_if_not_debug = 1

    # Can co_lnotab have negative deltas?
    negative_lnotab = not (PYPY and PYPYVERSION < (7, 2))

    # 3.7 changed how functions with only docstrings are numbered.
    docstring_only_function = (not PYPY) and ((3, 7, 0, 'beta', 5) <= PYVERSION <= (3, 10))

    # When a break/continue/return statement in a try block jumps to a finally
    # block, does the finally block do the break/continue/return (pre-3.8), or
    # does the finally jump back to the break/continue/return (3.8) to do the
    # work?
    finally_jumps_back = ((3, 8) <= PYVERSION < (3, 10))

    # When a function is decorated, does the trace function get called for the
    # @-line and also the def-line (new behavior in 3.8)? Or just the @-line
    # (old behavior)?
    trace_decorated_def = (CPYTHON and PYVERSION >= (3, 8)) or (PYPY and PYVERSION >= (3, 9))

    # Functions are no longer claimed to start at their earliest decorator even though
    # the decorators are traced?
    def_ast_no_decorator = (PYPY and PYVERSION >= (3, 9))

    # CPython 3.11 now jumps to the decorator line again while executing
    # the decorator.
    trace_decorator_line_again = (CPYTHON and PYVERSION > (3, 11, 0, 'alpha', 3, 0))

    # Are while-true loops optimized into absolute jumps with no loop setup?
    nix_while_true = (PYVERSION >= (3, 8))

    # CPython 3.9a1 made sys.argv[0] and other reported files absolute paths.
    report_absolute_files = (
        (CPYTHON or (PYPY and PYPYVERSION >= (7, 3, 10)))
        and PYVERSION >= (3, 9)
    )

    # Lines after break/continue/return/raise are no longer compiled into the
    # bytecode.  They used to be marked as missing, now they aren't executable.
    omit_after_jump = pep626

    # PyPy has always omitted statements after return.
    omit_after_return = omit_after_jump or PYPY

    # Modules used to have firstlineno equal to the line number of the first
    # real line of code.  Now they always start at 1.
    module_firstline_1 = pep626

    # Are "if 0:" lines (and similar) kept in the compiled code?
    keep_constant_test = pep626

    # When leaving a with-block, do we visit the with-line again for the exit?
    exit_through_with = (PYVERSION >= (3, 10, 0, 'beta'))

    # Match-case construct.
    match_case = (PYVERSION >= (3, 10))

    # Some words are keywords in some places, identifiers in other places.
    soft_keywords = (PYVERSION >= (3, 10))

    # Modules start with a line numbered zero. This means empty modules have
    # only a 0-number line, which is ignored, giving a truly empty module.
    empty_is_empty = (PYVERSION >= (3, 11, 0, 'beta', 4))

# Coverage.py specifics.

# Are we using the C-implemented trace function?
C_TRACER = os.getenv('COVERAGE_TEST_TRACER', 'c') == 'c'

# Are we coverage-measuring ourselves?
METACOV = os.getenv('COVERAGE_COVERAGE', '') != ''

# Are we running our test suite?
# Even when running tests, you can use COVERAGE_TESTING=0 to disable the
# test-specific behavior like contracts.
TESTING = os.getenv('COVERAGE_TESTING', '') == 'True'

USE_CONTRACTS = False

def debug_info():
    """Return a list of (name, value) pairs for printing debug information."""
    info = [
        (name, value) for name, value in globals().items()
        if not name.startswith("_") and
            name not in {"PYBEHAVIOR", "debug_info"} and
            not isinstance(value, type(os))
    ]
    info += [
        (name, value) for name, value in PYBEHAVIOR.__dict__.items()
        if not name.startswith("_")
    ]
    return sorted(info)
