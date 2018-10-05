from setuptools import setup
import unittest


def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('test', pattern='test_*.py')
    return test_suite


setup(name='rollout',
      version='0.1.0',
      description='deployment tool',
      url='http://github.com/kespindler/rollout',
      author='Kurt Spindler',
      author_email='kespindler@gmail.com',
      license='MIT',
      packages=['rollout'],
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'rollout=rollout.cli:main',
          ],
      },
      test_suite='setup.my_test_suite',
      install_requires=[
          "boto3",
          "paramiko",
          "PyYAML",
          "Jinja2",
      ],
      )
