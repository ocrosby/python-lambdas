import os
import shutil
import glob

from invoke import task

@task
def install(c):
    """Install the dependencies"""
    c.run("pip install --upgrade pip")
    c.run("pip install .")

@task
def clean(c):
    """Clean up the project"""
    c.run("echo 'Cleaning up'")

    # Remove any *.egg-info directories
    for egg_info in glob.glob('*.egg-info'):
        print(f"Removing '{egg_info}' ...")
        shutil.rmtree(egg_info)

    # Remove the build directory
    build_dir = 'build'
    if os.path.exists(build_dir):
        print(f"Removing '{build_dir}' ...")
        shutil.rmtree(build_dir)

@task(pre=[install])
def lint(c):
    """Lint the project"""
    c.run("pylint lambdas/ tests/")


@task()
def test(c):
    """Run the tests"""
    c.run("pytest")

@task(pre=[clean, lint, test])
def build(c):
    """Build the project"""
    c.run("echo 'Building the project'")
    # Add more build steps here

@task
def deploy(c):
    """Deploy the project"""
    c.run("echo 'Deploying the project'")
    # Add more deploy steps here


@task(default=True, pre=[build])
def default(c):
    """Default task"""
    c.run("echo 'Running the default task'")
    # Add more default steps here
