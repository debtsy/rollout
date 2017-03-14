from setuptools import setup


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
)
