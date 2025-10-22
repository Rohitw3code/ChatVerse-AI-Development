"""
Interrupt Helper Functions
Provides convenient helper functions for creating and handling interrupts in the agent system.
"""

from typing import Optional, List
from langgraph.types import interrupt
from chatagent.model.interrupt_model import InterruptRequest, InterruptResponse, InterruptType


def ask_user_option(
    name: str,
    question: str,
    options: List[str],
    context: str = ""
) -> str:
    """
    Ask the user to choose from a list of options.
    
    Args:
        name: Unique identifier for this interrupt
        question: The question to ask the user
        options: List of options for the user to choose from
        context: Additional context or information (optional)
        
    Returns:
        The user's selected option as a string
        
    Example:
        >>> response = ask_user_option(
        ...     name="send_email",
        ...     question="Do you want to send this email?",
        ...     options=["Yes", "No"]
        ... )
    """
    interrupt_request = InterruptRequest.create_input_option(
        name=name,
        title=question,
        options=options,
        content=context
    )
    return interrupt(interrupt_request.to_dict())


def ask_user_input(
    name: str,
    question: str,
    context: str = "",
    placeholder: Optional[str] = None,
    default_value: Optional[str] = None
) -> str:
    """
    Ask the user for free-form text input.
    
    Args:
        name: Unique identifier for this interrupt
        question: The question or prompt to display
        context: Additional context or information (optional)
        placeholder: Placeholder text for the input field (optional)
        default_value: Default value for the input field (optional)
        
    Returns:
        The user's input as a string
        
    Example:
        >>> email = ask_user_input(
        ...     name="get_recipient",
        ...     question="What is the recipient's email address?",
        ...     placeholder="example@domain.com"
        ... )
    """
    interrupt_request = InterruptRequest.create_input_field(
        name=name,
        title=question,
        content=context,
        placeholder=placeholder,
        default_value=default_value
    )
    return interrupt(interrupt_request.to_dict())


def ask_user_connect(
    platform: str,
    name: str,
    message: str,
    context: str = "",
    error_message: Optional[str] = None
) -> str:
    """
    Ask the user to connect or authenticate with a platform.
    
    Args:
        platform: The platform to connect (e.g., 'gmail', 'instagram', 'youtube')
        name: Unique identifier for this interrupt
        message: The message explaining why connection is needed
        context: Additional context (optional)
        error_message: Specific error message if this is due to an error (optional)
        
    Returns:
        The connection result as a string
        
    Example:
        >>> result = ask_user_connect(
        ...     platform="gmail",
        ...     name="gmail_auth",
        ...     message="Please connect your Gmail account to continue",
        ...     error_message="Your token has expired"
        ... )
    """
    interrupt_request = InterruptRequest.create_connect(
        name=name,
        platform=platform,
        title=message,
        content=context,
        error_message=error_message
    )
    return interrupt(interrupt_request.to_dict())


def parse_option_response(response: str, expected_option: str) -> bool:
    """
    Parse a response from an input_option interrupt and check if it matches the expected option.
    
    Args:
        response: The user's response
        expected_option: The option to check for
        
    Returns:
        True if the response matches the expected option (case-insensitive)
        
    Example:
        >>> response = ask_user_option("confirm", "Continue?", ["Yes", "No"])
        >>> if parse_option_response(response, "Yes"):
        ...     print("User confirmed")
    """
    return response.strip().lower() == expected_option.strip().lower()


def is_affirmative(response: str) -> bool:
    """
    Check if a response is affirmative (yes, true, ok, etc.).
    
    Args:
        response: The user's response
        
    Returns:
        True if the response is affirmative
        
    Example:
        >>> response = ask_user_option("confirm", "Proceed?", ["Yes", "No"])
        >>> if is_affirmative(response):
        ...     print("User said yes")
    """
    affirmative_values = ["yes", "y", "true", "ok", "confirm", "proceed", "continue"]
    return response.strip().lower() in affirmative_values


def is_negative(response: str) -> bool:
    """
    Check if a response is negative (no, false, cancel, etc.).
    
    Args:
        response: The user's response
        
    Returns:
        True if the response is negative
        
    Example:
        >>> response = ask_user_option("confirm", "Delete?", ["Yes", "No"])
        >>> if is_negative(response):
        ...     print("User said no")
    """
    negative_values = ["no", "n", "false", "cancel", "abort", "stop", "reject"]
    return response.strip().lower() in negative_values
