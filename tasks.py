import os
import shutil
import glob
import zipfile
import tempfile
import venv

from invoke import task, Context

def remove_directory(c: Context, dir_path: str):
    """
    Remove a directory

    :param c: The Invoke context
    :param dir_path: The directory path to be removed
    :return: None
    """
    if os.path.exists(dir_path):
        c.run(f"echo 'Removing {dir_path} ...'")
        shutil.rmtree(dir_path)

def create_zip_from_directory(c, source_dir: str, zip_file: str):
    """
    Create a ZIP file from a directory

    :param c: The Invoke context
    :param source_dir: The source directory to be zipped
    :param zip_file: The ZIP file to be created
    :return: None
    """
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zf.write(file_path, arcname)
    c.run(f"echo 'Packaged {source_dir} into {zip_file}'")

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

    # Remove the dist directory
    dist_dir = 'dist'
    if os.path.exists(dist_dir):
        print(f"Removing '{dist_dir}' ...")
        shutil.rmtree(dist_dir)

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


@task
def pack(c, name):
    """Package a Lambda function by name"""
    lambda_dir = f"lambdas/{name}"
    zip_file = f"dist/{name}.zip"

    if not os.path.exists(lambda_dir):
        c.run(f"echo 'Lambda directory '{lambda_dir}' does not exist.'")
        return

    if not os.path.exists('dist'):
        os.makedirs('dist')

    with tempfile.TemporaryDirectory() as staging_dir:
        # Create a virtual environment in the staging directory
        # venv.create(staging_dir, with_pip=True)

        for root, dirs, files in os.walk(lambda_dir):
            for current_dir in dirs:
                src_dir = os.path.join(root, current_dir)
                dst_dir = os.path.join(staging_dir, os.path.relpath(src_dir, lambda_dir))

                if '__pycache__' in dst_dir:
                    continue

                if not os.path.exists(dst_dir):
                    c.run(f"echo 'Creating directory {dst_dir} ...'")
                    # shutil.copytree(src_dir, dst_dir)
                    os.makedirs(dst_dir)

            for current_file in files:
                if current_file == 'requirements.txt':
                    continue

                src_file = os.path.join(root, current_file)
                dst_file = os.path.join(staging_dir, os.path.relpath(src_file, lambda_dir))

                c.run(f"echo 'Copying {src_file} to {dst_file} ...'")
                shutil.copy2(src_file, dst_file)

        # Install dependencies if requirements.txt exists
        # c.run(f"echo 'Installing dependencies for {name} ...'")
        # requirements_path = os.path.join(lambda_dir, 'requirements.txt')
        # if os.path.exists(requirements_path):
        #     c.run(f"pip install --target {staging_dir} --upgrade -r {requirements_path} -v")

        # Create a ZIP file from the staging directory
        create_zip_from_directory(c, lambda_dir, zip_file)


@task(pre=[clean])
def pack_all(c):
    """Package all Lambda functions"""
    lambdas_dir = 'lambdas'

    if not os.path.exists(lambdas_dir):
        print(f"Lambdas directory '{lambdas_dir}' does not exist.")
        return

    for name in os.listdir(lambdas_dir):
        c.run(f"echo 'Packaging {name} ...'")
        lambda_dir = os.path.join(lambdas_dir, name)
        if os.path.isdir(lambda_dir):
            pack(c, name)


@task(default=True, pre=[build])
def default(c):
    """Default task"""
    c.run("echo 'Running the default task'")
    # Add more default steps here
