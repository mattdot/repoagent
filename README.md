# AI Workflow Agent

This repository contains two main components, implemented in different programming languages, to support AI workflow automation:

## dotnet

The `dotnet` folder contains a .NET-based implementation of the AI workflow agent. It includes the following:

- **action.yml**: Configuration file for the .NET action.
- **Dockerfile**: Defines the container for running the .NET action.
- **entrypoint.sh**: The entry point script for the .NET action.
- **src/**: Contains the source code, including `Program.cs` and the project file `TpmAgent.csproj`.

This component is designed for scenarios where .NET is the preferred runtime environment.
Refer to the [dotnet-readme](./dotnet/README.md) for more details on dotnet.

## python

The `python` folder contains a Python-based implementation of the AI workflow agent. It includes the following:

- **action.yml**: Configuration file for the Python action.
- **Dockerfile**: Defines the container for running the Python action.
- **entrypoint.sh**: The entry point script for the Python action.
- **requirements.txt**: Lists the Python dependencies required for the project.
- **src/**: Contains the source code, including `main.py` and `main_no_openai.py`.

This component is designed for scenarios where Python is the preferred runtime environment.
Refer to the [python-readme](./python/README.md) for more details on python.

---

Both implementations are designed to be modular and can be used independently based on the requirements of the AI workflow.
