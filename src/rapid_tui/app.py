#!/usr/bin/env python3

from textual.app import App, ComposeResult
from textual.containers import Center, Middle
from textual.widgets import Header, Footer, Static


class HelloWorldApp(App):
    """A simple Hello World Textual application."""

    CSS = """
    .hello {
        width: 100%;
        height: 100%;
        content-align: center middle;
        text-style: bold;
        color: cyan;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the layout of the application."""
        yield Header()
        yield Footer()
        with Center():
            with Middle():
                yield Static("Hello, World! 🌍\n\nWelcome to Rapid TUI!", classes="hello")


def main():
    """Main entry point for the rapid-tui command."""
    app = HelloWorldApp()
    app.run()


if __name__ == "__main__":
    main()