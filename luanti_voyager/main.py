"""
Main entry point for Luanti Voyager.

Run this to start your agent's adventure!
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
import os

from .agent import VoyagerAgent
from .web_server import VoyagerWebServer


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Add color if available
    try:
        import colorama
        colorama.init()
        
        # Color codes
        colors = {
            'DEBUG': colorama.Fore.CYAN,
            'INFO': colorama.Fore.GREEN,
            'WARNING': colorama.Fore.YELLOW,
            'ERROR': colorama.Fore.RED,
            'CRITICAL': colorama.Fore.RED + colorama.Style.BRIGHT,
        }
        
        class ColoredFormatter(logging.Formatter):
            def format(self, record):
                if record.levelname in colors:
                    record.msg = colors[record.levelname] + record.msg + colorama.Style.RESET_ALL
                return super().format(record)
                
        for handler in logging.root.handlers:
            handler.setFormatter(ColoredFormatter(handler.formatter._fmt))
            
    except ImportError:
        pass  # No colors available
        

async def run_agent(args):
    """Run the agent with given arguments."""
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Welcome to Luanti Voyager!")
    logger.info(f"Starting agent '{args.name}'...")
    
    # Start web server if enabled
    web_server = None
    if args.web_ui:
        web_server = VoyagerWebServer(
            host='0.0.0.0' if args.lan_access else '127.0.0.1',
            http_port=args.web_port,
            ws_port=args.web_port + 1
        )
        ws_server, runner = await web_server.start()
        
        if args.lan_access:
            logger.info(f"🌐 Web UI: http://192.168.68.145:{args.web_port}")
            logger.info(f"🔌 WebSocket: ws://192.168.68.145:{args.web_port + 1}")
        else:
            logger.info(f"🌐 Web UI: http://localhost:{args.web_port}")
            logger.info(f"🔌 WebSocket: ws://localhost:{args.web_port + 1}")
    
    # Create agent with LLM support
    agent = VoyagerAgent(
        name=args.name,
        world_path=args.world_path,
        web_server=web_server,
        llm_provider=args.llm
    )
    
    # Note the port being used
    if args.port != 30000:
        logger.info(f"Using custom port: {args.port}")
    
    # LLM configuration is handled by the agent
    if args.llm != "none":
        logger.info(f"🧠 LLM enabled: {args.llm}")
    else:
        logger.info("🤖 Running in basic exploration mode (no LLM)")
        
    try:
        await agent.start()
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down gracefully...")
        await agent.stop()
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
        

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Luanti Voyager - Teaching AI to dream in blocks!"
    )
    
    parser.add_argument(
        "--name",
        default="VoyagerBot",
        help="Name of your agent (default: VoyagerBot)"
    )
    
    parser.add_argument(
        "--world-path",
        help="Path to Luanti world directory (auto-detected if not specified)"
    )
    
    parser.add_argument(
        "--llm",
        choices=["openai", "anthropic", "ollama", "none"],
        default="none",
        help="LLM to use for reasoning (default: none)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=30000,
        help="Luanti server port (default: 30000, test: 40000)"
    )
    
    parser.add_argument(
        "--web-ui",
        action="store_true",
        default=True,
        help="Enable web UI for visualization (default: enabled)"
    )
    
    parser.add_argument(
        "--web-port",
        type=int,
        default=8090,
        help="Web UI port (default: 8090)"
    )
    
    parser.add_argument(
        "--lan-access",
        action="store_true",
        default=True,
        help="Allow LAN access to servers (default: enabled, use --no-lan-access for localhost only)"
    )
    
    parser.add_argument(
        "--no-lan-access",
        dest="lan_access",
        action="store_false",
        help="Restrict to localhost only"
    )
    
    args = parser.parse_args()
    
    # Auto-detect world path if not specified
    if not args.world_path:
        # Try common locations
        possible_paths = [
            Path.home() / ".minetest" / "worlds" / "world",
            Path.home() / ".luanti" / "worlds" / "world",
            Path("worlds") / "world",  # Local development
        ]
        
        for path in possible_paths:
            if path.exists():
                args.world_path = str(path)
                break
        else:
            print("❌ Could not find Luanti world directory!")
            print("Please specify with --world-path")
            sys.exit(1)
            
    # Setup logging
    setup_logging(args.verbose)
    
    # Run the agent
    asyncio.run(run_agent(args))
    

if __name__ == "__main__":
    main()