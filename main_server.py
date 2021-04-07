from typing import *
import json
from Network.Server_LogEvent import Server_main
from LogEvent.LogEvent import LogControl
from LogEvent.LogTodo import Control_LogTodo


# Data
# ...


# Function
def main() -> None:
    # ----- config -----
    # read config
    with open("./Config_Server.json", "r") as f:
        data = json.load(f)

    # get path
    path_log  = data["Path_Log"]
    path_todo = data["Path_Todo"]

    # ----- control -----
    # create data_log
    control_log     = LogControl()
    control_todo    = Control_LogTodo()

    # try to read data from json
    control_log.file  = path_log
    control_todo.file = path_todo

    control_log.load()
    control_todo.load()

    # ----- server -----
    # start server
    Server_main(
        control_log,
        control_todo
    )


# Operation
if __name__ != "__main__":
	raise RuntimeError


main()
