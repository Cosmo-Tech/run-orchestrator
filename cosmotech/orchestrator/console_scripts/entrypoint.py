import configparser
import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

from cosmotech.orchestrator.utils.click import click
from cosmotech.orchestrator.utils.logger import LOGGER

MODE_HANDLE_PARAMETERS = "handle-parameters"
MODE_VALIDATE = "validate"
MODE_PRERUN = "prerun"
MODE_ENGINE = "engine"
MODE_POSTRUN = "postrun"
MODE_SCENARIODATA_TRANSFORM = "scenariodata-transform"

RESOURCE_PROVIDER_LOCAL = "local"
RESOURCE_PROVIDER_AZURE = "azureStorage"
RESOURCE_PROVIDER_GIT = "git"

RESOURCE_MAIN = "main.py"
RESOURCE_ZIP = "resource.zip"
RESOURCE_REQUIREMENTS = "requirements.txt"

CSM_MAIN = "main"

DEFAULT_PATH_ROOT_LOCAL = "/pkg/share/"
DEFAULT_RUN_TEMPLATES_ROOT_FOLDER = "code/run_templates/"

RUN_TEMPLATE_PLACE_HOLDER = "%CSM_RUN_TEMPLATE_ID%"
RUN_TEMPLATE_DEFAULT_PATH_TEMPLATE = DEFAULT_RUN_TEMPLATES_ROOT_FOLDER + RUN_TEMPLATE_PLACE_HOLDER + "/"

PARAMETERS_HANDLER_DEFAULT_PATH_TEMPLATE = RUN_TEMPLATE_DEFAULT_PATH_TEMPLATE + "parameters_handler/"
DATASET_VALIDATOR_DEFAULT_PATH_TEMPLATE = RUN_TEMPLATE_DEFAULT_PATH_TEMPLATE + "validator/"
PRERUN_DEFAULT_PATH_TEMPLATE = RUN_TEMPLATE_DEFAULT_PATH_TEMPLATE + "prerun/"
ENGINE_DEFAULT_PATH_TEMPLATE = RUN_TEMPLATE_DEFAULT_PATH_TEMPLATE + "engine/"
POSTRUN_DEFAULT_PATH_TEMPLATE = RUN_TEMPLATE_DEFAULT_PATH_TEMPLATE + "postrun/"
SCENARIODATA_TRANSFORM_DEFAULT_PATH_TEMPLATE = RUN_TEMPLATE_DEFAULT_PATH_TEMPLATE + "scenariodata_transform/"

DEFAULT_EXTERNALS_FOLDER = DEFAULT_RUN_TEMPLATES_ROOT_FOLDER + "_csm_external_/"

UNZIP_DEFAULT_PATH_TEMPLATE = DEFAULT_EXTERNALS_FOLDER + "unzip/"
GIT_REPOSITORY_DEFAULT_PATH_TEMPLATE = DEFAULT_EXTERNALS_FOLDER + "git_repository/"

GIT_CLONING_DEPTH = "1"

logging = LOGGER


class EntrypointException(Exception):
    def __init__(self, message):
        self.message = message


def get_provider(provider):
    if provider is None:
        return RESOURCE_PROVIDER_LOCAL
    return provider


def get_path(path, default):
    if path is None:
        logging.debug(f"No path defined in env var, applying default {default}")
        if RUN_TEMPLATE_PLACE_HOLDER in default \
                and CSM_RUN_TEMPLATE_ID is None:
            logging.warning("Cannot apply default path template "
                            "without CSM_RUN_TEMPLATE_ID env var")
            return None
        return DEFAULT_PATH_ROOT_LOCAL + \
            default.replace(
                RUN_TEMPLATE_PLACE_HOLDER,
                CSM_RUN_TEMPLATE_ID
            )
    else:
        return path


def install_azure_dependencies():
    logging.info("Installing & importing Azure packages")
    subprocess.check_call([sys.executable, "-m", "pip",
                           "install", "azure-storage-blob"])
    logging.debug("Azure packages configured")


