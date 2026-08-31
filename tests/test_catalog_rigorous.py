"""
Rigorous empirical tester for PROJECT_CATALOG.md.
Tests:
1. Python code blocks (syntax, compilation, execution)
2. All table usage recipes (syntax, import resolution, instantiation, method calls)
3. Class catalog exports in vibmo and vibmo.agent_api
4. Easing enums, Color constants, and Generator yield semantics
"""

import ast
import textwrap
import traceback
import sys
import os
import re
import pathlib

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import vibmo
import vibmo.agent_api as agent_api

CATALOG_PATH = pathlib.Path(__file__).parent.parent / "PROJECT_CATALOG.md"



def parse_markdown_blocks(filepath):
    lines = filepath.read_text(encoding="utf-8").splitlines()
    in_block = False
    lang = ""
    block_lines = []
    start_line = 0
    blocks = []
    
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            if not in_block:
                in_block = True
                lang = line.strip()[3:].strip()
                start_line = i
                block_lines = []
            else:
                in_block = False
                blocks.append({
                    "start_line": start_line,
                    "end_line": i,
                    "lang": lang,
                    "content": "\n".join(block_lines)
                })
        elif in_block:
            block_lines.append(line)
            
    return blocks

def parse_markdown_tables(filepath):
    lines = filepath.read_text(encoding="utf-8").splitlines()
    tables = []
    current_table = []
    table_start = 0
    
    for i, line in enumerate(lines, 1):
        if "|" in line:
            if not current_table:
                table_start = i
            current_table.append((i, line))
        else:
            if current_table:
                tables.append((table_start, current_table))
                current_table = []
    if current_table:
        tables.append((table_start, current_table))
    return tables

