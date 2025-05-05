"""
sequence.py
"""

"""
Sequence diagram generator for Mermaid.

This module provides functionality to generate sequence diagrams
with actors, messages, notes, and activation/deactivation.
"""

from typing import Any, Dict, List, Optional, Union

from ..base import BaseDiagramGenerator
from ..constants import SEQUENCE_ARROWS
from ..utils import escape_text


class SequenceDiagramGenerator(BaseDiagramGenerator):
    """
    Generator for Mermaid sequence diagrams.
    """

    def generate(
        self,
        actors: List[Dict],
        messages: List[Dict],
        title: Optional[str] = None,
        autonumber: bool = False,
    ) -> str:
        """
        Generate a Mermaid sequence diagram.

        Args:
            actors: List of actor dictionaries with 'name' and optional 'type' keys
            messages: List of message dictionaries with 'from', 'to', 'text', and optional 'type' keys
            title: Optional title for the diagram
            autonumber: Whether to autonumber the messages

        Returns:
            Mermaid sequence diagram as a string
        """
        content_lines = []

        # Add autonumbering if enabled
        if autonumber:
            content_lines.append("    autonumber")

        # Add participants/actors with proper types
        for actor in actors:
            actor_line = self._format_actor(actor)
            content_lines.append(f"    {actor_line}")

        # Add messages
        for msg in messages:
            msg_lines = self._format_message(msg)
            content_lines.extend([f"    {line}" for line in msg_lines])

        # Format the diagram
        return self._format_diagram("sequenceDiagram", content_lines, title)

    def _format_actor(self, actor: Dict) -> str:
        """
        Format an actor for a sequence diagram.

        Args:
            actor: Actor dictionary with 'name' and optional 'type' keys

        Returns:
            Formatted actor line
        """
        name = escape_text(actor["name"])
        actor_type = actor.get("type", "participant")

        valid_types = [
            "participant",
            "actor",
            "boundary",
            "control",
            "entity",
            "database",
        ]
        if actor_type not in valid_types:
            actor_type = "participant"  # Default to participant if type is invalid

        return f"{actor_type} {name}"

    def _format_message(self, msg: Dict) -> List[str]:
        """
        Format a message for a sequence diagram, including activation/deactivation and notes.

        Args:
            msg: Message dictionary with 'from', 'to', 'text', and optional 'type',
                'activate', 'deactivate', 'note', and 'note_position' keys

        Returns:
            List of formatted message lines
        """
        message_lines = []
        from_actor = escape_text(msg["from"])
        to_actor = escape_text(msg["to"])
        text = escape_text(msg["text"])
        msg_type = msg.get("type", "solid")

        # Get arrow style
        arrow = SEQUENCE_ARROWS.get(msg_type, SEQUENCE_ARROWS["solid"])

        # Add activation if specified
        if "activate" in msg and msg["activate"]:
            message_lines.append(f"activate {to_actor}")

        # Add message
        message_lines.append(f"{from_actor}{arrow}{to_actor}: {text}")

        # Add note if specified
        if "note" in msg:
            note_lines = self._format_note(msg, from_actor, to_actor)
            message_lines.extend(note_lines)

        # Add deactivation if specified
        if "deactivate" in msg and msg["deactivate"]:
            message_lines.append(f"deactivate {to_actor}")

        return message_lines

    def _format_note(self, msg: Dict, from_actor: str, to_actor: str) -> List[str]:
        """
        Format a note for a sequence diagram message.

        Args:
            msg: Message dictionary with 'note' and optional 'note_position' keys
            from_actor: Name of the sending actor
            to_actor: Name of the receiving actor

        Returns:
            List of formatted note lines
        """
        note_text = escape_text(msg["note"])
        note_pos = msg.get("note_position", "over")

        # Determine note target based on position
        if note_pos == "over" and from_actor != to_actor:
            note_target = f"{from_actor},{to_actor}"
        else:
            note_target = to_actor if note_pos == "right of" else from_actor

        # Split note into multiple lines if it contains newlines
        if "\n" in note_text:
            note_lines = []
            note_lines.append(f"Note {note_pos} {note_target}")
            for line in note_text.split("\n"):
                note_lines.append(f"    {line}")
            note_lines.append("end note")
            return note_lines
        else:
            return [f"Note {note_pos} {note_target}: {note_text}"]


def generate_sequence_diagram(
    actors: List[Dict],
    messages: List[Dict],
    title: Optional[str] = None,
    autonumber: bool = False,
    theme: str = "default",
) -> str:
    """
    Generate a Mermaid sequence diagram.

    Args:
        actors: List of actor dictionaries with 'name' and optional 'type' keys
        messages: List of message dictionaries with 'from', 'to', 'text', and optional 'type' keys
        title: Optional title for the diagram
        autonumber: Whether to autonumber the messages
        theme: Theme for the diagram ('default', 'dark', 'forest', 'neutral')

    Returns:
        Mermaid sequence diagram as a string
    """
    generator = SequenceDiagramGenerator(theme)
    return generator.generate(actors, messages, title, autonumber)
