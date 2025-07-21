from pydantic import BaseModel


class ExampleInput(BaseModel):
    message: str


def example_tool(input_data: ExampleInput) -> str:
    """
    Example tool that echoes a message.
    """
    return f"Echo: {input_data.message}"