import unittest
from unittest.mock import MagicMock
import pytest
from agents.agent import Agent
from agents._run_impl import ToolRunFunction
from agents.hoister import Hoister
from agents.items import HoistedArtifactItem

class TestHoister(unittest.TestCase):
    def test_generate_hoisted_items(self):
        """
        Test that Hoister.generate_hoisted_items correctly creates hoisted items for each URL
        in the tool result, and that the text part mentions the tool ID.
        """
        # Mock the agent
        mock_agent = MagicMock(spec=Agent)
        
        # Mock the tool call with a call_id
        mock_tool_call = MagicMock()
        mock_tool_call.call_id = "test_tool_call_id"
        
        # Mock the tool run
        mock_tool_run = MagicMock(spec=ToolRunFunction)
        mock_tool_run.tool_call = mock_tool_call
        
        # Create a tool result with multiple image URLs
        tool_result = """
        Here are some images:
        https://example.com/image1.jpg
        https://example.com/image2.png
        And some text in between
        https://example.com/image3.gif
        """
        
        # Call the method under test
        hoisted_items = Hoister.generate_hoisted_items(mock_agent, mock_tool_run, tool_result)
        
        # Assertions
        # 1. Check that we have the correct number of hoisted items (3 URLs)
        self.assertEqual(len(hoisted_items), 3)
        
        # 2. Check that each hoisted item is of the correct type
        for item in hoisted_items:
            self.assertIsInstance(item, HoistedArtifactItem)
            
        # 4. Check that each hoisted item has a text part that mentions the tool ID
        for item in hoisted_items:
            # Get the content parts
            content_parts = item.raw_item["content"]
            # Find the text part - in the actual implementation it should be type "text"
            # but in our test mock it might be different
            found_text_mention = False
            for part in content_parts:
                if "text" in part and "test_tool_call_id" in part["text"]:
                    found_text_mention = True
                    break
            self.assertTrue(found_text_mention, "Text part should mention the tool call ID")
       
            
        # 5. Check that each hoisted item has the correct image URL
        expected_urls = [
            "https://example.com/image1.jpg",
            "https://example.com/image2.png",
            "https://example.com/image3.gif"
        ]
        
        # Create a set of URLs from the hoisted items
        actual_urls = set()
        for item in hoisted_items:
            # Get the content parts
            content_parts = item.raw_item["content"]
            # Find image parts
            for part in content_parts:
                if "image_url" in part:
                    actual_urls.add(part["image_url"])
        
        # Check that all expected URLs are present
        self.assertEqual(set(expected_urls), actual_urls)
      

if __name__ == "__main__":
    unittest.main()
