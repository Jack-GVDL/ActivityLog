from typing import *
import os
# from termcolor import colored
# import colorama
from printy import printy
from .StringContent import StringContent, Control_StringContent


class _PrintyColorTable_:

	# data
	# List[Tuple[flag, color_name]]
	color: List[Tuple[str, str]] = [
		("k", 	"black"),
		("g",	"grey"),
		("w",	"white"),
		("r",	"red"),
		("n",	"green"),
		("y",	"yellow"),
		("c",	"blue"),  # redirect to cyan
		("m>",	"magenta"),
		("c",	"cyan"),
		("o",	"orange"),
		("<p",	"purple")
	]

	# operation
	@classmethod
	def getFlag_Color(cls, color: str) -> str:
		result: List[Tuple[str, str]] = list(filter(lambda x: x[1] == color, cls.color))
		if not result:
			return None
		return result[0][0]


class FileData:
	
	def __init__(self, name: str):
		super().__init__()

		# data
		self.name:			str			= ""
		self._data: 		List[Any] 	= []
		self._is_buffer: 	bool		= False

		# operation
		self.name = name

	def __del__(self) -> None:
		return

	# Operation
	def write(self, data_list: List[Any]) -> bool:
		if not self._is_buffer:
			self._data.clear()

		for data in data_list:
			self._data.append(data)

		return True

	def read(self, data_list: List[Any]) -> bool:
		for data in self._data:
			data_list.append(data)

		if self._is_buffer:
			data_list.clear()

		return True


class CmdData:

	def __init__(self, name: str, description: str = ""):
		super().__init__()

		# data
		self.name: 			str = ""
		self.description:	str = ""

		# operation
		self.name 			= name
		self.description 	= description

	def __del__(self):
		return

	# Operation
	# input: args
	# output: string_content
	# TODO: may move string_io into file_list
	def execute(self, args: List[str], file_list: List[FileData], string_io: Control_StringContent) -> int:
		raise NotImplementedError

	def getManual(self, string_io: Control_StringContent) -> int:
		return 0
	

class CmdData_Hook(CmdData):

	def __init__(
			self,
			name:			str,
			func_execute: 	Callable[[List[str], List[FileData], Control_StringContent],	int],
			func_manual:	Callable[[Control_StringContent], 								int] = None,
			description:	str 						= ""):
	
		super().__init__(name, description=description)
		
		# data
		self.func_execute: 	Callable[[List[str], List[FileData], Control_StringContent], 	int] = None
		self.func_manual:	Callable[[Control_StringContent],								int] = None
		
		# operation
		self.func_execute 	= func_execute
		self.func_manual	= func_manual
		
	def __del__(self):
		return
		
	# Operation
	def execute(self, args: List[str], file_list: List[FileData], string_io: Control_StringContent) -> int:
		if self.func_execute is None:
			return -1
		return self.func_execute(args, file_list, string_io)

	def getManual(self, string_io: Control_StringContent) -> int:
		if self.func_manual is None:
			return -1
		return self.func_manual(string_io)


