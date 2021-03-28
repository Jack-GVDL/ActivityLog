from typing import *
import datetime
from LogEvent import *
from Util_Cmd import *


class CmdPack_Logger(CmdPack):

	default_file: str = "./Data/Schedule_2021.json"

	def __init__(self) -> None:
		super().__init__()

		# ----- data -----
		self._log_control: 		LogControl 	= LogControl()
		self._date_current: 	List[int] 	= [0, 0, 0]

		self._file_data:		FileData = FileData("Logger")

		self._cmd_add_event 	= CmdData_Hook("log_add", 		self.addEvent,		description="add event")
		self._cmd_rm_event 		= CmdData_Hook("log_rm",		self.rmEvent,		description="remove event")
		self._cmd_config_event 	= CmdData_Hook("log_config",	self.configEvent,	description="config event")
		self._cmd_config_date 	= CmdData_Hook("log_date",		self.configDate,	description="config date")
		self._cmd_load_file 	= CmdData_Hook("log_load", 		self.loadFile,		description="load file")
		self._cmd_dump_file 	= CmdData_Hook("log_dump", 		self.dumpFile,		description="dump file")
		self._cmd_list_table	= CmdData_Hook("log_ls",		self.listTable,		description="list table")

		self._config_date		= ConfigHandler_Date(	"Date", 		["date", 		"d"])
		self._config_time_start	= ConfigHandler_Time(	"TimeStart", 	["time_start", 	"ts"])
		self._config_time_end	= ConfigHandler_Time(	"TimeEnd", 		["time_end", 	"te"])
		self._config_index 		= ConfigHandler_Hook(	"Index", 		["index", 		"i"], 1, ConfigHandler_Hook.convertInt)
		self._config_tag 		= ConfigHandler_Hook(	"Tag", 			["tag", 		"t"], 1, ConfigHandler_Hook.convertString)
		self._config_file		= ConfigHandler_Hook(	"File",			["file",		"f"], 1, ConfigHandler_Hook.convertString)
		self._config_reset		= ConfigHandler_Setter(	"Reset",		["reset"])
		self._config_limit		= ConfigHandler_Hook(	"Limit",		["limit"],			  1, ConfigHandler_Hook.convertInt)

		self._resolver_add_event:		ConfigResolver = ConfigResolver()
		self._resolver_rm_event:		ConfigResolver = ConfigResolver()
		self._resolver_config_event:	ConfigResolver = ConfigResolver()
		self._resolver_config_date:		ConfigResolver = ConfigResolver()
		self._resolver_file:			ConfigResolver = ConfigResolver()
		self._resolver_list_table:		ConfigResolver = ConfigResolver()

		# ----- operation -----
		# add shared data into file
		self._file_data.write([self._log_control])

		# need to reset date
		self._date_current = self._getDate_Today_()

		# config resolver
		self._resolver_add_event.addConfig(self._config_date)
		self._resolver_add_event.addConfig(self._config_time_start)
		self._resolver_add_event.addConfig(self._config_time_end)
		self._resolver_add_event.addConfig(self._config_tag)
		self._resolver_rm_event.addConfig(self._config_date)
		self._resolver_rm_event.addConfig(self._config_index)
		self._resolver_config_event.addConfig(self._config_date)
		self._resolver_config_event.addConfig(self._config_index)
		self._resolver_config_event.addConfig(self._config_tag)
		self._resolver_config_event.addConfig(self._config_time_start)
		self._resolver_config_event.addConfig(self._config_time_end)
		self._resolver_config_date.addConfig(self._config_date)
		self._resolver_config_date.addConfig(self._config_reset)
		self._resolver_file.addConfig(self._config_file)
		self._resolver_list_table.addConfig(self._config_date)
		self._resolver_list_table.addConfig(self._config_limit)

		# manual
		self._cmd_add_event.func_manual 	= self._resolver_add_event.getManual
		self._cmd_rm_event.func_manual		= self._resolver_rm_event.getManual
		self._cmd_config_event.func_manual	= self._resolver_config_event.getManual
		self._cmd_config_date.func_manual	= self._resolver_config_date.getManual
		self._cmd_load_file.func_manual		= self._resolver_file.getManual
		self._cmd_dump_file.func_manual		= self._resolver_file.getManual
		self._cmd_list_table.func_manual	= self._resolver_list_table.getManual

		# cmd_list
		self._cmd_list.append(self._cmd_add_event)
		self._cmd_list.append(self._cmd_rm_event)
		self._cmd_list.append(self._cmd_config_event)
		self._cmd_list.append(self._cmd_config_date)
		self._cmd_list.append(self._cmd_load_file)
		self._cmd_list.append(self._cmd_dump_file)
		self._cmd_list.append(self._cmd_list_table)

		# file_list
		self._file_list.append(self._file_data)

	def __del__(self) -> None:
		return

	# Operation
	# command
	def addEvent(self, args: List[str], file_list: List[FileData], string_io: Control_StringContent) -> int:
		data: Dict = self._resolver_add_event.resolve(args)

		# variable
		date:		List[int] = [0, 0, 0]
		time_start:	List[int] = [0, 0]
		time_end:	List[int] = [0, 0]
		tag:		List[str] = []

		# ----- get data -----
		# date
		# date is not a must
		# if date is not specified, then it will be the preset date (self._data_current)
		if "Date" not in data.keys():
			date = self._date_current
		else:
			date = data["Date"]

		# time_start
		# time_start config is a must
		if "TimeStart" not in data.keys():
			return -1
		time_start = data["TimeStart"]

		# time_end
		# time_end config is not a must
		# if time_end is not specified, then it will be the same as time_start
		if "TimeEnd" not in data.keys():
			time_end = time_start
		else:
			time_end = data["TimeEnd"]
		
		# tag
		# tag config is a must
		if "Tag" not in data.keys():
			return -1
		tag = data["Tag"][0].split(" ")

		# ----- log event -----
		log_event = LogEvent(time_start, time_end, tag)
		if not self._log_control.addEvent(date, log_event):
			return -1

		# ----- output -----
		string_io.addContent(StringContent("event added\n", color_fore="green"))
		self._listEvent_(log_event, string_io)
		
		return 0

	def rmEvent(self, args: List[str], file_list: List[FileData], string_io: Control_StringContent) -> int:
		data: Dict = self._resolver_rm_event.resolve(args)

		# variable
		date:	List[int]	= [0, 0, 0]
		index:	int			= -1

		# ----- get data -----
		# date
		# date is not a must
		# if date is not specified, then it will be today
		if "Date" not in data.keys():
			date = self._getDate_Today_()
		else:
			date = data["Date"]

		# index
		# index is a must
		if "Index" not in data.keys():
			return -1
		index = data["Index"][0]

		# ----- log event -----
		if not self._log_control.rmEvent(date, index):
			return -1

		# ----- output -----
		string_io.addContent(StringContent("event removed", color_fore="green"))

		return 0

	def configEvent(self, args: List[str], file_list: List[FileData], string_io: Control_StringContent) -> int:
		data: Dict = self._resolver_config_event.resolve(args)

		# ----- get data -----
		date:		List[int] 	= [0, 0, 0]
		index:		int			= -1
		time_start:	List[int]	= None  # None: no need to modify
		time_end:	List[int]	= None  # None: no need to modify
		tag:		List[str]	= None  # None: no need to modify

		# date: not a must: it not specified, it will be today
		if "Date" not in data.keys():
			date = self._getDate_Today_()
		else:
			date = data["Date"]

		# index: must
		if "Index" not in data.keys():
			return -1
		index = data["Index"][0]

		# time_start: not a must
		if "TimeStart" in data.keys():
			time_start = data["TimeStart"]

		# time_end: not a must
		if "TimeEnd" in data.keys():
			time_end = data["TimeEnd"]

		# tag: not a must
		if "Tag" in data.keys():
			tag = data["Tag"][0].split(" ")

		# ----- get log_event -----
		log_event: LogEvent = self._log_control.getEvent(date, index)
		if log_event is None:
			return -1

		# ----- config log_event -----
		if time_start is not None:
			log_event.start(time_start)
		if time_end is not None:
			log_event.end(time_end)
		if tag is not None:
			log_event.tag = tag

		# ----- output -----
		string_io.addContent(StringContent("event configured\n", color_fore="green"))
		self._listEvent_(log_event, string_io)

		return 0

	def configDate(self, args: List[str], file_list: List[FileData], string_io: Control_StringContent) -> int:
		data: Dict = self._resolver_config_date.resolve(args)

		# if "Date" is specified, then set the date
		# if "Reset" is specified, then reset the date (set the date to today)
		# then finally, for all option, print the date set
		#
		# "Reset" has the highest priority
		if "Reset" in data.keys():
			self._date_current = self._getDate_Today_()
		elif "Date" in data.keys():
			self._date_current = data["Date"]

		# print date
		date = self._date_current
		content = f"{date[0]}-{date[1]}-{date[2]}"
		string_io.addContent(StringContent(content))

		return 0

	def loadFile(self, args: List[str], file_list: List[FileData], string_io: Control_StringContent) -> int:
		data: Dict = self._resolver_file.resolve(args)

		# get the file path that needed to load
		if "File" in data.keys():
			self._log_control.file = data["File"][0]
		else:
			self._log_control.file = self.default_file

		# actual loading
		self._log_control.load()

		# output
		string_io.addContent(StringContent("file loaded", color_fore="green"))

		return 0

	def dumpFile(self, args: List[str], file_list: List[FileData], string_io: Control_StringContent) -> int:
		data: Dict = self._resolver_file.resolve(args)

		# get the file path that needed to load
		if "File" in data.keys():
			self._log_control.file = data["File"][0]
		else:
			self._log_control.file = self.default_file

		# actual loading
		self._log_control.dump()

		# output
		string_io.addContent(StringContent("file dumped", color_fore="green"))

		return 0

	def listTable(self, args: List[str], file_list: List[FileData], string_io: Control_StringContent) -> int:
		data: Dict = self._resolver_list_table.resolve(args)

		# variable
		limit: int = -1

		# get display limit
		# if limit is inside data, then display limited amount of event with size==limit
		# else display all event
		if "Limit" in data.keys():
			limit = data["Limit"][0]

		# ----- get date_list -----
		date_list: List[LogDate] = []

		# date is not a must
		# if date is not specified, then show all date
		if "Date" in data.keys():
			date:		List[int] 	= data["Date"]
			log_date:	LogDate		= self._log_control.getDate(date)

			if log_date is not None:
				date_list.append(log_date)

		else:
			date_list = self._log_control.date_list.copy()

		# ----- cut date_list -----
		# cut the list FROM BACK
		if limit >= 0:
			size_display = min(len(date_list), limit)
			date_list = date_list[-size_display:]

		# ----- print -----
		# print the date and event
		for index, log_date in enumerate(date_list):
			self._listDate_(log_date, string_io)

			# the first newline is newline for new date
			# the second newline is for separating different date with one empty line
			if index != len(date_list) - 1:
				string_io.addContent(StringContent("\n\n"))

		return 0

	# Protected
	def _getDate_Today_(self) -> List[int]:
		today = datetime.date.today()
		return [today.year, today.month, today.day]

	def _listDate_(self, log_date: LogDate, string_io: Control_StringContent) -> str:
		content: 	str = ""
		duration:	int = 0

		# print date
		content 	= ""
		content 	+= f"{log_date.date[0]}-{log_date.date[1]}-{log_date.date[2]}\n"
		string_io 	+= StringContent(content, color_fore="magenta")

		# foreach event
		for index_event, event in enumerate(log_date.event_list):

			# index
			content = ""
			content += f"[{index_event}] "
			string_io += StringContent(content, color_fore="magenta")

			# event itself
			self._listEvent_(event, string_io)

			# duration
			duration += event.duration

			# if there will be new event in the next line
			# create a newline
			# else, don't creat a newline
			if index_event != len(log_date.event_list) - 1:
				# content += '\n'
				string_io += "\n"

		# duration
		content 	= ""
		content 	+= '\n'
		content 	+= f"Duration: {duration} ({(duration / 60):.2f} hr)"
		string_io 	+= StringContent(content, color_fore="magenta")

	def _listEvent_(self, event: LogEvent, string_io: Control_StringContent) -> None:
		# time_start, time_end
		content = ""
		content += f"{event.time_start[0]:02d}:{event.time_start[1]:02d}; "
		content += f"{event.time_end[0]:02d}:{event.time_end[1]:02d}; "

		if event.time_start == event.time_end:
			string_io += StringContent(content, color_fore="red")
		else:
			string_io += StringContent(content, color_fore="yellow")

		# tag
		content = ""
		for index_tag, tag in enumerate(event.tag):
			if index_tag != 0:
				content += ', '
			content += tag

		string_io += StringContent(content, color_fore="blue")
