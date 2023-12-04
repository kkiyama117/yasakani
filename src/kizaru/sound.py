import asyncio
import psutil
from pathlib import Path
from typing import Optional

from loguru import logger


async def _play_sound(relative_path: str = "test.wav", timeout: Optional[float] = None, debug=False):
    # init vars
    stdout = None
    stderr = None
    data_dir = Path.cwd() / "data"
    wav = str(data_dir / relative_path)
    # start
    logger.debug(f"cwd: {Path.cwd()}")
    cmd = " ".join(['aplay', wav])
    logger.debug(f"sound command is: {cmd}")
    # ONLY FOR DEBUG MODE
    if debug:
        logger.debug(f"DUMMY SOUND PLAY")
        await asyncio.sleep(2.0)
        logger.debug(f"DUMMY SOUND STOPPED")
        # BLEAK;
        return
    # ONLY FOR REAL MODE BELOW
    logger.debug(f"SOUND PLAY")
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    # run sound process with/without timeout
    if timeout is not None:
        try:
            output = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            stdout, stderr = output
        except asyncio.CancelledError:
            proc.terminate()
            raise
        except asyncio.TimeoutError:
            if proc.returncode is not None:
                parent = psutil.Process(proc.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
    else:
        stdout, stderr = await proc.communicate()

    # print result
    if proc.returncode != 0:
        logger.error(f"sound play({cmd!r}) crashed")
        raise OSError(proc.returncode, proc.stderr)
    else:
        logger.debug(f"sound play({cmd!r}) finished successfully with {proc.returncode}")
        # aplay output is stderr
        if stderr:
            logger.debug(f'{stderr.decode()}')


async def init_sound(hit=False, timeout: Optional[float] = None, debug=False):
    await _play_sound("yasakani.wav", timeout=timeout, debug=debug)


async def play_sound(hit=False, timeout: Optional[float] = None, debug=False):
    if hit:
        # atari
        await _play_sound("hit.wav", timeout=timeout, debug=debug)
    else:
        await _play_sound("miss.wav", timeout=timeout, debug=debug)
