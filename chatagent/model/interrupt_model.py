"""
Interrupt Models Module
Defines structured models for different types of interrupts in the agent system.
Supports three interrupt types: input_option, input_field, and connect.
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any, Union
from enum import Enum


class InterruptType(str, Enum):
    """Enumeration of available interrupt types."""
    INPUT_OPTION = "input_option"
    INPUT_FIELD = "input_field"
    CONNECT = "connect"


class InterruptData(BaseModel):
    """Base model for interrupt data payload.

    The `content` field now supports JSON payloads (dict) in addition to strings
    to enable richer UI rendering and data passing.
    """
    title: str = Field(..., description="The title or question to display to the user")
    content: Union[str, Dict[str, Any]] = Field(
        default="",
        description="Additional content or context; can be a string or JSON object",
    )


class InputOptionData(InterruptData):
    """Data model for input_option interrupt type."""
    options: list[str] = Field(..., description="List of options for the user to choose from")


class InputFieldData(InterruptData):
    """Data model for input_field interrupt type."""
    placeholder: Optional[str] = Field(None, description="Placeholder text for the input field")
    default_value: Optional[str] = Field(None, description="Default value for the input field")


class ConnectData(InterruptData):
    """Data model for connect interrupt type."""
    platform: str = Field(..., description="The platform to connect (e.g., 'gmail', 'instagram')")
    error_message: Optional[str] = Field(None, description="Optional error message to display")


class InterruptRequest(BaseModel):
    """
    Unified model for interrupt requests.
    Automatically validates the data based on the interrupt type.
    """
    name: str = Field(..., description="Unique identifier name for this interrupt")
    type: InterruptType = Field(..., description="Type of interrupt")
    data: Union[InputOptionData, InputFieldData, ConnectData] = Field(
        ..., description="The interrupt data payload"
    )
    platform: Optional[str] = Field(None, description="Platform name for connect type")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the interrupt request to a dictionary for use with langgraph interrupt()."""
        result = {
            "name": self.name,
            "type": self.type.value,
            "data": self.data.model_dump()
        }
        if self.platform:
            result["platform"] = self.platform
        return result

    @classmethod
    def create_input_option(
        cls,
        name: str,
        title: str,
        options: list[str],
        content: Union[str, Dict[str, Any]] = "",
    ) -> "InterruptRequest":
        """
        Factory method to create an input_option interrupt.
        
        Args:
            name: Unique identifier for the interrupt
            title: Question or prompt to display
            options: List of options for user to choose from
            content: Additional context (optional). Supports JSON (dict) for rich data.
            
        Returns:
            InterruptRequest configured for input_option
        """
        return cls(
            name=name,
            type=InterruptType.INPUT_OPTION,
            data=InputOptionData(
                title=title,
                content=content,
                options=options
            )
        )

    @classmethod
    def create_input_field(
        cls,
        name: str,
        title: str,
        content: str = "",
        placeholder: Optional[str] = None,
        default_value: Optional[str] = None
    ) -> "InterruptRequest":
        """
        Factory method to create an input_field interrupt.
        
        Args:
            name: Unique identifier for the interrupt
            title: Question or prompt to display
            content: Additional context (optional)
            placeholder: Placeholder text for input field (optional)
            default_value: Default value for input field (optional)
            
        Returns:
            InterruptRequest configured for input_field
        """
        return cls(
            name=name,
            type=InterruptType.INPUT_FIELD,
            data=InputFieldData(
                title=title,
                content=content,
                placeholder=placeholder,
                default_value=default_value
            )
        )

    @classmethod
    def create_connect(
        cls,
        name: str,
        platform: str,
        title: str,
        content: str = "",
        error_message: Optional[str] = None
    ) -> "InterruptRequest":
        """
        Factory method to create a connect interrupt.
        
        Args:
            name: Unique identifier for the interrupt
            platform: Platform to connect (e.g., 'gmail', 'instagram')
            title: Prompt to display
            content: Additional context (optional)
            error_message: Error message to display (optional)
            
        Returns:
            InterruptRequest configured for connect
        """
        return cls(
            name=name,
            type=InterruptType.CONNECT,
            platform=platform,
            data=ConnectData(
                title=title,
                content=content,
                platform=platform,
                error_message=error_message
            )
        )


class InterruptResponse(BaseModel):
    """Model for handling interrupt responses from users."""
    interrupt_name: str = Field(..., description="Name of the interrupt this responds to")
    response_type: InterruptType = Field(..., description="Type of interrupt that was responded to")
    value: Union[str, bool, Dict[str, Any]] = Field(..., description="The user's response")
    
    def is_option_selected(self, option: str) -> bool:
        """Check if a specific option was selected (for input_option type)."""
        if self.response_type != InterruptType.INPUT_OPTION:
            return False
        return str(self.value).strip().lower() == option.strip().lower()
    
    def get_field_value(self) -> str:
        """Get the field value (for input_field type)."""
        return str(self.value)
    
    def is_connected(self) -> bool:
        """Check if connection was successful (for connect type)."""
        if self.response_type != InterruptType.CONNECT:
            return False
        if isinstance(self.value, bool):
            return self.value
        return str(self.value).strip().lower() in ["true", "yes", "connected", "success"]
