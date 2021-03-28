from typing import *
from LogEvent import *
from Util_Cmd import *
from CmdPack import *
	
	
# data
cmd_control_ 		= CmdControl()
package_util_		= CmdPack_Util()
package_logger_ 	= CmdPack_Logger()
package_statistic_	= CmdPack_Statistic()

# config
package_util_.load(cmd_control_)
package_logger_.load(cmd_control_)
package_statistic_.load(cmd_control_)

# pre-execution batched command
# cmd_control_.input_buffer.append("log_load")
# cmd_control_.input_buffer.append("pipe Logger Statistic")
# cmd_control_.input_buffer.append("stat_create")

# operation
cmd_control_.loop()
