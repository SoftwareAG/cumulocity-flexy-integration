import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from zipfile import ZipFile
import zipfile

from dotenv import load_dotenv
from invoke import task

NAME = 'ewon-talk2m-integration'
MODULE_NAME = NAME.replace('-', '_')
DOT_ENV = '.env'
root_dir = './'

load_dotenv()


@task()
def init(c):
    """Initialized the project by installing python and other helpful setup tasks
    """
    c.run('pip install -r requirements/requirements.dev.txt')

    if not os.path.exists(DOT_ENV):
        shutil.copy2(f'{DOT_ENV}.template', DOT_ENV)
    else:
        print(f'dotenv file already exists: {DOT_ENV}')
    
    with open(Path.home() / '.bashrc', mode='a') as f:
        f.writelines([
            f'source $(readlink -f {root_dir}/scripts/.bashrc)',
        ])
    
    with open(Path.home() / '.zshrc', mode='a') as f:
        f.writelines([
            f'source $(readlink -f {root_dir}/scripts/.zshrc)',
        ])

@task()
def clean(c):
    """
    Delete build all files and artifacts
    """
    print('Cleaning artifacts')
    paths = ['image.tar', 'build']
    for i_path in paths:
        if os.path.isdir(i_path):
            print(f'Removing folder {i_path}')
            shutil.rmtree(i_path)
        elif os.path.isfile(i_path):
            print(f'Removing file {i_path}')
            os.remove(i_path)

#
# Lint
#
@task()
def lint(c):
    """Run linting
    """
    print('Running linting')
    c.run(f'pylint {MODULE_NAME}')


#
# Build
#

@task(clean)
def build_python(c):
    """
    Build the python project
    """
    print("Building python app")
    c.run('python setup.py build')
    _build_manifest()


@task(build_python)
def build_docker(c, name=NAME, no_cache=False):
    """
    Build docker image
    """
    print("Building docker image")
    options = ''
    if no_cache:
        options = '--no-cache'
    c.run(f'docker build {options} -f Dockerfile -t "{name}" .')


@task(build_python, build_docker, help={'name': "Name of the micorservice"})
def pack(c, name=NAME):
    """
    Build the microservice image
    """
    print('Packing docker image')
    c.run(f'docker save {name} > image.tar')

    target_zip = f'{name}.zip'
    if os.path.exists(target_zip):
        os.remove(target_zip)

    with ZipFile(target_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zipObj:
        zipObj.write('image.tar')
        zipObj.write('build/cumulocity.json', 'cumulocity.json')
    
    os.remove('image.tar')


@task(clean, build_python, build_docker, post=[pack])
def build(c):
    """
    Build app, docker image and create the Cumulocity zip file
    """
    print("Building python app and microservice")


@task()
def version(c):
    """
    Get the version of the microservice
    """
    print(f'Version: {_get_version()}')


def _get_version():
    """
    Get the version of the microservice from the built python microservice
    """
    return subprocess.check_output(
        ['python', '-c', 'import ewon_flexy_integration; print(ewon_flexy_integration.__version__);'],
        cwd='build/lib', universal_newlines=True).strip()


def _build_manifest():
    """
    Get the microservice version
    """
    print('Creating Cumulocity manifest file')
    manifest = {}
    with open('cumulocity.json') as fp:
        manifest = json.load(fp)
        manifest['version'] = format_c8y_version(_get_version())
    
    with open('build/cumulocity.json', mode='w') as fp:
        fp.write(json.dumps(manifest, indent=2))


def format_c8y_version(version: str, default_version='0.0.0') -> str:
    """Format c8y version string to confirm with semver which is enforced by c8y
    """
    semver = re.match(r'^\d+\.\d+\.\d+(-SNAPSHOT)?$', version)
    if semver:
        return version
        
    # Note: Cumulocity is strict with the version numbers, and only semver style
    # versions are accepted, so try to extact a semver version otherwise
    # default to 
    partial_version = re.search(r'^(\d+\.\d+\.\d+)', version)
    f_version = partial_version.group(1) if partial_version else default_version
    f_version += '-SNAPSHOT'
    return f_version


@task()
def deploy(c, name=NAME):
    """
    Deploy the microservice to Cumulocity
    """
    
    print(f'Deploying {name}.zip to Cumulocity ({os.getenv("C8Y_HOST")})')
    c.run(f'c8y microservices create --file "./{name}.zip" --verbose')


#
# Other useful tasks
#
@task()
def start_docker(c, name=NAME, env=DOT_ENV):
    """
    Run microservice in a local docker image (to validate production environment)
    """
    print("Starting microservice in local docker container")
    c.run(f'docker run --env-file "{env}" -p 5000:80 {name}')

#
# Testing
#
@task()
def test(c):
    """Run tests
    """
    print('Running tests')
    c.run(f'pytest tests')

@task
def start_production_local(c):
    """
    Start a local production server (not using docker)
    """
    c.run('gunicorn3 -c config.py -w 4 -b 0.0.0.0:5000 --log-level=debug server:app')