def download_azure(connection_string, path, download_file):
    install_azure_dependencies()
    from azure.storage.blob import BlobServiceClient, __version__
    logging.debug("Azure Blob storage v" + __version__)
    if connection_string is None:
        raise EntrypointException(
            "You must provide the azure storage account "
            "connection string in AZURE_STORAGE_CONNECTION_STRING")

    if "/" not in path:
        raise EntrypointException(
            f"You must provide the azure blob path in "
            "the format: CONTAINER/BLOB")

    split_path = path.split("/", maxsplit=1)
    container = split_path[0]
    blob = split_path[1]

    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string)
    blob_client = blob_service_client.get_blob_client(
        container=container, blob=blob)
    with open(download_file, "wb") as file:
        file.write(blob_client.download_blob().readall())


def fetch_azure_storage(path):
    logging.info("Fetching resource from Azure Storage")
    if not path.endswith(".zip"):
        raise EntrypointException(
            f"Unsupported resource file format in {path}. "
            "Only zip is supported.")

    local_path = Path(DEFAULT_PATH_ROOT_LOCAL) / UNZIP_DEFAULT_PATH_TEMPLATE
    logging.debug(f"Creating {local_path} directory")
    local_path.mkdir(parents=True, exist_ok=True)
    download_file = local_path / RESOURCE_ZIP

    download_azure(AZURE_STORAGE_CONNECTION_STRING, path, download_file)

    logging.debug(f"Unzipping {download_file}")
    with ZipFile(download_file, 'r') as zipObj:
        zipObj.extractall(local_path)
    if not (local_path / RESOURCE_MAIN).is_file():
        raise EntrypointException(
            "Your resource archive MUST contain "
            "a main.py file at the root")

    return local_path


def run_git_command(*args):
    try:
        subprocess.check_call(['git'] + list(args))
    except subprocess.CalledProcessError as error:
        logging.error(error.output)


def git_clone_repository(repositoryUrl, localPath, branchName=None):
    cloningOptions = '--depth'
    if branchName is not None:
        run_git_command("clone", cloningOptions, GIT_CLONING_DEPTH, '--branch', branchName, repositoryUrl, localPath)
    else:
        run_git_command("clone", cloningOptions, GIT_CLONING_DEPTH, repositoryUrl, localPath)


def fetch_git_repository(path):
    logging.info("Fetching resource from Git repository.")

    local_path = Path(DEFAULT_PATH_ROOT_LOCAL) / GIT_REPOSITORY_DEFAULT_PATH_TEMPLATE

    git_clone_repository(path, local_path, CSM_RUN_TEMPLATE_GIT_BRANCH_NAME)
    run_template_path = local_path
    if CSM_RUN_TEMPLATE_SOURCE_DIRECTORY is not None:
        run_template_path /= CSM_RUN_TEMPLATE_SOURCE_DIRECTORY
        run_template_path /= CSM_CONTAINER_MODE
    else:
        run_template_path /= CSM_CONTAINER_MODE
    return run_template_path


def fetch_resource(provider, path):
    if path is None:
        logging.warning("Cannot fetch resources from path None")
        return None
    if provider == RESOURCE_PROVIDER_LOCAL:
        return Path(path)
    if provider == RESOURCE_PROVIDER_AZURE:
        return fetch_azure_storage(path)
    if provider == RESOURCE_PROVIDER_GIT:
        return fetch_git_repository(path)


def run_python(path):
    logging.info("Running Python")
    project_root = Path(path)
    project_main = project_root / RESOURCE_MAIN
    project_requirements = project_root / RESOURCE_REQUIREMENTS
    if not project_main.is_file():
        raise EntrypointException(f"Exiting: No main script file found "
                                  f"in {project_main}")
    if project_requirements.is_file():
        logging.debug(f"Installing packages requirements "
                      f"from {project_requirements}")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install",
             '-r', RESOURCE_REQUIREMENTS], cwd=project_root)
    else:
        logging.debug(f"No specific packages requirements "
                      f"found in {project_requirements}")

    logging.debug(f"Running script {project_main}")
    subprocess.check_call([sys.executable, RESOURCE_MAIN], cwd=project_root)


