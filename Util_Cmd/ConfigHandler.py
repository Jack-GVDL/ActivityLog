from typing import *
from .CmdControl import ConfigHandler


class ConfigHandler_Hook(ConfigHandler):

	@classmethod
	def convertInt(cls, dst: List[Any], content_list: List[str]) -> bool:
		result_list: List[int] = []

		try:
			for content in content_list:
				temp: int = int(content)
				result_list.append(temp)
		except Exception:
			return False

		dst.extend(result_list)
		return True

	@classmethod
	def convertFloat(cls, dst: List[Any], content_list: List[str]) -> bool:
		result_list: List[float] = []

		try:
			for content in content_list:
				temp: float = float(content)
				result_list.append(temp)
		except Exception:
			return False

		dst.extend(result_list)
		return True

	@classmethod
	def convertString(cls, dst: List[Any], content_list: List[str]) -> bool:
		dst.extend(content_list)
		return True

	def __init__(
			self,
			name: 			str,
			alias: 			List[str],
			size_parameter: int,
			func_convert:	Callable[[List[Any], List[str]], bool]):

		super().__init__(name, alias, size_parameter)

		# data
		self.func_convert: Callable[[List[Any], List[str]], bool] = None

		# operation
		self.func_convert = func_convert

	def __del__(self):
		return

	# Operation
	def convert(self, dst: List[Any], content_list: List[str]) -> bool:
		return self.func_convert(dst, content_list)


class ConfigHandler_Setter(ConfigHandler):

	def __init__(self, name: str, alias: List[str]):
		super().__init__(name, alias, 0)

		# data
		# ...

		# operation
		# ...

	def __del__(self):
		return

	# Operation
	def convert(self, dst: List[Any], content_list: List[str]) -> bool:
		return True


class ConfigHandler_Date(ConfigHandler):

	def __init__(self, name: str, alias: List[str]):
		super().__init__(name, alias, 1)

		# data
		# ...

		# operation
		# ...

	def __del__(self):
		return

	# Operation
	def convert(self, dst: List[Any], content_list: List[str]) -> bool:
		content: str = content_list[0]

		# content string should be in format of YYYY-(M)M-(D)D
		# where the character inside () is optional
		content_list: List[str] = content.split("-")
		if len(content_list) < 3:
			return False

		date: List[int] = [0, 0, 0]

		# if the content in content_list is invalid
		# e.g. abcd-df-12
		# the conversion from string to int may not be success
		try:
			date[0] = int(content_list[0])
			date[1] = int(content_list[1])
			date[2] = int(content_list[2])
		except Exception:
			return False

		# TODO: the checking is not completed
		#  especially for the day part
		if date[1] < 1 or date[1] > 12:
			return False
		if date[2] < 1 or date[2] > 31:
			return False

		# return result
		dst.extend(date)

		return True


class ConfigHandler_Time(ConfigHandler):

	def __init__(self, name: str, alias: List[str]):
		super().__init__(name, alias, 1)
		
		# data
		# ...
		
		# operation
		# ...
		
	def __del__(self):
		return
		
	# Operation
	def convert(self, dst: List[Any], content_list: List[str]) -> bool:
		content: str = content_list[0]

		# content_string should be in format of HH:MM
		content_list: List[str] = content.split(":")

		if len(content_list) < 2:
			return False

		# get time value
		time: List[int] = [0, 0]

		try:
			time[0] = int(content_list[0])
			time[1] = int(content_list[1])
		except Exception:
			return False

		# check if time is valid or not
		# +6 is due to the fact that there is some work that needed to work overnight
		if time[0] < 0 or time[0] >= 24 + 6:
			return False
		if time[1] < 0 or time[1] >= 60:
			return False

		# return result
		dst.extend(time)

		return True
