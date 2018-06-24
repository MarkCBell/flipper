
import os
from hypothesis import settings, Verbosity, HealthCheck
import pytest

def pytest_addoption(parser):
    parser.addoption('--runslow', action='store_true', help='run slow tests')

def pytest_collection_modifyitems(config, items):
    if not config.getoption('--runslow'):
        skip_slow = pytest.mark.skip(reason='need --runslow option to run')
        for item in items:
            if 'slow' in item.keywords:
                item.add_marker(skip_slow)


settings.register_profile('ci', settings(deadline=None, suppress_health_check=(HealthCheck.too_slow,)))
settings.register_profile('dev', settings(deadline=None, suppress_health_check=(HealthCheck.too_slow,), max_examples=5))
settings.register_profile('debug', settings(deadline=None, suppress_health_check=(HealthCheck.too_slow,), max_examples=5, verbosity=Verbosity.verbose))
settings.load_profile(os.getenv(u'HYPOTHESIS_PROFILE', 'dev'))

