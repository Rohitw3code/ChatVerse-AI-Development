"""
Unit tests for interrupt models and helpers.
Run with: pytest chatagent/model/test_interrupt_model.py
"""

import pytest
from chatagent.model.interrupt_model import (
    InterruptType,
    InterruptRequest,
    InterruptResponse,
    InputOptionData,
    InputFieldData,
    ConnectData
)
from chatagent.model.interrupt_helpers import (
    parse_option_response,
    is_affirmative,
    is_negative
)


class TestInterruptRequest:
    """Test InterruptRequest model and factory methods."""
    
    def test_create_input_option(self):
        """Test creating input_option interrupt."""
        req = InterruptRequest.create_input_option(
            name="test_option",
            title="Choose an option",
            options=["Yes", "No"],
            content="Some context"
        )
        
        assert req.name == "test_option"
        assert req.type == InterruptType.INPUT_OPTION
        assert isinstance(req.data, InputOptionData)
        assert req.data.title == "Choose an option"
        assert req.data.options == ["Yes", "No"]
        assert req.data.content == "Some context"
    
    def test_create_input_field(self):
        """Test creating input_field interrupt."""
        req = InterruptRequest.create_input_field(
            name="test_input",
            title="Enter value",
            placeholder="example@email.com",
            default_value="default@email.com"
        )
        
        assert req.name == "test_input"
        assert req.type == InterruptType.INPUT_FIELD
        assert isinstance(req.data, InputFieldData)
        assert req.data.title == "Enter value"
        assert req.data.placeholder == "example@email.com"
        assert req.data.default_value == "default@email.com"
    
    def test_create_connect(self):
        """Test creating connect interrupt."""
        req = InterruptRequest.create_connect(
            name="test_connect",
            platform="gmail",
            title="Connect Gmail",
            error_message="Token expired"
        )
        
        assert req.name == "test_connect"
        assert req.type == InterruptType.CONNECT
        assert req.platform == "gmail"
        assert isinstance(req.data, ConnectData)
        assert req.data.title == "Connect Gmail"
        assert req.data.platform == "gmail"
        assert req.data.error_message == "Token expired"
    
    def test_to_dict_input_option(self):
        """Test converting input_option to dictionary."""
        req = InterruptRequest.create_input_option(
            name="test",
            title="Question?",
            options=["A", "B"]
        )
        
        result = req.to_dict()
        
        assert result["name"] == "test"
        assert result["type"] == "input_option"
        assert result["data"]["title"] == "Question?"
        assert result["data"]["options"] == ["A", "B"]
    
    def test_to_dict_input_field(self):
        """Test converting input_field to dictionary."""
        req = InterruptRequest.create_input_field(
            name="test",
            title="Enter:",
            placeholder="hint"
        )
        
        result = req.to_dict()
        
        assert result["name"] == "test"
        assert result["type"] == "input_field"
        assert result["data"]["title"] == "Enter:"
        assert result["data"]["placeholder"] == "hint"
    
    def test_to_dict_connect(self):
        """Test converting connect to dictionary."""
        req = InterruptRequest.create_connect(
            name="test",
            platform="instagram",
            title="Connect now"
        )
        
        result = req.to_dict()
        
        assert result["name"] == "test"
        assert result["type"] == "connect"
        assert result["platform"] == "instagram"
        assert result["data"]["title"] == "Connect now"


