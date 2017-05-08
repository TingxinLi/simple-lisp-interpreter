
from setuptools import setup, find_packages

install_requires = [

]

version = '0.0.1'

setup(
    name='lisp-interpreter',
    version=version,
    description='Simple Lisp Interpreter',
    author='Travis Lee',
    install_requires=install_requires,
    packages=find_packages(),
)
