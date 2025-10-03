from python.helpers import files
from python.helpers.print_style import PrintStyle

async def execute(agent):
    """Initialize VTube Fast Agent with optimized settings"""

    # Set a fun agent name
    agent.config.name = "VTube Fast"

    # Log that memory is disabled for speed
    PrintStyle(font_color="green", padding=True).print(
        f"🚀 {agent.config.name} initialized - Memory disabled for maximum speed!"
    )
