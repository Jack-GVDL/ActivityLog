from typing import *
import datetime
from Util_Cmd import *


class CmdData_Pipe(CmdData):

	def __init__(self):
		super().__init__("pipe", description="pipeline data")

		# data
		# ...

		# operation
		# ...

	def __del__(self):
		return

	# Operation
	def execute(self, args: List[str], file_list: List[FileData], string_io: Control_StringContent) -> int:
		# check
		if len(args) < 3:
			return -1

		# config
		file_src: FileData = self._findFile_(args[1], file_list)
		file_dst: FileData = self._findFile_(args[2], file_list)

		if file_src is None:
			return -1
		if file_dst is None:
			return -1

		# actual pipe
		data_list: List[Any] = []
		if not file_src.read(data_list):
			return -1
		if not file_dst.write(data_list):
			return -1

		# log
		string_io += f"{file_src.name} > {file_dst.name}"

		# ret
		return 0

	# Protected
	def _findFile_(self, filename: str, file_list: List[FileData]) -> FileData:
		for file in file_list:
			if filename != file.name:
				continue
			return file
		return None


class CmdData_ListFile(CmdData):

	def __init__(self):
		super().__init__("ls", "list file")

		# data
		# ...

		# operation
		# ...

	def __del__(self):
		return

	# Operation
	def execute(self, args: List[str], file_list: List[FileData], string_io: Control_StringContent) -> int:
		content: str = ""
		for index, file in enumerate(file_list):

			content += file.name
			if index != len(file_list) - 1:
				content += '\n'

		# add to io (stdout)
		string_io += content

		# ret
		return 0

	# Protected
	# ...


class CmdPack_Util(CmdPack):

	def __init__(self):
		super().__init__()

		# data
		self._cmd_list:		List[CmdData] 	= []
		self._file_list:	List[FileData]	= []

		self._cmd_pipe:	CmdData = CmdData_Pipe()
		self._cmd_ls:	CmdData = CmdData_ListFile()

		# operation
		self._cmd_list.append(self._cmd_pipe)
		self._cmd_list.append(self._cmd_ls)

	def __del__(self):
		return

	# Operation
	# ...