# TODO: need to change name? shell?
class CmdControl:

	def __init__(self) -> None:
		super().__init__()
		
		# data
		self._cmd_list:		List[CmdData] 			= []
		self._file_list:	List[FileData]			= []
		self._string_io:	Control_StringContent 	= Control_StringContent()

		self._input_buffer:	List[str]				= []

		# operation
		self._string_io.func_output = self._outputScreen_

		# backup
		# to make the color text available on NT
		# need to use colorama
		#
		# reference
		# - https://stackoverflow.com/questions/21858567/why-does-termcolor-output-control-characters
		# -instead-of-colored-text-in-the-wind colorama.init(autoreset = True)

	def __del__(self) -> None:
		return

	# Property
	@property
	def input_buffer(self) -> List[str]:
		return self._input_buffer

	# Operation
	def loop(self) -> None:
		while True:

			# for each input buffer, execute
			input_buffer: List[str] = self._input_buffer.copy()
			self._input_buffer.clear()

			for input_ in input_buffer:
				result: bool = self._execute_(input_)

				# clear output buffer
				# newline is added before output to separate the command before and after
				self._string_io += "\n"
				self._string_io.output()

				# check if exit the loop
				if result is False:
					return

			# get console input
			self._input_()

	def addCmd(self, cmd: CmdData) -> bool:
		temp: CmdData = self._findCommand_(cmd.name)
		if temp is not None:
			return False

		self._cmd_list.append(cmd)
		return True

	def rmCmd(self, cmd: CmdData) -> bool:
		try:
			index: int = self._cmd_list.index(cmd)
		except ValueError:
			return False

		self._cmd_list.pop(index)
		return True

	def addFile(self, file: FileData) -> bool:
		temp: FileData = self._findFile_(file.name)
		if temp is not None:
			return False
		
		self._file_list.append(file)
		return True

	def rmFile(self, file: FileData) -> bool:
		try:
			index: int = self._file_list.index(file)
		except ValueError:
			return False

		self._file_list.pop(index)
		return True

	# Protected
	def _input_(self) -> None:
		# prefix
		self._string_io.addContent(StringContent("> "))
		self._string_io.output()

		# get input
		data: str = input()

		# add to buffer
		self._input_buffer.append(data)

	def _execute_(self, input_: str) -> bool:
		# get input
		data: str = input_

		# ----- get data -----
		# first slice the data into data_list
		# the first item in the data_list is the
		#
		# if the list is empty
		# then it will do nothing (and will not output any error)
		data_list: List[str] = data.split(" ")
		if not data_list:
			return True

		# ----- default command -----
		# check if exit the loop or not
		# return False means the looping is foreced to be ended
		# exit
		if data_list[0] == "exit":
			return False

		# help: list available command
		if data_list[0] == "help":
			self._listCommand_(self._string_io)
			self._string_io.addContent(StringContent("\n"))
			return True

		# man: print the manual of the target command
		if data_list[0] == "man":
			cmd: CmdData = self._findCommand_(data_list[1])
			if cmd is None:
				self._string_io.addContent(StringContent("man: target command not found\n", color_fore="red"))
				return True
			
			self._manualCommand_(cmd, self._string_io)
			self._string_io.addContent(StringContent("\n"))
			return True

		if data_list[0] == "cls" or data_list[0] == "clear":
			self._clearScreen_()
			return True

		# ----- user defined command -----
		# find the target command
		# if not found, show not found error / warning message
		cmd: CmdData = self._findCommand_(data_list[0])
		if cmd is None:
			self._string_io.addContent(StringContent("command not found\n", color_fore="red"))
			return True
		
		# execute
		ret: int = cmd.execute(data_list, self._file_list.copy(), self._string_io)
		
		# add a newline if there is content output from the executable
		if self._string_io.content_list:
			self._string_io.addContent(StringContent("\n"))

		# show error
		if ret != 0:
			self._string_io.addContent(StringContent(f"error; code: {ret}\n", color_fore="red"))

		return True

	def _findCommand_(self, command: str) -> CmdData:
		for cmd in self._cmd_list:
			if command != cmd.name:
				continue
			return cmd
		return None

	def _findFile_(self, f: str) -> FileData:
		for file in self._file_list:
			if f != file.name:
				continue
			return file
		return None

	def _listCommand_(self, string_io: Control_StringContent) -> None:
		content: str = ""
		for index, cmd in enumerate(self._cmd_list):

			content += cmd.name
			content += ': '
			content += cmd.description

			if index != len(self._cmd_list) - 1:
				content += '\n'

		string_io.addContent(StringContent(content))

	def _manualCommand_(self, cmd: CmdData, string_io: Control_StringContent) -> None:
		content: str = ""

		content += "Name:\n"
		content += cmd.name
		content += "\n\n"

		content += "Description:\n"
		content += cmd.description
		content += "\n\n"

		content += "Detail:\n"
		string_io.addContent(StringContent(content))

		cmd.getManual(string_io)

	def _clearScreen_(self) -> None:
		if os.name == "nt":
			os.system("cls")
		else:
			os.system("clear")

	def _outputScreen_(self, content: StringContent) -> None:
		# termcolor
		# if content.color_fore is None:
		# 	print(content.content, end=' ')
		# else:
		# 	print(colored(content.content, content.color_fore), end=' ')

		# printy
		# get flag
		color_fore: str = None

		if content.color_fore is not None:
			color_fore = _PrintyColorTable_.getFlag_Color(content.color_fore)
		
		# print content (default)
		if content.color_fore is None:
			print(content.content, end='')
			return
		
		# special handling of "[" and "]"
		# replace "[" and "]" with "\[" and "\]" respectively
		# string: str = content.content
		# if '[' in string or ']' in string:
			
		string = ""
		for s in content.content:
			if s == '[':
				string += '\['
			elif s == ']':
				string += '\]'
			else:
				string += s
		
		# print content (color)
		printy(string, color_fore, end='')


class CmdPack:

	def __init__(self):
		super().__init__()

		# data
		self._cmd_list:		List[CmdData]	= []
		self._file_list:	List[FileData]	= []

		# operation
		# ...

	def __del__(self):
		return

	# Operation
	# load, dump
	def load(self, cmd_control: CmdControl) -> bool:
		if cmd_control is None:
			return False

		# command
		for cmd in self._cmd_list:
			cmd_control.addCmd(cmd)

		# file
		for file in self._file_list:
			cmd_control.addFile(file)

		return True

	def dump(self, cmd_control: CmdControl) -> bool:
		if cmd_control is None:
			return False

		# command
		for cmd in self._cmd_list:
			cmd_control.rmCmd(cmd)

		# file
		for file in self._file_list:
			cmd_control.rmFile(file)

		return True

	# Protected
	# ...


