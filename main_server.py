from shutil import copyfile
from Network.Server_LogEvent import data_control_log, data_control_todo, app


# Data
file_production:	str	= "./Data/Schedule_2021_Server.json"
file_testing:		str	= "./Data/Schedule_2021_Test.json"

file_todo_production:	str = "./Data/Schedule_2021_Todo_Server.json"
file_todo_testing:		str = "./Data/Schedule_2021_Todo_Test.json"

# copy data from production to testing environment
# copyfile(file_production, file_testing)  # (src, dst)

# control log
data_control_log[0].file = file_production
# data_control_log[0].file = file_testing
data_control_log[0].load()

data_control_todo[0].file = file_todo_production
# data_control_todo[0].file = file_todo_testing
data_control_todo[0].load()


# Operation
app.run()
