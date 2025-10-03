from python.helpers.tool import Tool, Response

class MemorySave(Tool):
    """Disabled for speed - VTube Fast Agent doesn't use memory"""

    async def execute(self, **kwargs):
        # Skip memory saving for faster responses
        return Response(message="", break_loop=False)
