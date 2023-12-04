import sys
import subprocess
from enum import Enum, auto

from kizaru.secret import Secrets


class Command(Enum):
    RUN = auto()
    STOP = auto()
    OTHERS = auto()


def _pueue_command(arg: list[str], command: Command = Command.OTHERS, is_remote=True, profile: str = "colered") -> list[
    str]:
    secrets = Secrets()
    if is_remote:
        _pueue_base = ["pueue", "--profile", profile]
    else:
        _pueue_base = ["pueue"]
    match command:
        case Command.RUN:
            if is_remote:
                _pueue_base.extend(["add", "-i", "-w",secrets.PROGRAM_PATH])
            else:
                # _pueue_base.extend(["add"])
                _pueue_base.extend(["add", "-i", "-w", secrets.PROGRAM_LOCAL_PATH])
        case Command.STOP:
            _pueue_base.extend(["kill", "-s", "SIGINT"])
        case Command.OTHERS:
            pass

    _pueue_base.extend(arg)
    return _pueue_base


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        print("see daemon_scripts.py")
        print("this is 'pueue'/'pueue --profile (profile name)'")
        print("subcommands: add/stop/add local/stop local/local")
    else:
        match args[1]:
            case "add":
                if len(args) >= 3 and args[2] == "local":
                    _cmd = _pueue_command(args[3:], Command.RUN, is_remote=False)
                else:
                    _cmd = _pueue_command(args[2:], Command.RUN)
            case "stop":
                if len(args) >= 3 and args[2] == "local":
                    _cmd = _pueue_command(args[3:], Command.STOP, is_remote=False)
                else:
                    _cmd = _pueue_command(args[2:], Command.STOP)
            case "local":
                _cmd = _pueue_command(args[2:], is_remote=False)
            case _unknown:
                _cmd = _pueue_command(args[1:])
        subprocess.run(_cmd)
