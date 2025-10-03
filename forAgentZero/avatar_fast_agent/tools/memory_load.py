from python.helpers.tool import Tool, Response

class MemoryLoad(Tool):
    """Disabled for speed - VTube Fast Agent doesn't use memory"""

    async def execute(self, **kwargs):
        # Skip memory loading for faster responses
        return Response(message="", break_loop=False)
