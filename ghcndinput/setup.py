from setuptools import setup, find_packages

setup(name='ghcndinput',
      version='0.1',
      description='Connector for accessing NOAA NCDC GHCND meterological datasets',
      url='http://github.com/geoedf/connectors',
      author='Rajesh Kalyanam',
      author_email='rkalyanapurdue@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=['cdo-api-py','pandas'],
      zip_safe=False)
