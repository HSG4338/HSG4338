#!/usr/bin/env python3
"""
Agentic AI System — CLI Entry Point.
Usage: python main.py "Your goal here"
       python main.py --ui
       python main.py --validate
"""

import os
import sys
import argparse

# Always run from the project root regardless of where the script was launched from
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

import cli


def run_goal(goal: str):
    from orchestrator.orchestrator import Orchestrator

    cli.section("RUNNING GOAL", cli.C.MAGENTA)
    cli.kv("Goal", goal)
    print()

    with cli.Spinner("Initialising orchestrator", cli.C.CYAN):
        orch = Orchestrator(os.path.join(PROJECT_ROOT, "configs", "config.json"))

    print()
    result = orch.run_goal(goal)
    cli.print_goal_result(result, goal)
    return result


def run_ui():
    import subprocess
    cli.section("WEB UI", cli.C.CYAN)
    cli.info("Starting Flask server...")
    cli.kv("URL", "http://127.0.0.1:5000", value_color=cli.C.CYAN)
    cli.muted("Press Ctrl+C in this window to stop the server.")
    print()
    subprocess.run([sys.executable, os.path.join(PROJECT_ROOT, "ui", "app.py")], cwd=PROJECT_ROOT)


def run_validation():
    cli.print_validation_header()
    import subprocess

    errors = []

    cli.section("1 / 4  --  Required Files", cli.C.BLUE)
    required_files = [
        "agents/__init__.py", "agents/base_agent.py", "agents/planner_agent.py",
        "agents/developer_agent.py", "agents/reviewer_agent.py", "agents/qa_agent.py",
        "agents/repo_manager.py", "orchestrator/__init__.py", "orchestrator/orchestrator.py",
        "memory/__init__.py", "memory/memory_store.py", "models/__init__.py",
        "models/model_manager.py", "ui/app.py", "ui/templates/index.html",
        "tests/test_memory.py", "tests/test_demo_calculator.py",
        "tests/test_repo_manager.py", "configs/config.json",
        "requirements.txt", "install_dependencies.bat", "README.md", ".gitignore",
    ]
    for f in required_files:
        if os.path.exists(f):
            cli.ok(f)
        else:
            cli.fail("MISSING: " + f)
            errors.append("Missing file: " + f)

    cli.section("2 / 4  --  Module Imports", cli.C.BLUE)
    import_checks = [
        ("memory.memory_store",       "MemoryStore"),
        ("models.model_manager",      "generate_text"),
        ("agents.planner_agent",      "PlannerAgent"),
        ("agents.developer_agent",    "DeveloperAgent"),
        ("agents.reviewer_agent",     "ReviewerAgent"),
        ("agents.qa_agent",           "QAAgent"),
        ("agents.repo_manager",       "RepoManagerAgent"),
        ("orchestrator.orchestrator", "Orchestrator"),
    ]
    for module, symbol in import_checks:
        try:
            m = __import__(module, fromlist=[symbol])
            getattr(m, symbol)
            cli.ok(module + "." + symbol)
        except Exception as e:
            cli.fail(module + "." + symbol + "  --  " + str(e))
            errors.append("Import failed: " + module + "." + symbol)

    cli.section("3 / 4  --  Demo Calculator Tests", cli.C.BLUE)
    sp = cli.Spinner("Running calculator tests").start()
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_demo_calculator.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=60, cwd=PROJECT_ROOT
    )
    if result.returncode == 0:
        sp.stop(True, "All calculator tests passed")
    else:
        sp.stop(False, "Calculator tests failed")
        cli.muted(result.stdout[-800:])
        errors.append("Calculator tests failed")

    cli.section("4 / 4  --  Memory Tests", cli.C.BLUE)
    sp = cli.Spinner("Running memory tests").start()
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_memory.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=60, cwd=PROJECT_ROOT
    )
    if result.returncode == 0:
        sp.stop(True, "All memory tests passed")
    else:
        sp.stop(False, "Memory tests failed")
        cli.muted(result.stdout[-400:])
        errors.append("Memory tests failed")

    cli.print_validation_result(errors)
    sys.exit(0 if not errors else 1)


def main():
    parser = argparse.ArgumentParser(description="Agentic AI System")
    parser.add_argument("goal",       nargs="?",           help="Goal to execute")
    parser.add_argument("--ui",       action="store_true", help="Launch web UI")
    parser.add_argument("--validate", action="store_true", help="Run self-validation")

    args = parser.parse_args()

    if args.validate:
        run_validation()
    elif args.ui:
        run_ui()
    elif args.goal:
        run_goal(args.goal)
    else:
        cli.print_menu()
        choice = input("").strip()
        if choice == "1":
            print()
            sys.stdout.write(cli.c(cli.C.CYAN + cli.C.BOLD, "  ❯ ") + cli.c(cli.C.WHITE, "Your goal: "))
            sys.stdout.flush()
            goal = input("").strip()
            if goal:
                run_goal(goal)
            else:
                cli.warn("No goal entered.")
        elif choice == "2":
            run_ui()
        elif choice == "3":
            run_validation()
        elif choice == "4":
            pass
        else:
            cli.warn("Invalid choice.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        cli.warn("Interrupted.")
        print()
    except Exception:
        import traceback
        cli.print_crash(traceback.format_exc())
    finally:
        input(cli.c(cli.C.MUTED, "\n  Press ENTER to exit..."))
