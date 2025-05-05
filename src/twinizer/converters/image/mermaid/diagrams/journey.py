"""
journey.py
"""

"""
User journey diagram generator for Mermaid.

This module provides functionality to generate user journey diagrams
with tasks, sections, and scores.
"""

from typing import Any, Dict, List, Optional, Union

from ..base import BaseDiagramGenerator
from ..utils import escape_text


class JourneyDiagramGenerator(BaseDiagramGenerator):
    """
    Generator for Mermaid user journey diagrams.
    """

    def generate(self, journeys: List[Dict], title: Optional[str] = None) -> str:
        """
        Generate a Mermaid user journey diagram.

        Args:
            journeys: List of journey dictionaries with 'title', 'sections', and 'tasks' keys
            title: Optional title for the diagram

        Returns:
            Mermaid user journey diagram as a string
        """
        content_lines = []

        # Add journeys
        for journey in journeys:
            journey_lines = self._format_journey(journey)
            content_lines.extend([f"    {line}" for line in journey_lines])

        # Format the diagram
        return self._format_diagram("journey", content_lines, title)

    def _format_journey(self, journey: Dict) -> List[str]:
        """
        Format a journey for a user journey diagram.

        Args:
            journey: Journey dictionary with 'title' and 'tasks' keys

        Returns:
            List of formatted journey lines
        """
        journey_lines = []
        journey_title = escape_text(journey["title"])

        # Add section header
        journey_lines.append(f"section {journey_title}")

        # Add tasks
        for task in journey.get("tasks", []):
            task_line = self._format_task(task)
            journey_lines.append(f"    {task_line}")

        return journey_lines

    def _format_task(self, task: Dict) -> str:
        """
        Format a task for a user journey diagram.

        Args:
            task: Task dictionary with 'name', optional 'score' (1-5), and optional 'actors'

        Returns:
            Formatted task line
        """
        task_name = escape_text(task["name"])
        task_score = task.get("score", 3)  # Default score is 3 (out of 5)

        # Ensure score is in valid range
        if task_score < 1:
            task_score = 1
        elif task_score > 5:
            task_score = 5

        # Format task with optional actors
        task_actors = task.get("actors", [])
        if task_actors:
            actors_str = ": " + ",".join(escape_text(actor) for actor in task_actors)
            return f"{task_name}: {task_score}{actors_str}"
        else:
            return f"{task_name}: {task_score}"


def generate_journey_diagram(
    journeys: List[Dict], title: Optional[str] = None, theme: str = "default"
) -> str:
    """
    Generate a Mermaid user journey diagram.

    Args:
        journeys: List of journey dictionaries with 'title' and 'tasks' keys
        title: Optional title for the diagram
        theme: Theme for the diagram ('default', 'dark', 'forest', 'neutral')

    Returns:
        Mermaid user journey diagram as a string
    """
    generator = JourneyDiagramGenerator(theme)
    return generator.generate(journeys, title)