class ConfigHandler:

	def __init__(self, name: str, alias: List[str], size_parameter: int):
		super().__init__()

		# data
		self.name:				str 		= ""
		self.alias:				List[str]	= []
		self.size_parameter:	int 		= 0

		# operation
		# TODO: may need to perform uniqueness check on alias
		self.name 			= name
		self.alias			= alias
		self.size_parameter	= size_parameter

	def __del__(self):
		return

	# Operation
	def match(self, alias: str) -> bool:
		for item in self.alias:
			if alias != item:
				continue
			return True
		return False

	def convert(self, dst: List[Any], content_list: List[str]) -> bool:
		raise NotImplementedError


class ConfigResolver:

	def __init__(self) -> None:
		super().__init__()
		
		# data
		self._config_list: List[ConfigHandler] = []

		# operation
		# ...

	def __del__(self) -> None:
		return

	# Operation
	def addConfig(self, config: ConfigHandler) -> bool:
		self._config_list.append(config)
		return True

	def rmConfig(self, config: ConfigHandler) -> bool:
		try:
			index: int = self._config_list.index(config)
		except ValueError:
			return False

		self._config_list.pop(index)
		return True
	
	def resolve(self, data_list: List[str]) -> Dict:
		result: Dict 	= {}
		next_:	int		= -1

		# data_list preprocessing
		data_list = self._mergeString_(data_list)

		# create the default key
		result[""] = []
		
		# assume: the command name is removed from the first position
		for index, item in enumerate(data_list):

			# check if needed to skip some data in data_list
			if index < next_:
				continue
			
			# ----- empty -----
			# remark
			# this operation is already done in _mergeString_
			#
			# check if the string is empty or not
			# if empty, then ignore it
			# if not item:
			# 	continue

			# ----- regular data -----
			# check if the string started with '-' or not
			if item[0] != '-':
				result[""].append(item)
				continue

			# ----- config prefix "-" -----
			# check if this configuration existed in argument list or not
			config: ConfigHandler = self._findConfig_(item[1:])

			# if not exist, then put this into default key
			if config is None:
				result[""].append(item)
				continue

			# ----- config data -----
			# add data to content_list
			# then content will be converted (in ConfigHandler.convert) to the final result
			content_list: List[str] = []

			# put the parameter into the content_list
			# parameter_end: index of last parameter item + 1
			parameter_end: int = index + config.size_parameter + 1
			for i in range(index + 1, min(parameter_end, len(data_list))):
				content_list.append(data_list[i])

			# convert content_list to data_list
			data: List[Any] = []
			if not config.convert(data, content_list):
				continue

			# create new key and put data (list of data) as value
			result[config.name] = data

			# set next
			next_ = parameter_end

		return result

	def getManual(self, string_io: Control_StringContent) -> int:
		# first get max length of config.name
		max_length: int = 0
		for config in self._config_list:
			max_length = max(max_length, len(config.name))

		# make content
		content: str = ""
		for index_config, config in enumerate(self._config_list):

			# name
			content = ""
			content += config.name
			content += ' ' * (max_length - len(config.name) + 4)  # at least 4 space between name and alias
			string_io += content

			# alias
			for index_alias, alias in enumerate(config.alias):

				string_io += "-"
				string_io += StringContent(alias, color_fore="green")

				if index_alias != len(config.alias) - 1:
					string_io += ","

			if index_config != len(self._config_list) - 1:
				string_io += "\n"

		return 0

	# Protected
	def _findConfig_(self, alias: str) -> ConfigHandler:
		for config in self._config_list:
			if not config.match(alias):
				continue
			return config
		return None

	def _mergeString_(self, data_list: List[str]) -> List[str]:
		is_started: 	bool 		= False
		content:		str			= ""
		result:			List[str]	= []
		
		# foreach data
		for data in data_list:
			
			# ignore empty string
			# but normally empty string should not occur
			if data == "":
				continue

			# ----- not in string -----
			if not is_started:

				# start of string
				if data[0] == '\"':

					# check if special condition "Example"
					# i.e. string that have both starting and ending "
					if data[-1] == '\"':
						result.append(data[1:-1])
					else:
						is_started = True
						content = data[1:]  # remove "

				# normal data that not inside string
				else:
					result.append(data)
				
				continue

			# ----- in string -----
			# end of string
			if data[-1] == '\"':
				is_started = False
				content += ' '
				content += data[:-1]
				result.append(content)

			# normal data that inside string
			else:
				content += ' '
				content += data

		return result
