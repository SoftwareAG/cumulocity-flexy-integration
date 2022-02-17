import setuptools
import versioneer


with open("requirements/requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh]


setuptools.setup(
    name='ewon_flexy_integration',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    long_description=__doc__,
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
)