def run_resource(
    name,
    provider,
    path,
    default_path,
    fallback_function=None,
    fallback_name=""
):
    logging.info(f"Running {name}...")
    final_provider = get_provider(provider)
    logging.debug(f"Provider: {final_provider}")
    final_path = get_path(path, default_path)
    logging.debug(f"Path: {final_path}")

    local_path = fetch_resource(final_provider, final_path)
    logging.debug(f"Local Python project path is {local_path}")
    if local_path is None or not local_path.is_dir():
        if fallback_function is not None:
            logging.debug("No Python project resource to run")
            logging.debug(f"Running fallback {fallback_name}")
            fallback_function()
        else:
            raise EntrypointException(f"No Python project resource to run for {name}")
    else:
        try:
            run_python(local_path)
        except subprocess.CalledProcessError as e:
            logging.error(f"{name} exited with code {e.returncode}")
            sys.exit(e.returncode)
    logging.info(f"Finished {name}")


def run_handle_parameters():
    run_resource(
        "parameters handler",
        CSM_PARAMETERS_HANDLER_PROVIDER,
        CSM_PARAMETERS_HANDLER_PATH,
        PARAMETERS_HANDLER_DEFAULT_PATH_TEMPLATE
    )


def run_validate():
    run_resource(
        "dataset validator",
        CSM_DATASET_VALIDATOR_PROVIDER,
        CSM_DATASET_VALIDATOR_PATH,
        DATASET_VALIDATOR_DEFAULT_PATH_TEMPLATE
    )


def run_prerun():
    run_resource(
        "pre-run",
        CSM_PRERUN_PROVIDER,
        CSM_PRERUN_PATH,
        PRERUN_DEFAULT_PATH_TEMPLATE
    )


def run_scenariodata_transform():
    run_resource(
        "scenariodata transform",
        CSM_SCENARIODATA_TRANSFORM_PROVIDER,
        CSM_SCENARIODATA_TRANSFORM_PATH,
        SCENARIODATA_TRANSFORM_DEFAULT_PATH_TEMPLATE
    )


def run_direct_simulator():
    if CSM_SIMULATION:
        logging.info(f"Simulation: {CSM_SIMULATION}")

        args = ["-i", CSM_SIMULATION]
        if CSM_PROBES_MEASURES_TOPIC is not None:
            logging.debug(f"Probes measures topic: {CSM_PROBES_MEASURES_TOPIC}")
            args = args + ["--amqp-consumer", CSM_PROBES_MEASURES_TOPIC]
        else:
            logging.warning("No probes measures topic")

        if CSM_CONTROL_PLANE_TOPIC is not None:
            logging.debug(f"Control plane topic: {CSM_CONTROL_PLANE_TOPIC}."
                          "Main Simulator binary is able to handle "
                          "CSM_CONTROL_PLANE_TOPIC directly so it is not"
                          "transformed as an argument.")
        else:
            logging.warning("No Control plane topic")
    else:
        args = sys.argv[2:]
        logging.debug(f"main arguments: {args}")

    subprocess.check_call([CSM_MAIN] + args)


def run_engine():
    run_resource(
        "engine",
        CSM_ENGINE_PROVIDER,
        CSM_ENGINE_PATH,
        ENGINE_DEFAULT_PATH_TEMPLATE,
        run_direct_simulator,
        "direct main simulator"
    )


def run_postrun():
    run_resource(
        "post-run",
        CSM_POSTRUN_PROVIDER,
        CSM_POSTRUN_PATH,
        POSTRUN_DEFAULT_PATH_TEMPLATE
    )


