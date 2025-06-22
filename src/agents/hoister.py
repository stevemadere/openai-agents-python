#ALFRED: there is a circular import. need to extract hoister types to another file
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Final

from openai.types.responses import ResponseFunctionToolCall
from agents.agent import Agent
from agents.items import HoistedArtifactItem, HoistedFunctionCallOutputArtifact, ImageContentPart, TextContentPart
from agents.tool import ToolRunFunction

#TODO: ToolRunFunction, is already defined in agents._run_impl but it causes a circular import. We should really extract this type and those like it to another file, but i'm trying to make minimum modifications right now.

__all__ = ["Hoister"]

class Hoister:
    """Class responsible for extracting image URLs from tool results and creating hoisted artifact items."""
    
    # Regular expression to match image URLs
    # This is a simple pattern that matches common image file extensions
    # It can be improved in the future for more robust URL detection
    IMAGE_URL_PATTERN: Final[str] = r'(https?://[^\s]+\.(jpg|jpeg|png|gif|bmp|webp|svg))'

    @classmethod 
    def generate_artifact_text_part(cls, tool_run: ToolRunFunction) -> TextContentPart:
        #We can expand this to have more information about the tool call
        return TextContentPart(
            type="input_text",
            text=f"Image from tool call {tool_run.tool_call.call_id}"
        )
    @classmethod
    def create_hoisted_artifact_item(cls, agent: Agent[Any], tool_run: ToolRunFunction, image_url: str) -> HoistedArtifactItem:
        """Create a hoisted artifact item from a tool run and its result."""
        artifact = HoistedFunctionCallOutputArtifact(
                role="user",
                content=[
                    cls.generate_artifact_text_part(tool_run ),
                    ImageContentPart(
                        type="input_image",
                        image_url=image_url
                    )
                ],
                tool_call_id=tool_run.tool_call.call_id
            )
            
            # Create the hoisted artifact item
        hoisted_item = HoistedArtifactItem(
                agent=agent,
                raw_item=artifact,
                output="place holder tool result. What makes sense to go here as this isn't a real tool call?", #What goes here? Should it be the original ouput of the tool?
                type="hoisted_artifact_item"
            )
        
        return hoisted_item
    
    @classmethod
    def generate_hoisted_items(cls, agent: Agent[Any], tool_run: ToolRunFunction, tool_result: str) -> list[HoistedArtifactItem]:
        #TODO: figure out if we can constrain the type of tool_result at all
        """Generate hoisted artifact items from a tool run and its result.
        
        Args:
            tool_run: The tool run that produced the result
            tool_result: The result of the tool run
            
        Returns:
            A list of hoisted artifact items containing image URLs found in the tool result
        """
        
        image_urls = cls._find_image_urls(tool_result)
        hoisted_items: list[HoistedArtifactItem] = []
        if not image_urls:
            return hoisted_items
        try:
            call_id: str = tool_run.tool_call.call_id
            if call_id is "":
              raise ValueError("function call id is empty")
        except (AttributeError, ValueError):
            # If we can't get the call_id or agent, we can't create the hoisted items
            print("ERROR: Tool run must have a tool call with a call_id")
            return hoisted_items
        
        for image_url in image_urls:
            # Create the artifact with text and image content
            hoisted_item = cls.create_hoisted_artifact_item(agent, tool_run, image_url) 
            hoisted_items.append(hoisted_item)
            
        return hoisted_items
    
    @classmethod
    def _find_image_urls(cls, data: str) -> list[str]:
        """Recursively search for image URLs in the data.
        
        Args:
            data: The data to search for image URLs
            
        Returns:
            A list of image URLs found in the data
        """
        image_urls: list[str] = []
        
        # Handle different data types
        # Search for image URLs in the string using a capturing group to get the full URL
        matches = re.findall(cls.IMAGE_URL_PATTERN, data)
        if matches:
            # Extract the full URLs (first group in each match)
            image_urls.extend([match[0] for match in matches])
    
        # Return unique URLs to avoid duplicates
        return list(set(image_urls))
