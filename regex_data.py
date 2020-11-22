import dataclasses
import re

@dataclasses.dataclass(frozen=True)
class LogRegex:
    server_start = re.compile(r"\[\d+:\d+:\d+\] \[Server thread/INFO\]: Done \((.*)\)! For help, type \"help\"")
    server_stop = re.compile(r"\[\d+:\d+:\d+\] \[Server thread/INFO\]: Stopping server")
    player_join = re.compile(r"\[\d+:\d+:\d+\] \[Server thread/INFO\]: ([0-9a-zA-Z_]{3,16})\[.+\] logged in with entity id.*")
    player_leave = re.compile(r"\[\d+:\d+:\d+\] \[Server thread/INFO\]: ([0-9a-zA-Z_]{3,16}) left the game")
    on_chat = re.compile(r"\[\d+:\d+:\d+\] \[(?:Server thread|Async Chat Thread - #\d+)/INFO\]: <([0-9a-zA-Z_]{3,16})> (.*)")
    on_tell = re.compile(r"\[\d+:\d+:\d+\] \[Server thread/INFO\]: You whisper to [0-9a-zA-Z_]{3,16}: (.*)")
    ignore = re.compile(r"\[\d+:\d+:\d+\] \[Server thread/WARN\]: Entity (EntityAreaEffectCloud|apz)\['Area Effect Cloud(.*)\] left loaded chunk area")
