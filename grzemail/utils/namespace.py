import re

split_namespace_groups = re.compile(
    r'(?:(?:NIL)|\((?:\("([^"]*)" "([^"]*)"\)\s*)+\))+'
)


def parse_namespace(raw: bytes):
    string = raw.decode("ascii")
    personal, _, _ = split_namespace_groups.findall(string)
    return personal[0], personal[1]


parse_mailbox_returns = re.compile(r'\(([^\)]*)\) "([^"]*)" ([\S]*)')


def parse_mailbox(raw: bytes):
    string = raw.decode("ascii")
    if (match := parse_mailbox_returns.match(string)) is not None:
        flags, _, name = match.groups()
        return {
            "flags": list(x.replace("\\", "") for x in flags.split(" ")),
            "name": name,
        }
    raise Exception("Failed to parse mailboxes")
