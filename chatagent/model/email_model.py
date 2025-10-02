from typing import TypedDict, Annotated, Literal
from pydantic import BaseModel, Field
from typing import Literal
from langgraph.graph.message import add_messages


class SendEmailInput(BaseModel):
    recipient: str = Field(..., description="The recipient email address")
    subject: str = Field(..., description="The subject of the email")
    body: str = Field(..., description="The body of the email")