def analyze():
    print("=" * 80)
    print("EMPIRICAL TEST SUITE: PROJECT_CATALOG.md VERIFICATION")
    print("=" * 80)
    
    blocks = parse_markdown_blocks(CATALOG_PATH)
    print(f"\n1. Found {len(blocks)} total fenced code blocks.")
    
    py_blocks = [b for b in blocks if b["lang"] in ("python", "py")]
    print(f"   Python blocks: {len(py_blocks)}")
    
    # 1. Check Python code blocks
    block_results = []
    for idx, b in enumerate(py_blocks, 1):
        raw_code = b["content"]
        dedented = textwrap.dedent(raw_code).strip()
        start = b["start_line"]
        end = b["end_line"]
        
        # AST Check
        syntax_ok = True
        syntax_err = None
        try:
            tree = ast.parse(dedented)
        except SyntaxError as e:
            syntax_ok = False
            syntax_err = str(e)
            
        # Exec Check
        exec_ok = True
        exec_err = None
        
        if syntax_ok:
            # Prepare execution sandbox with agent_api
            sandbox = {}
            exec("from vibmo.agent_api import *", sandbox)
            sandbox["__name__"] = "__sandbox__"
            
            # Mock or dummy scene methods if needed, or run as is
            try:
                exec(dedented, sandbox)
            except Exception as e:
                exec_ok = False
                exec_err = f"{type(e).__name__}: {str(e)}"
                
        block_results.append({
            "idx": idx,
            "start": start,
            "end": end,
            "code_preview": dedented.splitlines()[0] if dedented.splitlines() else "",
            "syntax_ok": syntax_ok,
            "syntax_err": syntax_err,
            "exec_ok": exec_ok,
            "exec_err": exec_err,
            "raw_code": dedented
        })

    print("\n--- Python Code Block Analysis ---")
    for res in block_results:
        status = "PASS" if (res["syntax_ok"] and res["exec_ok"]) else "FAIL"
        print(f"Block {res['idx']} (Lines {res['start']}-{res['end']}) [{status}]: {res['code_preview'][:50]}")
        if not res["syntax_ok"]:
            print(f"  SYNTAX ERROR: {res['syntax_err']}")
        if not res["exec_ok"]:
            print(f"  EXEC ERROR: {res['exec_err']}")

    # 2. Extract Table Recipes & Classes
    print("\n2. Analyzing Markdown Tables & Usage Recipes...")
    tables = parse_markdown_tables(CATALOG_PATH)
    print(f"   Found {len(tables)} tables.")
    
    table_recipe_results = []
    class_export_results = []
    
    for start_line, rows in tables:
        header_line = rows[0][1] if rows else ""
        if "Component Classes" in header_line or "Usage Recipe" in header_line or "Classes" in header_line:
            print(f"\nProcessing Catalog Table at line {start_line}...")
            for line_no, row_str in rows[2:]:
                cells = [c.strip() for c in row_str.split("|")[1:-1]]
                if len(cells) >= 3:
                    suite_name = cells[0]
                    comp_classes_cell = cells[1]
                    recipe_cell = cells[2]
                    
                    # Extract classes
                    class_names = re.findall(r"`([A-Za-z0-9_]+)`", comp_classes_cell)
                    for cls_name in class_names:
                        in_vibmo = hasattr(vibmo, cls_name)
                        in_agent_api = hasattr(agent_api, cls_name)
                        class_export_results.append({
                            "line": line_no,
                            "suite": suite_name,
                            "class": cls_name,
                            "in_vibmo": in_vibmo,
                            "in_agent_api": in_agent_api
                        })
                    
                    # Extract recipes
                    recipes = re.findall(r"`([^`]+)`", recipe_cell)
                    for recipe in recipes:
                        recipe_clean = recipe.replace("&gt;", ">").replace("&lt;", "<").strip()
                        is_generator = "yield " in recipe_clean
                        
                        r_syntax_ok = True
                        r_syntax_err = None
                        r_exec_ok = True
                        r_exec_err = None
                        
                        # Syntax test
                        try:
                            if is_generator:
                                ast.parse(f"def _test_gen():\n    {recipe_clean}")
                            else:
                                ast.parse(recipe_clean)
                        except SyntaxError as e:
                            r_syntax_ok = False
                            r_syntax_err = str(e)
                            
                        # Execution test in sandbox
                        if r_syntax_ok:
                            sandbox = {}
                            exec("from vibmo.agent_api import *", sandbox)
                            dummy_scene = agent_api.Scene(duration=1.0)
                            sandbox["scene"] = dummy_scene
                            sandbox["app_ui"] = agent_api.GlassCard()
                            sandbox["health_ui"] = agent_api.GlassCard()
                            sandbox["checkout_ui"] = agent_api.GlassCard()
                            sandbox["notes_ui"] = agent_api.GlassCard()
                            sandbox["home_ui"] = agent_api.GlassCard()
                            sandbox["game_node"] = agent_api.GlassCard()
                            sandbox["math"] = __import__("math")
                            
                            try:
                                if is_generator:
                                    wrapper = f"def _test_gen():\n    {recipe_clean}\ng = _test_gen()\nfor item in g:\n    pass"
                                    exec(wrapper, sandbox)
                                else:
                                    exec(recipe_clean, sandbox)
                            except Exception as e:
                                r_exec_ok = False
                                r_exec_err = f"{type(e).__name__}: {str(e)}"
                                
                        table_recipe_results.append({
                            "line": line_no,
                            "suite": suite_name,
                            "recipe": recipe_clean,
                            "syntax_ok": r_syntax_ok,
                            "syntax_err": r_syntax_err,
                            "exec_ok": r_exec_ok,
                            "exec_err": r_exec_err
                        })

    # Summary of Class Exports
    missing_classes = [c for c in class_export_results if not c["in_agent_api"]]
    print(f"\n================================================================================")
    print(f"CLASS EXPORT SUMMARY")
    print(f"================================================================================")
    print(f"Total Classes cataloged in tables: {len(class_export_results)}")
    print(f"Missing from agent_api: {len(missing_classes)}")
    if missing_classes:
        for mc in missing_classes:
            print(f"  MISSING CLASS: line {mc['line']} [{mc['suite']}] -> {mc['class']} (in_vibmo={mc['in_vibmo']})")

    # Summary of Table Recipes
    failed_recipes = [r for r in table_recipe_results if not (r["syntax_ok"] and r["exec_ok"])]
    print(f"\n================================================================================")
    print(f"TABLE RECIPE EXECUTION SUMMARY")
    print(f"================================================================================")
    print(f"Total Table Recipes tested: {len(table_recipe_results)}")
    print(f"Passed recipes: {len(table_recipe_results) - len(failed_recipes)}")
    print(f"Failed recipes: {len(failed_recipes)}")
    if failed_recipes:
        for fr in failed_recipes:
            print(f"\n  FAILED RECIPE at line {fr['line']} [{fr['suite']}]:")
            print(f"    Code: {fr['recipe']}")
            if not fr["syntax_ok"]:
                print(f"    Syntax: {fr['syntax_err']}")
            if not fr["exec_ok"]:
                print(f"    Exec: {fr['exec_err']}")

    # 3. Check All Easing Constants mentioned in doc
    print(f"\n================================================================================")
    print(f"EASING CONSTANTS VERIFICATION")
    print(f"================================================================================")
    content = CATALOG_PATH.read_text(encoding="utf-8")
    ease_mentions = re.findall(r"Ease\.([A-Za-z0-9_]+)", content)
    ease_set = sorted(set(ease_mentions))
    print(f"Found {len(ease_mentions)} Ease references ({len(ease_set)} unique): {ease_set}")
    for e in ease_set:
        exists_on_ease = hasattr(agent_api.Ease, e)
        print(f"  Ease.{e}: {'EXISTS' if exists_on_ease else 'MISSING'}")

    # 4. Check All Colors mentioned in doc
    print(f"\n================================================================================")
    print(f"COLORS CONSTANTS VERIFICATION")
    print(f"================================================================================")
    color_mentions = re.findall(r"colors\.([A-Z0-9_]+)", content)
    color_set = sorted(set(color_mentions))
    print(f"Found {len(color_mentions)} colors.* references ({len(color_set)} unique): {color_set}")
    for c in color_set:
        exists_on_colors = hasattr(agent_api.colors, c)
        print(f"  colors.{c}: {'EXISTS' if exists_on_colors else 'MISSING'}")


if __name__ == "__main__":
    analyze()