def get_env():
    logging.debug("Setting context from project.csm")
    projectFile = configparser.ConfigParser()
    projectFile.read("/pkg/share/project.csm")
    if projectFile.has_section("EntrypointEnv"):
        for key, value in projectFile.items("EntrypointEnv"):
            globals()[key.upper()] = value

    env_names = [
        # Run data
        "CSM_CONTAINER_MODE",
        "CSM_SIMULATION",
        # Run template config
        "CSM_RUN_TEMPLATE_ID",
        "CSM_RUN_TEMPLATE_GIT_BRANCH_NAME",
        "CSM_RUN_TEMPLATE_SOURCE_DIRECTORY",
        # Event topics
        "CSM_CONTROL_PLANE_TOPIC",
        "CSM_PROBES_MEASURES_TOPIC",
        # Azure connections
        "AZURE_TENANT_ID",
        "AZURE_CLIENT_ID",
        "AZURE_CLIENT_SECRET",
        "AZURE_STORAGE_CONNECTION_STRING",
    ]
    # Mode's provider and path
    for mode in ["PARAMETERS_HANDLER", "DATASET_VALIDATOR", "PRERUN", "ENGINE", "POSTRUN", "SCENARIODATA_TRANSFORM"]:
        env_names.append(f"CSM_{mode}_PROVIDER")
        env_names.append(f"CSM_{mode}_PATH")

    logging.debug("Setting context from env vars")
    for var_name in env_names:
        # Env var has priority, then project.csm and finally None
        globals()[var_name] = os.environ.get(var_name, globals().get(var_name))
        if globals().get(var_name) is not None:
            os.environ.setdefault(var_name, str(globals().get(var_name)))


modes_handlers = {
    MODE_HANDLE_PARAMETERS: run_handle_parameters,
    MODE_VALIDATE: run_validate,
    MODE_PRERUN: run_prerun,
    MODE_ENGINE: run_engine,
    MODE_POSTRUN: run_postrun,
    MODE_SCENARIODATA_TRANSFORM: run_scenariodata_transform
}


def get_mode():
    mode = CSM_CONTAINER_MODE or MODE_ENGINE
    logging.info(f"mode: {mode}")
    return mode


def handle_mode(mode):
    if mode not in modes_handlers:
        logging.error(f"Unrecognized mode {mode}")
        sys.exit(1)
    else:
        modes_handlers[mode]()


def run_entrypoint():
    logging.info("Phoenix Entry Point")
    get_env()
    modes = get_mode()
    smodes = modes.split(",")
    for mode in smodes:
        handle_mode(mode)


@click.command(hidden="True", context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
def main():
    """Docker entrypoint
    
    This command is used in CosmoTech docker containers only"""
    try:
        if os.environ.get("CSM_ENTRYPOINT_LEGACY", "true").lower() == "true":
            run_entrypoint()
        else:
            if importlib.util.find_spec("cosmotech") is None or importlib.util.find_spec(
                    "cosmotech.orchestrator") is None:
                raise EntrypointException(
                    "You need to install the library `cosmotech-run-orchestrator` in your container. "
                    "Check if you set it in your requirements.txt.")
            get_env()
            project_root = Path("/pkg/share")
            template_id = os.environ.get("CSM_RUN_TEMPLATE_ID")
            if template_id is None:
                raise EntrypointException("No run template id defined in environment variable \"CSM_RUN_TEMPLATE_ID\"")
            orchestrator_json = project_root / "code/run_templates" / template_id / "run.json"
            if not orchestrator_json.is_file():
                raise EntrypointException(f"No \"run.json\" defined for the run template {template_id}")
            _env = os.environ.copy()
            subprocess.check_call(["csm-orc", "run", str(orchestrator_json.absolute())],
                                  cwd=project_root,
                                  env=_env)
    except subprocess.CalledProcessError:
        logging.error("Error while running the entrypoint - check your logs")
        exit(1)


if __name__ == "__main__":
    main()
