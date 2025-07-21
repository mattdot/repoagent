# TPM Agent

The TPM Agent operates as a modular GitHub Action designed to process GitHub issues efficiently. It provides two distinct implementations, one in .NET and the other in Python, to cater to different runtime preferences and use cases.

### .NET Implementation

The .NET-based implementation leverages the Semantic Kernel Process Framework to process GitHub issues. It is encapsulated in a Docker container and includes the following components:

1. **action.yml**: Defines the metadata and inputs/outputs for the GitHub Action.
2. **Dockerfile**: Specifies the environment and dependencies required to run the .NET action.
3. **entrypoint.sh**: Serves as the entry point for executing the action.
4. **src/**: Contains the core logic, including `Program.cs` and the project file `TpmAgent.csproj`.

This implementation is ideal for workflows that require the robustness and performance of the .NET runtime.
Refer to the [dotnet-readme](./dotnet/README.md) for more details on dotnet.

### Python Implementation

The Python-based implementation utilizes OpenAI to process GitHub issues. It is also encapsulated in a Docker container and includes the following components:

1. **action.yml**: Defines the metadata and inputs/outputs for the GitHub Action.
2. **Dockerfile**: Specifies the environment and dependencies required to run the Python action.
3. **entrypoint.sh**: Serves as the entry point for executing the action.
4. **requirements.txt**: Lists the Python dependencies needed for the project.
5. **src/**: Contains the core logic, including `main.py` for OpenAI integration and `main_no_openai.py` for alternative processing.

This implementation is suitable for workflows that benefit from Python's flexibility and the capabilities of OpenAI. Refer to the [python-readme](./python/README.md) for more details on python.


## Integrating TPM Agent from any other repository

To integrate the TPM Agent into another repository, follow these steps:

1. **Referencing TPM Agent in External GitHub Workflows**:  
    For example, if you have a test repository that needs to use the TPM Agent, you can integrate it by updating your workflow file. The workflow (e.g., `.github/workflows/test.yml`) can be configured to run when a GitHub Issue is opened, edited, or otherwise modified.

2. Set the required Secrets on the Test GitHub repository
| Input | Description | Required For |
|-------|-------------|-------------|
| `GitHub_TOKEN` | GitHub token for API access | .NET and Python |
| `AZURE_OPENAI_TYPE ` | Azure OpenAI Type | Python |
| `AZURE_OPENAI_KEY ` | Azure OpenAI Key | Python |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI Endpoint | Python |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API Version | Python |
| `AZURE_OPENAI_DEPLOYMENT ` | Azure OpenAI Deployment | Python |

3. **Reference the Action in Your Workflow**:
   Update your GitHub Actions workflow file to include the TPM Agent. For example:
   
   ```yaml
    name: Issue Processing
    on:
    issues:
        types: [opened, edited]

    jobs:
    process-issue:
        runs-on: ubuntu-latest
        steps:
        - name: Process Issue
            uses: mattdot/repoagent/dotnet@main
            # uses: mattdot/repoagent/python@main
            with:
            issue_content: ${{ github.event.issue.body }}
            github_token: ${{ secrets.GITHUB_TOKEN }}
            repository: ${{ github.repository }}
            issue_number: ${{ github.event.issue.number }}
            # Below are required varaibles for python implementation
            # azure_openai_api_type: ${{ secrets.AZURE_OPENAI_TYPE }}
            # azure_openai_key: ${{ secrets.AZURE_OPENAI_KEY }}
            # azure_openai_endpoint: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
            # azure_openai_api_version: ${{ secrets.AZURE_OPENAI_API_VERSION }}
            # azure_openai_deployment: ${{ secrets.AZURE_OPENAI_DEPLOYMENT }}
            id: issue-processor
        
        - name: Display Processing Results
            run: |
            echo "Processing Status: ${{ steps.issue-processor.outputs.status }}"
            echo "Processing Result: ${{ steps.issue-processor.outputs.result }}"
            
Refer to the [test.yml](./test/test.yml) for complete yml file for testing

3. **Configure Inputs**:
   Ensure that the required inputs (e.g., `issue_number`, `repo_name`) are correctly passed to the action in your workflow file.

4. **Test the Integration**:
   Trigger the workflow in your repository to verify that the TPM Agent processes issues as expected.

By following these steps, you can seamlessly integrate the TPM Agent into your repository's workflows, leveraging its capabilities to process GitHub issues efficiently.

These steps ensure that both the .NET and Python implementations of the TPM Agent are functioning correctly and can be integrated seamlessly into your workflows.


