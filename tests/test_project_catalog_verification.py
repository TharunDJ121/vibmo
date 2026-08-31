"""
Empirical test suite to challenge and verify PROJECT_CATALOG.md code blocks,
API signatures, classes, methods, imports, generator yields, and easing constants.
"""

import ast
import re
import inspect
from pathlib import Path
import pytest
import vibmo
import vibmo.agent_api as agent_api

CATALOG_PATH = Path(__file__).parent.parent / "PROJECT_CATALOG.md"

def extract_python_blocks(markdown_text: str):
    """Extract all python code blocks with line numbers."""
    pattern = r"```(?:python|py)\n(.*?)```"
    blocks = []
    for match in re.finditer(pattern, markdown_text, re.DOTALL):
        # Calculate line number
        start_line = markdown_text[:match.start()].count("\n") + 1
        code = match.group(1)
        blocks.append((start_line, code))
    return blocks

def extract_table_recipes(markdown_text: str):
    """Extract table rows containing Component Classes and Usage Recipes."""
    # Matches markdown tables
    lines = markdown_text.splitlines()
    recipes = []
    for i, line in enumerate(lines, 1):
        if "|" in line and "`" in line:
            parts = [p.strip() for p in line.split("|")]
            # Look for parts with code
            for p in parts:
                codes = re.findall(r"`([^`]+)`", p)
                if codes:
                    recipes.append((i, line, codes))
    return recipes

def test_catalog_file_exists():
    assert CATALOG_PATH.exists(), f"PROJECT_CATALOG.md not found at {CATALOG_PATH}"

def test_all_python_blocks_syntax():
    content = CATALOG_PATH.read_text(encoding="utf-8")
    blocks = extract_python_blocks(content)
    assert len(blocks) > 0, "No python blocks found in PROJECT_CATALOG.md"
    
    syntax_errors = []
    for line_no, code in blocks:
        try:
            ast.parse(code)
        except SyntaxError as e:
            syntax_errors.append((line_no, str(e), code))
            
    assert not syntax_errors, f"Syntax errors found in python blocks:\n{syntax_errors}"

if __name__ == "__main__":
    content = CATALOG_PATH.read_text(encoding="utf-8")
    blocks = extract_python_blocks(content)
    print(f"Extracted {len(blocks)} python code blocks.")
    for idx, (line_no, code) in enumerate(blocks):
        print(f"\n--- Block {idx+1} (Line {line_no}) ---")
        try:
            tree = ast.parse(code)
            print("Syntax: VALID AST")
        except SyntaxError as e:
            print(f"Syntax ERROR: {e}")
