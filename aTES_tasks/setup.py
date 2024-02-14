import os

from importlib.machinery import SourceFileLoader
from pkg_resources import parse_requirements
from setuptools import setup, find_packages

MODULE_NAME = 'task_tracker'

module = SourceFileLoader(
    MODULE_NAME, os.path.join(MODULE_NAME, '__init__.py')
).load_module(MODULE_NAME)


def load_requirements(fname: str) -> list:
    requirements = []
    with open(fname, 'r') as f:
        for req in parse_requirements(f.read()):
            extras = '[{}]'.format(','.join(req.extras)) if req.extras else ''
            requirements.append(
                '{}{}{}'.format(req.name, extras, req.specifier)
            )
    return requirements


setup(
    name=MODULE_NAME.replace('_', '-'),
    version=module.__version__,
    author=module.__author__,
    author_email=module.__email__,
    description=module.__doc__,
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=load_requirements('requirements.txt'),
    extras_require={
        'test': load_requirements('requirements-test.txt')
    },
    include_package_data=True,
)
