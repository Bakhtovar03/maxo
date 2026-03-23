from __future__ import annotations

import os.path
from collections.abc import Iterable, Sequence
from typing import TYPE_CHECKING

from maxo.dialogs.setup import collect_dialogs
from maxo.dialogs.widgets.kbd import Back, Cancel, Group, Next, Start, SwitchTo
from maxo.fsm import State
from maxo.routing.interfaces import BaseRouter

if TYPE_CHECKING:
    from diagrams import Node

    from maxo.dialogs.api.internal.window import WindowProtocol
    from maxo.dialogs.api.protocols.dialog import DialogProtocol

ICON_PATH = os.path.join(os.path.dirname(__file__), "icon.png")


def _widget_edges(
    nodes: dict[State, Node],
    dialog: DialogProtocol,
    starts: list[tuple[State, State]],
    current_state: State,
    kbd: object,
) -> None:
    from diagrams import Edge

    states = list(dialog.windows.keys())
    if isinstance(kbd, Start):
        nodes[current_state] >> Edge(color="#338a3e") >> nodes[kbd.state]
    elif isinstance(kbd, SwitchTo):
        nodes[current_state] >> Edge(color="#0086c3") >> nodes[kbd.state]
    elif isinstance(kbd, Next):
        idx = states.index(current_state)
        nodes[current_state] >> Edge(color="#0086c3") >> nodes[states[idx + 1]]
    elif isinstance(kbd, Back):
        idx = states.index(current_state)
        nodes[current_state] >> Edge(color="grey") >> nodes[states[idx - 1]]
    elif isinstance(kbd, Cancel):
        for from_, to_ in starts:
            if to_.group == current_state.group:
                nodes[current_state] >> Edge(color="grey", style="dashed") >> nodes[from_]


def _walk_keyboard(
    nodes: dict[State, Node],
    dialog: DialogProtocol,
    starts: list[tuple[State, State]],
    current_state: State,
    keyboards: Sequence[object],
) -> None:
    for kbd in keyboards:
        if isinstance(kbd, Group):
            _walk_keyboard(nodes, dialog, starts, current_state, kbd.buttons)
        else:
            _widget_edges(nodes, dialog, starts, current_state, kbd)


def _find_starts(
    current_state: State,
    keyboards: Sequence[object],
) -> Iterable[tuple[State, State]]:
    for kbd in keyboards:
        if isinstance(kbd, Group):
            yield from _find_starts(current_state, kbd.buttons)
        elif isinstance(kbd, Start):
            yield current_state, kbd.state


def render_transitions(
    router: BaseRouter,
    title: str = "Maxo Dialog",
    filename: str = "maxo_dialog",
    format: str = "png",
) -> None:
    """Render a PNG state-transition diagram for all dialogs in the router.

    Requires: pip install maxo[preview] and system graphviz (brew install graphviz).
    """
    from diagrams import Cluster, Diagram
    from diagrams.custom import Custom

    from maxo.dialogs.window import Window

    dialogs = list(collect_dialogs(router))
    with Diagram(title, filename=filename, outformat=format, show=False):
        nodes: dict[State, Node] = {}
        for dialog in dialogs:
            with Cluster(dialog.states_group_name()):
                for state, window in dialog.windows.items():
                    nodes[state] = Custom(
                        label=state._state or "",
                        icon_path=ICON_PATH,
                    )

        starts: list[tuple[State, State]] = []
        for dialog in dialogs:
            for state, window in dialog.windows.items():
                if isinstance(window, Window):
                    starts.extend(_find_starts(state, [window.keyboard]))

        for dialog in dialogs:
            for state, window in dialog.windows.items():
                if not isinstance(window, Window):
                    continue
                _walk_keyboard(nodes, dialog, starts, state, [window.keyboard])
                if window.preview_add_transitions:
                    _walk_keyboard(
                        nodes, dialog, starts, state, window.preview_add_transitions
                    )
