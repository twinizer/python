"""
state.py
"""

"""
State diagram generator for Mermaid.

This module provides functionality to generate state diagrams
with states, transitions, and nested states.
"""

from typing import Any, Dict, List, Optional, Union

from ..base import BaseDiagramGenerator
from ..constants import STATE_STYLES
from ..utils import escape_text


class StateDiagramGenerator(BaseDiagramGenerator):
    """
    Generator for Mermaid state diagrams.
    """

    def generate(
        self,
        states: List[Dict],
        transitions: List[Dict],
        title: Optional[str] = None,
        direction: str = "LR",
        start_state: Optional[str] = None,
        end_states: Optional[List[str]] = None,
    ) -> str:
        """
        Generate a Mermaid state diagram.

        Args:
            states: List of state dictionaries with 'id' and optional 'label', 'type' keys
            transitions: List of transition dictionaries with 'from', 'to', and optional 'label' keys
            title: Optional title for the diagram
            direction: Direction of the diagram (LR, RL, TB, BT)
            start_state: Optional start state ID
            end_states: Optional list of end state IDs

        Returns:
            Mermaid state diagram as a string
        """
        # Validate direction
        valid_directions = ["TB", "BT", "RL", "LR"]
        if direction not in valid_directions:
            direction = "LR"  # Default to left-to-right

        # Add additional directives
        additional_directives = [f"    direction {direction}"]

        content_lines = []

        # Add start state if provided
        if start_state:
            content_lines.append(f"    [*] --> {escape_text(start_state)}")

        # Add states
        for state in states:
            state_lines = self._format_state(state)
            content_lines.extend([f"    {line}" for line in state_lines])

        # Add transitions
        for transition in transitions:
            transition_line = self._format_transition(transition)
            content_lines.append(f"    {transition_line}")

        # Add end states if provided
        if end_states:
            for end_state in end_states:
                content_lines.append(f"    {escape_text(end_state)} --> [*]")

        # Format the diagram
        return self._format_diagram(
            "stateDiagram-v2", content_lines, title, additional_directives
        )

    def _format_state(self, state: Dict) -> List[str]:
        """
        Format a state for a state diagram.

        Args:
            state: State dictionary with 'id' and optional 'label', 'type', 'substates', 'subtransitions' keys

        Returns:
            List of formatted state lines
        """
        state_lines = []
        state_id = escape_text(state["id"])

        # Get state label
        if "label" in state:
            state_label = escape_text(state["label"])
            state_lines.append(f"{state_id}: {state_label}")

        # Add state style based on type
        if "type" in state:
            state_type = state["type"].lower()

            if state_type == "choice":
                state_lines.append(f"state {state_id} {{")
                state_lines.append(f"    {state_id}")
                state_lines.append("}")
            elif state_type == "composite" or state_type == "nested":
                state_lines.extend(self._format_composite_state(state))
            elif state_type == "note":
                state_lines.append(f"note right of {state_id}")
                note_text = state.get("note", state_id)
                state_lines.append(f"    {escape_text(note_text)}")
                state_lines.append("end note")
            elif state_type in STATE_STYLES:
                # Add specific state style if applicable
                state_style = STATE_STYLES[state_type]
                if state_style:
                    state_lines.append(f"state {state_id} {state_style}")

        return state_lines

    def _format_composite_state(self, state: Dict) -> List[str]:
        """
        Format a composite (nested) state for a state diagram.

        Args:
            state: State dictionary with 'id', 'substates', and optional 'subtransitions' keys

        Returns:
            List of formatted composite state lines
        """
        state_lines = []
        state_id = escape_text(state["id"])

        # Start composite state
        state_lines.append(f"state {state_id} {{")

        # Add substates
        for substate in state.get("substates", []):
            substate_id = escape_text(substate["id"])

            if "label" in substate:
                substate_label = escape_text(substate["label"])
                state_lines.append(f"    {substate_id}: {substate_label}")
            else:
                state_lines.append(f"    {substate_id}")

            # Add substate type if provided
            if "type" in substate and substate["type"] in STATE_STYLES:
                substate_style = STATE_STYLES[substate["type"]]
                if substate_style:
                    state_lines.append(f"    state {substate_id} {substate_style}")

        # Add subtransitions
        for subtrans in state.get("subtransitions", []):
            from_id = escape_text(subtrans["from"])
            to_id = escape_text(subtrans["to"])
            label = escape_text(subtrans.get("label", ""))

            if label:
                state_lines.append(f"    {from_id} --> {to_id}: {label}")
            else:
                state_lines.append(f"    {from_id} --> {to_id}")

        # Close composite state
        state_lines.append("}")

        return state_lines

    def _format_transition(self, transition: Dict) -> str:
        """
        Format a transition for a state diagram.

        Args:
            transition: Transition dictionary with 'from', 'to', and optional 'label' keys

        Returns:
            Formatted transition line
        """
        from_id = escape_text(transition["from"])
        to_id = escape_text(transition["to"])
        label = escape_text(transition.get("label", ""))

        if label:
            return f"{from_id} --> {to_id}: {label}"
        else:
            return f"{from_id} --> {to_id}"


def generate_state_diagram(
    states: List[Dict],
    transitions: List[Dict],
    title: Optional[str] = None,
    direction: str = "LR",
    start_state: Optional[str] = None,
    end_states: Optional[List[str]] = None,
    theme: str = "default",
) -> str:
    """
    Generate a Mermaid state diagram.

    Args:
        states: List of state dictionaries with 'id' and optional 'label', 'type' keys
        transitions: List of transition dictionaries with 'from', 'to', and optional 'label' keys
        title: Optional title for the diagram
        direction: Direction of the diagram (LR, RL, TB, BT)
        start_state: Optional start state ID
        end_states: Optional list of end state IDs
        theme: Theme for the diagram ('default', 'dark', 'forest', 'neutral')

    Returns:
        Mermaid state diagram as a string
    """
    generator = StateDiagramGenerator(theme)
    return generator.generate(
        states, transitions, title, direction, start_state, end_states
    )
