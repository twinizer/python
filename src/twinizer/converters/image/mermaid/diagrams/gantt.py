"""
gantt.py
"""

"""
Gantt chart generator for Mermaid.

This module provides functionality to generate Gantt charts
with sections, tasks, and dependencies.
"""

from typing import Any, Dict, List, Optional, Union

from ..base import BaseDiagramGenerator
from ..utils import escape_text


class GanttChartGenerator(BaseDiagramGenerator):
    """
    Generator for Mermaid Gantt charts.
    """

    # Task status options
    TASK_STATUSES = ["done", "active", "crit", "milestone"]

    def generate(
        self,
        sections: List[Dict],
        title: Optional[str] = None,
        date_format: str = "YYYY-MM-DD",
        excludes: Optional[List[str]] = None,
        includes: Optional[List[str]] = None,
    ) -> str:
        """
        Generate a Mermaid Gantt chart.

        Args:
            sections: List of section dictionaries with 'name' and 'tasks' keys
            title: Optional title for the chart
            date_format: Date format to use
            excludes: Days to exclude (weekends, holidays)
            includes: Days to include

        Returns:
            Mermaid Gantt chart as a string
        """
        content_lines = []

        # Add date format
        content_lines.append(f"    dateFormat {date_format}")

        # Add excludes if provided
        if excludes:
            for exclude in excludes:
                content_lines.append(f"    excludes {exclude}")

        # Add includes if provided
        if includes:
            for include in includes:
                content_lines.append(f"    includes {include}")

        # Add sections and tasks
        for section in sections:
            section_lines = self._format_section(section)
            content_lines.extend([f"    {line}" for line in section_lines])

        # Format the diagram
        return self._format_diagram("gantt", content_lines, title)

    def _format_section(self, section: Dict) -> List[str]:
        """
        Format a section for a Gantt chart.

        Args:
            section: Section dictionary with 'name' and 'tasks' keys

        Returns:
            List of formatted section lines
        """
        section_lines = []
        section_name = escape_text(section["name"])

        # Add section header
        section_lines.append(f"section {section_name}")

        # Add tasks
        for task in section.get("tasks", []):
            task_line = self._format_task(task)
            section_lines.append(f"    {task_line}")

        return section_lines

    def _format_task(self, task: Dict) -> str:
        """
        Format a task for a Gantt chart.

        Args:
            task: Task dictionary with 'name' and optional 'start', 'end',
                'duration', 'status', and 'dependencies' keys

        Returns:
            Formatted task line
        """
        task_name = escape_text(task["name"])
        task_start = task.get("start", "")
        task_end = task.get("end", "")
        task_duration = task.get("duration", "")
        task_dependencies = task.get("dependencies", [])

        # Build task definition
        task_def = f"{task_name} : "

        # Add task status if provided
        if "status" in task:
            status = task["status"]
            if status in self.TASK_STATUSES:
                task_def += f"{status}, "
            else:
                # For custom statuses, we'll use a string
                task_def += f"{status}, "

        # Add task timing
        if task_start and task_end:
            task_def += f"{task_start}, {task_end}"
        elif task_start and task_duration:
            task_def += f"{task_start}, {task_duration}"
        elif task_duration:
            task_def += f"{task_duration}"

        # Add dependencies if any
        if task_dependencies:
            task_def += (
                f", after {', '.join(escape_text(dep) for dep in task_dependencies)}"
            )

        return task_def


def generate_gantt_chart(
    sections: List[Dict],
    title: Optional[str] = None,
    date_format: str = "YYYY-MM-DD",
    excludes: Optional[List[str]] = None,
    includes: Optional[List[str]] = None,
    theme: str = "default",
) -> str:
    """
    Generate a Mermaid Gantt chart.

    Args:
        sections: List of section dictionaries with 'name' and 'tasks' keys
        title: Optional title for the chart
        date_format: Date format to use
        excludes: Days to exclude (weekends, holidays)
        includes: Days to include
        theme: Theme for the diagram ('default', 'dark', 'forest', 'neutral')

    Returns:
        Mermaid Gantt chart as a string
    """
    generator = GanttChartGenerator(theme)
    return generator.generate(sections, title, date_format, excludes, includes)
