#!/usr/bin/env python3
"""Debug script to isolate the setup hanging issue"""

import logging
from claude_desktop_mcp.setup_wizard import setup_logging, SetupWizard

def debug_setup():
    # Setup logging
    logger = setup_logging()
    logger.info("Debug setup started")
    
    try:
        wizard = SetupWizard()
        logger.info("SetupWizard created")
        
        # Test just the dependency check
        logger.info("Testing dependency check...")
        deps_ok = wizard.check_dependencies_interactive()
        logger.info(f"Dependency check result: {deps_ok}")
        
        if deps_ok:
            logger.info("Dependencies OK, testing install_servers...")
            # This is where it should hang
            result = wizard.install_servers()
            logger.info(f"install_servers result: {result}")
        
    except Exception as e:
        logger.error(f"Error in debug setup: {e}")
        raise

if __name__ == "__main__":
    debug_setup()