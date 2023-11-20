FROM python:latest

COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

# The code folder must be set in this position to work 
# with the predefined entrypoint of csm-orc
COPY code /pkg/share/code

# Defining a run template ID here allows to have a default for the image
# and thus avoid having to define the EnvVar at run
ENV CSM_RUN_TEMPLATE_ID=RUN

# The following command is the entrypoint defined by csm-orc that will do 
# a default run of your template.
# This command is hidden in the list of commands, 
# but you can check it by running `csm-orc entrypoint --help`
ENTRYPOINT ["csm-orc", "entrypoint"]