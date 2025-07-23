import sys
import re
from typing import List
from urllib.parse import urlparse, parse_qs
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from semantic_kernel.functions.kernel_arguments import KernelArguments

def parse_azure_openai_uri(target_url: str):
    """
    Parse a full Azure OpenAI chat completions URL and extract endpoint, deployment name, and API version.

    Args:
        target_url (str): Full Azure OpenAI chat completions URL.

    Returns:
        tuple: (endpoint, deployment_name, api_version)

    Raises:
        SystemExit: If the URI is malformed or missing required components.
    """
    parsed = urlparse(target_url)
    endpoint = f"{parsed.scheme}://{parsed.netloc}/" if parsed.scheme and parsed.netloc else None
    match = re.search(r"/deployments/([^/]+)/", parsed.path)
    deployment_name = match.group(1) if match else None
    query = parse_qs(parsed.query)
    api_version = query.get("api-version", [None])[0]
    if not endpoint or not deployment_name or not api_version:
        print(f"Error: Malformed Azure OpenAI URI or missing required components: {target_url}", file=sys.stderr)
        sys.exit(1)
    return endpoint, deployment_name, api_version


def initialize_kernel(
    azure_openai_target_uri: str, azure_openai_api_key: str
) -> Kernel:
    """
    Initialize and return a Semantic Kernel with Azure OpenAI chat completion service.

    Args:
        azure_openai_target_uri (str): Full Azure OpenAI chat completions URL.
        azure_openai_api_key (str): The API key for Azure OpenAI.

    Returns:
        Kernel: Configured Semantic Kernel instance.

    Raises:
        SystemExit: If initialization fails.
    """
    endpoint, deployment_name, api_version = parse_azure_openai_uri(
        azure_openai_target_uri
    )
    kernel = Kernel()
    try:
        kernel.add_service(
            AzureChatCompletion(
                service_id="azure-openai",
                api_key=azure_openai_api_key,
                endpoint=endpoint,
                deployment_name=deployment_name,
                api_version=api_version,
            )
        )
        return kernel
    except Exception as e:
        print(f"Error initializing AzureChatCompletion: {e}", file=sys.stderr)
        sys.exit(1)


async def run_completion(kernel: Kernel, messages: List) -> str:
    """
    Run a chat completion using the provided kernel and message history.

    Args:
        kernel (Kernel): The Semantic Kernel instance with Azure OpenAI service.
        messages (List): List of message dicts with 'role' and 'content'.
            Supported roles: 'system', 'user', 'assistant'.

    Returns:
        str: The content of the completion response.

    Raises:
        SystemExit: If the chat service is not available.
    """
    chat_service: AzureChatCompletion = kernel.get_service("azure-openai")

    if not chat_service:
        print("Azure OpenAI service is not available in the kernel.", file=sys.stderr)
        sys.exit(1)

    history = ChatHistory()

    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "system":
            history.add_system_message(content)
        elif role == "user":
            history.add_user_message(content)
        elif role == "assistant":
            history.add_assistant_message(content)

    settings = AzureChatPromptExecutionSettings()

    result = await chat_service.get_chat_message_content(
        chat_history=history,
        settings=settings,
        kernel=kernel,
        kernel_arguments=KernelArguments(),
    )

    return result.content

