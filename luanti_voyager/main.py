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
    
    # Create agent
    agent = VoyagerAgent(
        name=args.name,
        world_path=args.world_path
    )
    
    # Note the port being used
    if args.port != 30000:
        logger.info(f"Using custom port: {args.port}")
    
    # Check if LLM is configured
    if args.llm:
        logger.info(f"Using LLM: {args.llm}")
        # TODO: Initialize LLM
    else:
        logger.info("Running in exploration mode (no LLM)")
        
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
        choices=["openai", "anthropic", "local", "none"],
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