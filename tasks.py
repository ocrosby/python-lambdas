import os
import shutil
import tempfile
import zipfile

from invoke import task

def create_zip_from_directory(c, source_dir, zip_file):
    """Create a ZIP file from a directory."""
    c.run(f"echo 'Creating ZIP file {zip_file} from directory {source_dir} ...'")
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as archive:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = str(os.path.join(root, file))
                archive_name = os.path.relpath(file_path, source_dir)
                c.run(f"echo 'Adding {file_path} as {archive_name} ...'")
                archive.write(file_path, archive_name)

@task
def clean(c):
    """Clean the project"""
    c.run("echo 'Cleaning the project'")

    egg_info = 'project.egg-info'
    if os.path.exists(egg_info):
        print(f"Removing '{egg_info}' ...")
        shutil.rmtree(egg_info)

    build_dir = 'build'
    if os.path.exists(build_dir):
        print(f"Removing '{build_dir}' ...")
        shutil.rmtree(build_dir)

    dist_dir = 'dist'
    if os.path.exists(dist_dir):
        print(f"Removing '{dist_dir}' ...")
        shutil.rmtree(dist_dir)

@task(aliases=["i"])
def install(c):
    """Install the project"""
    c.run("echo 'Installing the project'")
    c.run("pip install .")

@task
def lint(c):
    """Lint the project"""
    c.run("pylint lambdas/ tests/")

@task
def test(c):
    """Run the tests"""
    c.run("pytest")

@task(pre=[clean, lint, test])
def build(c):
    """Build the project"""
    c.run("echo 'Building the project'")

@task
def deploy(c):
    """Deploy the project"""
    c.run("echo 'Deploying the project'")

@task
def pack(c, name):
    """Package a Lambda function by name"""
    lambda_dir = f"lambdas/{name}"
    zip_file = f"dist/{name}.zip"

    if not os.path.exists(lambda_dir):
        c.run(f"echo 'Lambda directory {lambda_dir} does not exist.'")
        return

    if not os.path.exists('dist'):
        os.makedirs('dist')

    with tempfile.TemporaryDirectory() as staging_dir:
        for root, dirs, files in os.walk(lambda_dir):
            for current_dir in dirs:
                src_dir = os.path.join(root, current_dir)
                dst_dir = os.path.join(staging_dir, os.path.relpath(src_dir, lambda_dir))

                if '__pycache__' in dst_dir:
                    continue

                if not os.path.exists(dst_dir):
                    c.run(f"echo 'Creating directory {dst_dir} ...'")
                    os.makedirs(dst_dir)

            for current_file in files:
                if current_file == 'requirements.txt':
                    continue

                src_file = os.path.join(root, current_file)
                dst_file = os.path.join(staging_dir, os.path.relpath(src_file, lambda_dir))

                c.run(f"echo 'Copying {src_file} to {dst_file} ...'")
                shutil.copy2(src_file, dst_file)

        requirements_path = os.path.join(lambda_dir, 'requirements.txt')
        if os.path.exists(requirements_path):
            c.run(f"pip install --target {staging_dir} --upgrade -r {requirements_path} -v")

        create_zip_from_directory(c, staging_dir, zip_file)

@task
def pack_layer(c, name):
    """Package a Lambda layer by name"""
    layer_dir = f"layers/{name}"
    zip_file = f"dist/{name}.zip"

    if not os.path.exists(layer_dir):
        c.run(f"echo 'Layer directory {layer_dir} does not exist.'")
        return

    if not os.path.exists('dist'):
        os.makedirs('dist')

    with tempfile.TemporaryDirectory() as staging_dir:
        for root, dirs, files in os.walk(layer_dir):
            for current_file in files:
                src_file = os.path.join(root, current_file)
                dst_file = os.path.join(staging_dir, os.path.relpath(src_file, layer_dir))

                c.run(f"echo 'Copying {src_file} to {dst_file} ...'")
                shutil.copy2(src_file, dst_file)

        requirements_path = os.path.join(layer_dir, 'requirements.txt')
        if os.path.exists(requirements_path):
            c.run(f"pip install --target {staging_dir} --upgrade -r {requirements_path} -v")

        create_zip_from_directory(c, staging_dir, zip_file)

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

@task(pre=[clean])
def pack_all_layers(c):
    """Package all Lambda layers"""
    layers_dir = 'layers'

    if not os.path.exists(layers_dir):
        print(f"Layers directory '{layers_dir}' does not exist.")
        return

    for name in os.listdir(layers_dir):
        c.run(f"echo 'Packaging {name} ...'")
        layer_dir = os.path.join(layers_dir, name)
        if os.path.isdir(layer_dir):
            pack_layer(c, name)

@task(default=True, pre=[build])
def default(c):
    """Default task"""
    c.run("echo 'Running the default task'")