class TestInterruptResponse:
    """Test InterruptResponse model."""
    
    def test_is_option_selected(self):
        """Test checking if specific option was selected."""
        response = InterruptResponse(
            interrupt_name="test",
            response_type=InterruptType.INPUT_OPTION,
            value="Yes"
        )
        
        assert response.is_option_selected("Yes")
        assert response.is_option_selected("yes")  # Case insensitive
        assert response.is_option_selected(" Yes ")  # Strips whitespace
        assert not response.is_option_selected("No")
    
    def test_get_field_value(self):
        """Test getting field value."""
        response = InterruptResponse(
            interrupt_name="test",
            response_type=InterruptType.INPUT_FIELD,
            value="user@example.com"
        )
        
        assert response.get_field_value() == "user@example.com"
    
    def test_is_connected_with_bool(self):
        """Test checking connection status with boolean."""
        response = InterruptResponse(
            interrupt_name="test",
            response_type=InterruptType.CONNECT,
            value=True
        )
        
        assert response.is_connected()
        
        response.value = False
        assert not response.is_connected()
    
    def test_is_connected_with_string(self):
        """Test checking connection status with string."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("yes", True),
            ("connected", True),
            ("success", True),
            ("false", False),
            ("no", False),
            ("failed", False),
        ]
        
        for value, expected in test_cases:
            response = InterruptResponse(
                interrupt_name="test",
                response_type=InterruptType.CONNECT,
                value=value
            )
            assert response.is_connected() == expected


class TestInterruptHelpers:
    """Test interrupt helper functions."""
    
    def test_parse_option_response(self):
        """Test parsing option responses."""
        assert parse_option_response("Yes", "Yes")
        assert parse_option_response("yes", "Yes")  # Case insensitive
        assert parse_option_response(" Yes ", "Yes")  # Strips whitespace
        assert not parse_option_response("No", "Yes")
    
    def test_is_affirmative(self):
        """Test checking affirmative responses."""
        affirmative = ["yes", "Yes", "y", "Y", "true", "True", "ok", "OK", 
                      "confirm", "proceed", "continue"]
        
        for value in affirmative:
            assert is_affirmative(value), f"'{value}' should be affirmative"
        
        assert not is_affirmative("no")
        assert not is_affirmative("false")
        assert not is_affirmative("cancel")
    
    def test_is_negative(self):
        """Test checking negative responses."""
        negative = ["no", "No", "n", "N", "false", "False", "cancel", 
                   "Cancel", "abort", "stop", "reject"]
        
        for value in negative:
            assert is_negative(value), f"'{value}' should be negative"
        
        assert not is_negative("yes")
        assert not is_negative("true")
        assert not is_negative("ok")
    
    def test_whitespace_handling(self):
        """Test that functions handle whitespace correctly."""
        assert is_affirmative("  yes  ")
        assert is_negative("  no  ")
        assert parse_option_response("  Yes  ", "Yes")


class TestDataModels:
    """Test individual data models."""
    
    def test_input_option_data(self):
        """Test InputOptionData model."""
        data = InputOptionData(
            title="Question?",
            content="Context",
            options=["A", "B", "C"]
        )
        
        assert data.title == "Question?"
        assert data.content == "Context"
        assert len(data.options) == 3
    
    def test_input_field_data(self):
        """Test InputFieldData model."""
        data = InputFieldData(
            title="Enter value:",
            placeholder="hint",
            default_value="default"
        )
        
        assert data.title == "Enter value:"
        assert data.placeholder == "hint"
        assert data.default_value == "default"
    
    def test_connect_data(self):
        """Test ConnectData model."""
        data = ConnectData(
            title="Connect platform",
            platform="gmail",
            error_message="Token expired"
        )
        
        assert data.title == "Connect platform"
        assert data.platform == "gmail"
        assert data.error_message == "Token expired"
    
    def test_data_defaults(self):
        """Test default values in data models."""
        # InputOptionData requires all fields
        option_data = InputOptionData(
            title="Test",
            options=["A"]
        )
        assert option_data.content == ""  # Default
        
        # InputFieldData with optional fields
        field_data = InputFieldData(title="Test")
        assert field_data.content == ""
        assert field_data.placeholder is None
        assert field_data.default_value is None
        
        # ConnectData with optional error
        connect_data = ConnectData(
            title="Test",
            platform="gmail"
        )
        assert connect_data.error_message is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
