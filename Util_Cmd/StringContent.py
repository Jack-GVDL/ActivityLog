from typing import *


class StringContent:

	def __init__(self, content: str, color_fore: str = None, color_back: str = None) -> None:
		super().__init__()

		# data
		self.content:		str = ""
		self.color_fore:	str = None
		self.color_back:	str = None

		# operation
		self.content	= content
		self.color_fore	= color_fore
		self.color_back	= color_back

	def __del__(self) -> None:
		return

	# Operation
	# ...


class Control_StringContent:

	def __init__(self) -> None:
		super().__init__()

		# data
		self.content_list:	List[StringContent]				= []
		self.func_output:	Callable[[StringContent], None]	= []

		# operation
		# ...

	def __del__(self) -> None:
		return

	# Operation
	def addContent(self, content: StringContent) -> bool:
		self.content_list.append(content)
		return True

	def addString(self, string: str) -> bool:
		self.content_list.append(StringContent(string))
		return True

	# TODO: not yet completed
	def rmContent(self, content: StringContent) -> bool:
		return False

	def output(self) -> bool:
		if self.func_output is None:
			return False

		# output all content (one-by-one)
		for content in self.content_list:
			self.func_output(content)

		# output will clear the output buffer (content_list)
		self.content_list.clear()
		
		return True

	# Operator Overloading
	def __iadd__(self, other):
		# check type
		if type(other) == Control_StringContent:
			self.content_list.extend(other.content_list)
		elif type(other) == StringContent:
			self.addContent(other)
		elif type(other) == str:
			self.addString(other)

		return self
