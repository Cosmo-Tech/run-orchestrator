---
description: Advanced tutorial to package csm-orc plugins with customized command templates 
---
# Plugins and Command Templates

!!! notes "Objectives"
    - Present the Plugins and Library system added in version 1.2.0

## About the Library

The `Library` is a concept inside `csm-orc` that allow developers to make common `CommandTemplate` 
available to users without needing to copy-paste an external file.

For a user only writing `.json` orchestrator file it will simply allow him to gain some time in writing 
by using ready-made `CommandTemplate`, for a library developer it is a way to package new `CommandTemplate` 
for `csm-orc` in his own work.

The content of the `Library` is easily displayable with the command `csm-orc list-templates` 
that will list every existing template in the Library and display their origin.

## What is a Plugin ?

A `Plugin` is a precisely defined python library. By following a given format it is automatically 
picked up by the Library and made available to the users.

### How to create a Plugin ?

A `Plugin` needs the following structure

???+ experiment "A plugin structure"
    ```text
    cosmotech/
    └── orchestrator_plugins/
        └── my_plugin
            ├── __init__.py
            └── templates
                └── ...
    ```

```python title="cosmotech/orchestrator_plugins/my_plugin/__init__.py"
--8<-- "tutorial/plugins_and_templates/init.py"
```

And in the `templates` folder you can put any `.json` file containing either one single `CommandTemplate` 
or an orchestration file containing valid `CommandTemplate`

=== "json file containing a single `CommandTemplate`"
    ```json
    --8<-- "tutorial/plugins_and_templates/single_template.json"
    ```
=== "json file containing multiple `CommandTemplate`"
    ```json
    --8<-- "tutorial/plugins_and_templates/multi_template.json"
    ```

And that is all you need to create a `Plugin`.

### How to make a plugin available ?

The `Library` make use of the `Implicit Namespace Packages` of `python` as defined by the [PEP-420](https://peps.python.org/pep-0420/).

To summarize, we can define `Namespaces` that will be able to be filled across multiple `Packages` 
and here we define the namespace `cosmotech.orchestrator_plugins` to contain all future `Plugins`.

We can easily add our `Plugin` by making the `cosmotech/` folder part of the `PYTHONPATH`.

To do so we can :
- Define a standalone python package for our `Plugin` and users just need to install said package in their python environment to get access to the `Plugin`.
- Add the `cosmotech` folder inside the installation of our python package so that when users install the package from any source the `Plugin` gets installed alongside it
- Copy the `cosmotech` folder in the working directory
