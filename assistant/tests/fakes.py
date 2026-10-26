"""A scripted stand-in for the provider client: each call to `create` returns the next item of the
script, or raises it when it is an exception. Every call's arguments are kept in `calls`."""

from types import SimpleNamespace


def usage(tokens):
    return SimpleNamespace(total_tokens=tokens) if tokens is not None else None


def text_response(content, tokens=100):
    message = SimpleNamespace(content=content, tool_calls=None)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=usage(tokens))


def tool_response(*calls, tokens=100):
    """`calls` are (name, arguments) pairs, or (name, arguments, extra) when the provider sent
    fields beyond the standard ones (the SDK keeps those in `model_extra`); the ids are call_1,
    call_2..."""
    tool_calls = [
        SimpleNamespace(
            id=f"call_{index}",
            type="function",
            function=SimpleNamespace(name=name, arguments=arguments),
            model_extra=extra[0] if extra else None,
        )
        for index, (name, arguments, *extra) in enumerate(calls, start=1)
    ]
    message = SimpleNamespace(content=None, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=usage(tokens))


class FakeClient:
    def __init__(self, *script):
        self.script = list(script)
        self.calls = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item
