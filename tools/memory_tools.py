"""
Memory Tools for Agent

Provides tools for the agent to save and retrieve memories across sessions.
"""
import time
import re
from pathlib import Path
from typing import Literal


def save_memory(
    content: str,
    memory_type: Literal["user", "feedback", "project", "reference"],
    name: str,
    description: str
) -> str:
    """
    Save a memory to persistent storage.

    Args:
        content: The main content of the memory
        memory_type: Type of memory - user/feedback/project/reference
        name: Short name for the memory (used in frontmatter)
        description: One-line description for future relevance matching

    Returns:
        Success message with filename
    """
    memory_dir = Path("./memory")
    memory_dir.mkdir(exist_ok=True)

    # Generate filename
    timestamp = int(time.time())
    # Sanitize name for filename
    safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')[:40]
    filename = f"{memory_type}_{safe_name}_{timestamp}.md"
    filepath = memory_dir / filename

    # Create memory file with frontmatter
    frontmatter = f"""---
        name: {name}
        description: {description}
        type: {memory_type}
        ---
        {content}
        """

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)

    # Update MEMORY.md index
    _update_memory_index(filename, name, description)

    return f"✅ Memory saved to {filename}"


def read_memory(query: str = "") -> str:
    """
    Read memories from storage.

    Args:
        query: Optional search query to filter memories (searches in name/description)

    Returns:
        Formatted string with all matching memories
    """
    memory_dir = Path("./memory")
    memory_index = memory_dir / "MEMORY.md"

    if not memory_index.exists():
        return "No memories found yet."

    # Read index
    index_content = memory_index.read_text(encoding="utf-8")

    if query:
        # Filter by query
        lines = [line for line in index_content.split('\n')
                 if query.lower() in line.lower()]
        if not lines:
            return f"No memories found matching '{query}'"
        filtered_index = "\n".join(lines)
        return f"Matching memories:\n{filtered_index}"

    return f"All memories:\n{index_content}"


def _update_memory_index(filename: str, name: str, description: str) -> None:
    """Update MEMORY.md with new memory entry."""
    memory_dir = Path("./memory")
    memory_index = memory_dir / "MEMORY.md"

    index_entry = f"- [{name}]({filename}) — {description}\n"

    if memory_index.exists():
        content = memory_index.read_text(encoding="utf-8")
        if filename not in content:
            content += index_entry
            memory_index.write_text(content, encoding="utf-8")
    else:
        header = "# Agent Memory\n\nPersistent knowledge across sessions:\n\n"
        memory_index.write_text(header + index_entry, encoding="utf-8")
