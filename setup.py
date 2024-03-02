from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in portaltechtrixsystem_reports/__init__.py
from portaltechtrixsystem_reports import __version__ as version

setup(
	name="portaltechtrixsystem_reports",
	version=version,
	description="portal tech rix system",
	author="Safdar Ali",
	author_email="safdar211@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
