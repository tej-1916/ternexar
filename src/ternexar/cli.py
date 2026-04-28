import typer
from ternexar.boot import boot_sequence
from ternexar.config import config_manager
from ternexar.ui import ui

app = typer.Typer(
    name="tx",
    help="TERNEXAR: A premium, terminal-native AI command center.",
    rich_markup_mode="rich",
    no_args_is_help=False
)

config_app = typer.Typer(help="Manage TERNEXAR configuration.")
app.add_typer(config_app, name="config")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Run the standard boot sequence and health check."""
    if ctx.invoked_subcommand is None:
        boot_sequence.run()

@app.command()
def doctor():
    """Explicit deep-dive diagnostic with live-updating progress."""
    boot_sequence.run(show_splash=True, deep_diagnostic=True)

@config_app.command("init")
def config_init():
    """Initialize default configuration."""
    config_manager.ensure_config()
    ui.info("Configuration initialized.")

@config_app.command("view")
def config_view():
    """View current configuration."""
    config_data = config_manager.load()
    ui.config_view(config_data)

@config_app.command("reset")
def config_reset():
    """Reset configuration to defaults."""
    config_manager.reset()
    ui.info("Configuration reset to defaults.")

if __name__ == "__main__":
    app()
