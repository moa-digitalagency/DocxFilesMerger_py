#!/usr/bin/env python3
"""
DocxFilesMerger - Server for CLI documentation
Developed by MOA Digital Agency LLC (https://myoneart.com)
Email: moa@myoneart.com
Copyright © 2025 MOA Digital Agency LLC. All rights reserved.
"""

from cli_app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)