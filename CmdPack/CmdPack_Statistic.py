from typing import *
import os
import datetime
import calendar
import matplotlib.pyplot as plt
from LogEvent import *
from Util_Cmd import *


class CmdPack_Statistic(CmdPack):

	default_folder: str = "./Report"

	def __init__(self):
		super().__init__()

		# ----- data -----
		# data
		self._folder_save:	str = self.default_folder

		# file
		self._file_data		= FileData("Statistic")

		# cmd
		self._cmd_create	= CmdData_Hook("stat_create", 	self._createGraph_, description="create graph")
		self._cmd_folder	= CmdData_Hook("stat_folder",	self._setFolder_,	description="set save folder")

		# config
		self._config_folder = ConfigHandler_Hook("Folder", ["folder"], 1, ConfigHandler_Hook.convertString)

		# resolver
		self._resolver_create	= ConfigResolver()
		self._resolver_folder	= ConfigResolver()

		# ----- operation -----
		# cmd_list
		self._cmd_list.append(self._cmd_create)
		self._cmd_list.append(self._cmd_folder)

		# file_list
		self._file_list.append(self._file_data)

		# resolver
		self._resolver_create.addConfig(self._config_folder)
		self._resolver_folder.addConfig(self._config_folder)

	def __del__(self):
		return

	# Operation
	# ...

	# Protected
	def _createGraph_(self, args: List[str], file_list: List[FileData], string_io: Control_StringContent) -> int:
		# ----- get data -----
		data: Dict = self._resolver_create.resolve(args)

		# folder: not must
		folder: str = self._folder_save
		if self._config_folder.name in data:
			folder = data[self._config_folder.name]

		# check if folder exist or not
		if not os.path.isdir(folder):
			string_io += StringContent("folder path does not exist", "red")
			return -1

		# get LogControl
		data: List[Any] = []
		self._file_data.read(data)
		if not data:
			string_io += StringContent("LogControl is not inside file", "red")
			return -1

		log_control: LogControl = data[0]

		# ----- create graph -----
		self._createGraph_Monthly_Duration_(log_control, folder, string_io)

		return 0

	def _setFolder_(self, args: List[str], file_list: List[FileData], string_io: Control_StringContent) -> int:
		# ----- get data -----
		data: Dict = self._resolver_folder.resolve(args)

		# folder: must
		folder: str = ""
		if self._config_folder.name not in data:
			return -1

		# ----- set folder -----
		self._folder_save = folder

		# ----- log -----
		string_io += StringContent(f"{self._folder_save}", "green")
		return 0

	def _createGraph_Monthly_Duration_(self, control: LogControl, folder_path: str, string_io: Control_StringContent) -> None:
		# ----- compute duration of each day -----
		# TODO: currently this is fixed
		# get month
		today		= datetime.date.today()
		year:	int	= today.year
		month:	int	= today.month

		# get number of day in this month
		# https://stackoverflow.com/questions/4938429/how-do-we-determine-the-number-of-days-for-a-given-month-in-python
		size_day: int = calendar.monthrange(year, month)[1]

		# get LogDate of this month
		# assumed: control.data_list is sorted based on date [YYYY, MM, DD]
		log_date_list: List[LogDate] = [None for _ in range(size_day)]

		is_this_month: bool = False
		for log_date in control.date_list:

			if log_date.date[0] == year and log_date.date[1] == month:
				log_date_list[log_date.date[2]] = log_date
				is_this_month = True
				continue

			# month is passed
			if is_this_month:
				return

		# compute duration
		duration_list: 	List[int]	= []
		date_list:		List[str]	= []

		for day, log_date in enumerate(log_date_list):

			# add date
			date_list.append(f"{year}-{month}-{day}")

			# add duration
			if log_date is None:
				duration_list.append(0)
				continue

			duration: int = 0
			for log_event in log_date.event_list:
				duration += log_event.duration
			duration_list.append(duration)

		# ----- plot graph -----
		# https://matplotlib.org/tutorials/introductory/pyplot.html
		plt.plot(duration_list)
		plt.ylabel("Duration")
		plt.xlabel("Date")

		plt.savefig(os.path.join(folder_path, "Monthly_Duration"), bbox_inches="tight")
		plt.clf()

		# ----- log -----
		string_io += StringContent("created: Monthly_Duration")
