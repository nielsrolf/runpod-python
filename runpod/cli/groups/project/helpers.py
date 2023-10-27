"""Helper functions for project group commands."""

import re
import os
import shutil
import click

from runpod import get_pods, create_pod
from runpod import error as rp_error

def validate_project_name(name):
    '''
    Validate the project name.
    '''
    match = re.search(r"[<>:\"/\\|?*\s]", name)
    if match:
        raise click.BadParameter(f"Project name contains an invalid character: '{match.group()}'.")
    return name

def get_project_pod(project_id: str):
    """Check if a project pod exists.
    Return the pod_id if it exists, else return None.
    """
    for pod in get_pods():
        if project_id in pod['name']:
            return pod['id']

    return None

def copy_template_files(template_dir, destination):
    """Copy the template files to the destination directory."""
    for item in os.listdir(template_dir):
        source_item = os.path.join(template_dir, item)
        destination_item = os.path.join(destination, item)
        if os.path.isdir(source_item):
            shutil.copytree(source_item, destination_item)
        else:
            shutil.copy2(source_item, destination_item)

def attempt_pod_launch(config, environment_variables):
    """Attempt to launch a pod with the given configuration."""
    for gpu_type in config['project'].get('gpu_types', []):
        print(f"Trying to get a pod with {gpu_type}... ", end="")
        try:
            created_pod = create_pod(
                f'{config["project"]["name"]}-dev ({config["project"]["uuid"]})',
                config['project']['base_image'],
                gpu_type,
                gpu_count=int(config['project']['gpu_count']),
                support_public_ip=True,
                ports=f'{config["project"]["ports"]}',
                network_volume_id=f'{config["project"]["storage_id"]}',
                volume_mount_path=f'{config["project"]["volume_mount_path"]}',
                container_disk_in_gb=int(config["project"]["container_disk_size_gb"]),
                env=environment_variables
            )
            print("Success!")
            return created_pod
        except rp_error.QueryError:
            print("Unavailable.")
    return None
