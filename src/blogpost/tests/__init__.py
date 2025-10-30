# Make Django discover tests in this directory.
# Import test modules, but without importing * which can confuse discovery.
from . import tests, tests_api