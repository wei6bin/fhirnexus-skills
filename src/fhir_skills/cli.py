#!/usr/bin/env python3
"""CLI tool for installing FHIR Engine Claude skills."""

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import Optional


def get_skills_source_dir() -> Path:
    """Get the path to the bundled skills directory."""
    return Path(__file__).parent / "skills"


def get_target_dir(custom_path: Optional[str] = None) -> Path:
    """Get the target installation directory."""
    if custom_path:
        return Path(custom_path).resolve()
    return Path.cwd()


def install_skills(target_path: Optional[str] = None, force: bool = False) -> int:
    """
    Install FHIR Engine Claude skills to a project.

    Args:
        target_path: Custom installation path (default: current directory)
        force: Overwrite existing skills without confirmation

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    source_dir = get_skills_source_dir()
    target_base = get_target_dir(target_path)
    target_dir = target_base / ".claude" / "skills"

    # Validate source directory exists
    if not source_dir.exists():
        print("❌ Error: Skills source directory not found in package.", file=sys.stderr)
        print(f"   Expected at: {source_dir}", file=sys.stderr)
        return 1

    # Check if target already exists
    if target_dir.exists() and not force:
        print(f"⚠️  Skills directory already exists at: {target_dir}")
        response = input("   Overwrite existing skills? [y/N]: ").strip().lower()
        if response not in ('y', 'yes'):
            print("   Installation cancelled.")
            return 0

    # Create target directory
    try:
        target_dir.parent.mkdir(parents=True, exist_ok=True)

        # Remove existing if present
        if target_dir.exists():
            print(f"🗑️  Removing existing skills at: {target_dir}")
            shutil.rmtree(target_dir)

        # Copy skills
        print(f"📦 Installing FHIR Engine skills to: {target_dir}")
        shutil.copytree(source_dir, target_dir)

        # Count installed skills
        skill_files = list(target_dir.rglob("SKILL.md"))
        skill_count = len(skill_files)

        print(f"✅ Successfully installed {skill_count} skills!")
        print()
        print("📚 Available skills:")

        # List installed skills
        skill_dirs = sorted(set(f.parent.name for f in skill_files))
        for skill_dir in skill_dirs:
            print(f"   • {skill_dir}")

        print()
        print("🚀 Next steps:")
        print("   1. Open your project in Claude Code")
        print("   2. Skills will activate automatically when relevant")
        print("   3. Try asking: 'Create CRUD handlers for Patient resource'")
        print()
        print(f"📖 Documentation: {target_dir / 'README.md'}")

        return 0

    except PermissionError:
        print(f"❌ Error: Permission denied writing to {target_dir}", file=sys.stderr)
        print("   Try running with appropriate permissions.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error during installation: {e}", file=sys.stderr)
        return 1


def list_skills() -> int:
    """List all available skills in the package."""
    source_dir = get_skills_source_dir()

    if not source_dir.exists():
        print("❌ Error: Skills source directory not found in package.", file=sys.stderr)
        return 1

    skill_files = list(source_dir.rglob("SKILL.md"))

    print("📚 FHIR Engine Claude Skills")
    print("=" * 50)
    print()

    # Group by category
    categories = {
        "Troubleshooting & Help": [],
        "Code Generation": [],
        "Analysis & Mapping": []
    }

    for skill_file in skill_files:
        skill_name = skill_file.parent.name
        skill_path = skill_file.relative_to(source_dir)

        # Categorize
        if skill_path.parts[0] == "codegen":
            categories["Code Generation"].append(skill_name)
        elif skill_path.parts[0] == "tasks":
            categories["Analysis & Mapping"].append(skill_name)
        else:
            categories["Troubleshooting & Help"].append(skill_name)

    for category, skills in categories.items():
        if skills:
            print(f"{category}:")
            for skill in sorted(skills):
                print(f"  • {skill}")
            print()

    print(f"Total: {len(skill_files)} skills")
    print()
    print("To install: fhir-skills install")

    return 0


def update_skills(target_path: Optional[str] = None) -> int:
    """Update existing skills installation."""
    print("🔄 Updating FHIR Engine skills...")
    return install_skills(target_path=target_path, force=True)


def show_info() -> int:
    """Show package information."""
    from . import __version__

    print(f"FHIR Engine Claude Skills v{__version__}")
    print()
    print("Claude Code skills for FHIR Engine development")
    print()
    print("Skills help you:")
    print("  • Troubleshoot configuration issues")
    print("  • Generate FHIR handlers and resources")
    print("  • Map custom data models to FHIR")
    print("  • Debug errors and exceptions")
    print()
    print("Commands:")
    print("  fhir-skills install     Install skills to current project")
    print("  fhir-skills list        List available skills")
    print("  fhir-skills update      Update existing skills")
    print("  fhir-skills info        Show this information")
    print()
    print("Documentation: https://github.com/ihis/fhir-engine-skills")

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="FHIR Engine Claude Skills - AI-powered development assistance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Install skills to current project
  fhir-skills install

  # Install to specific project
  fhir-skills install --path /path/to/my-fhir-project

  # List available skills
  fhir-skills list

  # Update existing installation
  fhir-skills update

  # Force install (no confirmation)
  fhir-skills install --force
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Install command
    install_parser = subparsers.add_parser(
        "install",
        help="Install skills to a project"
    )
    install_parser.add_argument(
        "--path",
        type=str,
        help="Target project path (default: current directory)"
    )
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing skills without confirmation"
    )

    # Update command
    update_parser = subparsers.add_parser(
        "update",
        help="Update existing skills installation"
    )
    update_parser.add_argument(
        "--path",
        type=str,
        help="Target project path (default: current directory)"
    )

    # List command
    subparsers.add_parser(
        "list",
        help="List available skills"
    )

    # Info command
    subparsers.add_parser(
        "info",
        help="Show package information"
    )

    args = parser.parse_args()

    # Default to info if no command
    if not args.command:
        return show_info()

    # Execute command
    if args.command == "install":
        return install_skills(
            target_path=args.path,
            force=args.force
        )
    elif args.command == "update":
        return update_skills(target_path=args.path)
    elif args.command == "list":
        return list_skills()
    elif args.command == "info":
        return show_info()
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
