import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.patch_stdout import patch_stdout

from ternexar.router import router, Intent
from ternexar.do import handle_do
from ternexar.ask import handle_ask
from ternexar.plan import handle_plan
from ternexar.preview import handle_preview
from ternexar.ui import ui

OPERATOR_STYLE = Style.from_dict({
    "default": "bg:#2b2b2b #ffffff",
    "prompt": "#00FFFF bold",
    "placeholder": "#666666 italic",
    "bottom-toolbar": "bg:#1e1e1e #888888",
    "bottom-toolbar.safety": "#00ff00 bold",
    "bottom-toolbar.context": "#00FFFF",
    "bottom-toolbar.exit": "#ff5555",
})

def bottom_toolbar():
    return HTML(
        ' Safety: <style class="bottom-toolbar.safety">LOW-only</style> | '
        'Context: <style class="bottom-toolbar.context">@file enabled</style> | '
        'Exit: <style class="bottom-toolbar.exit">Ctrl+D or exit</style> '
    )

def route_operator_input(text: str):
    """Main routing logic for operator input."""
    if not text.strip():
        return

    if text.strip().lower() in ["exit", "quit"]:
        ui.info("Exiting Operator Mode...")
        sys.exit(0)

    # 1. Resolve context (@file)
    prompt_text, context_blobs = router.resolve_context(text)
    
    # Combine text with context if available
    if context_blobs:
        full_prompt = f"{prompt_text}\n\n" + "\n\n".join(context_blobs)
    else:
        full_prompt = prompt_text

    # 2. Classify intent
    intent = router.classify_intent(text)

    # 3. Route to handler
    try:
        if intent == Intent.DO:
            ui.info(f"Routing to [success]EXECUTION[/]...")
            handle_do(text)
        elif intent == Intent.ASK:
            ui.info(f"Routing to [info]ASK[/]...")
            handle_ask(full_prompt)
        elif intent == Intent.PLAN:
            ui.info(f"Routing to [brand]PLAN[/]...")
            handle_plan(full_prompt)
        elif intent == Intent.PREVIEW:
            ui.info(f"Routing to [warning]PREVIEW[/]...")
            handle_preview(full_prompt)
        elif intent == Intent.REFUSE:
            ui.render_refusal(text, "Dangerous command or blocked pattern detected.")
        else:
            ui.info("Unknown input. Try a question, task, or safe command.")
            ui.hint("Examples: 'ls -la', 'what is recursion?', 'explain @README.md'")
    except SystemExit:
        # Typer/SysExit might be raised by handlers; we want to stay in the loop
        pass
    except Exception as e:
        ui.error(f"Routing error: {str(e)}")

def handle_operator():
    """Starts the interactive TERNEXAR Operator session."""
    ui.operator_welcome()
    
    # In-memory session history only for v1.1
    session = PromptSession(
        message=HTML("<prompt>&gt;</prompt> "),
        style=OPERATOR_STYLE,
        bottom_toolbar=bottom_toolbar,
    )

    while True:
        try:
            with patch_stdout():
                user_input = session.prompt(placeholder="Type your message or @path/to/file")
                
            if user_input:
                route_operator_input(user_input)
                
        except KeyboardInterrupt:
            # Ctrl+C clears the line, doesn't exit the loop
            continue
        except EOFError:
            # Ctrl+D exits
            ui.info("\nExiting Operator Mode...")
            break
        except Exception as e:
            ui.error(f"Session error: {str(e)}")
            break

    ui.render_operator_exit()
