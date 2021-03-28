import enum
from typing import *
import json
from enum import IntEnum, auto
from .Interface_DictData import Interface_DictData


# Data Structure
class LogSubTask(Interface_DictData):

	# Enum
	class Label(IntEnum):
		ID		= 0
		NAME	= 1
		IS_DONE	= 2

	# Static Data
	label = Label

	def __init__(
		self,
		id_:			int,
		name:			str,
		is_done:		bool) -> None:
		super().__init__()

		# data
		self.id_:		int		= id_
		self.name:		str 	= name
		self.is_done:	bool 	= is_done

		# operation
		# ...

	def __del__(self) -> None:
		return

	# Property
	# ...

	# Operation
	# ...

	# Interface
	def getDictData(self) -> Dict:
		return {
			self.label.ID.value:		self.id_,
			self.label.NAME.value:		self.name,
			self.label.IS_DONE.value:	self.is_done
		}

	def setDictData(self, data: Dict) -> None:
		self.id_		= data[str(self.label.ID.value)]
		self.name		= data[str(self.label.NAME.value)]
		self.is_done	= data[str(self.label.IS_DONE.value)]

	# Protected
	# ...


class LogTodo(Interface_DictData):

	# Enum
	class Label(IntEnum):
		ID		= 0
		NAME	= 1
		SUBTASK	= 2
		NOTE	= 3

	# Static Data
	label = Label

	def __init__(
		self,
		id_:			int,
		name:       	str,
		note:       	str) -> None:
		super().__init__()

		# data
		self.id_:			int					= id_
		self.name:			str 				= name
		self.subtask_list:	List[LogSubTask]	= []
		self.note:			str					= note

		# operation
		# ...

	def __del__(self) -> None:
		return

	# Property
	# ...

	# Operation
	# ...

	# Interface
	def getDictData(self) -> Dict:
		# compute subtask list
		dict_subtask = []
		for subtask in self.subtask_list:
			dict_subtask.append(subtask.getDictData())

		return {
			self.label.ID.value:		self.id_,
			self.label.NAME.value:		self.name,
			self.label.SUBTASK.value:	dict_subtask,
			self.label.NOTE.value:		self.note
		}

	def setDictData(self, data: Dict) -> None:
		self.id_	= data[str(self.label.ID.value)]
		self.name	= data[str(self.label.NAME.value)]
		self.note	= data[str(self.label.NOTE.value)]

		# compute subtask list
		self.subtask_list.clear()

		dict_subtask = data[str(self.label.SUBTASK.value)]
		for subtask in dict_subtask:

			task = LogSubTask(-1, None, None)
			task.setDictData(subtask)
			self.subtask_list.append(task)

	# Protected
	# ...


class Control_LogTodo:

	class Label:
		DATA_LIST: 		int = 0
		INDEX_TODO: 	int = 1
		INDEX_SUBTASK:	int = 2

	def __init__(self) -> None:
		super().__init__()

		# data
		self.file:		str = ""
		self.todo_list:	List[LogTodo] = []

		self.index_todo:	int = 0
		self.index_subtask: int = 0

		# operation
		# ...

	def __del__(self) -> None:
		return

	# Property
	# ...

	# Operation
	# name is used as the identifier
	def addLog_Todo(self, name: str, note: str) -> bool:
		# get id
		id_: int = self.index_todo
		self.index_todo += 1

		# create and add todo
		log_todo = LogTodo(id_, name, note)
		self.todo_list.append(log_todo)
		return True

	def rmLog_Todo(self, id_: int) -> bool:
		index: int = self._getIndex_Todo_ID_(id_)
		if index < 0:
			return False

		self.todo_list.pop(index)
		return True

	# name is used as the id of of the LogTodo
	def addLog_SubTask(self, id_todo: int, subtask_name: str, subtask_done: bool) -> bool:
		# check if target LogTodo existed or not
		log_todo = self._getLog_Todo_ID_(id_todo)
		if log_todo is None:
			return False

		# get id
		id_: int = self.index_subtask
		self.index_subtask += 1

		# create and add subtask
		log_subtask = LogSubTask(id_, subtask_name, subtask_done)
		log_todo.subtask_list.append(log_subtask)
		return True
	
	def rmLog_SubTask(self, id_todo: int, id_subtask: int) -> bool:
		# get log_todo
		log_todo: LogTodo = self._getLog_Todo_ID_(id_todo)
		if log_todo is None:
			return False

		# get index of log_subtask
		index: int = self._getIndex_SubTask_ID_(log_todo, id_subtask)
		if index < 0:
			return False

		# rm subtask
		log_todo.subtask_list.pop(index)
		return True

	def getLog_Todo_ID(self, id_: int) -> LogTodo:
		return self._getLog_Todo_ID_(id_)

	def getLog_SubTask_ID(self, log_todo: LogTodo, id_: int) -> LogSubTask:
		return self._getLog_SubTask_ID_(log_todo, id_)

	def load(self) -> bool:
		with open(self.file, "r") as f:
			data = f.read()
			data = json.loads(data)
			self._load_(data)

		return True

	def dump(self) -> bool:
		data = self._dump_()

		with open(self.file, "w") as f:
			data = json.dumps(data, indent=None, separators=(',', ':'))
			f.write(data)
		
		return True

	# Protected
	def _load_(self, data: Dict) -> None:
		# index
		self.index_todo 	= data[str(self.Label.INDEX_TODO)]
		self.index_subtask 	= data[str(self.Label.INDEX_SUBTASK)]

		# data list
		self.todo_list.clear()

		data_list: List[Dict] = data[str(self.Label.DATA_LIST)]
		for data in data_list:

			temp = LogTodo(-1, None, None)
			temp.setDictData(data)
			self.todo_list.append(temp)
	
	def _dump_(self) -> Dict:
		# ----- data -----
		data_list: List[Dict] = []
		for data in self.todo_list:
			data_list.append(data.getDictData())

		# ----- result -----
		result: Dict = {
			self.Label.DATA_LIST: 		data_list,
			self.Label.INDEX_TODO: 		self.index_todo,
			self.Label.INDEX_SUBTASK: 	self.index_subtask
		}

		return result

	def _getLog_Todo_Name_(self, name: str) -> LogTodo:
		for item in self.todo_list:
			if item.name != name:
				continue
			return item
		return None

	def _getLog_Todo_ID_(self, id_: int) -> LogTodo:
		for item in self.todo_list:
			if item.id_ != id_:
				continue
			return item
		return None

	def _getLog_SubTask_ID_(self, log_todo: LogTodo, id_: int) -> LogSubTask:
		for item in log_todo.subtask_list:
			if item.id_ != id_:
				continue
			return item
		return None

	def _getIndex_Todo_Name_(self, name: str) -> int:
		for index, item in enumerate(self.todo_list):
			if item.name != name:
				continue
			return index
		return -1

	def _getIndex_Todo_ID_(self, id_: int) -> int:
		for index, item in enumerate(self.todo_list):
			if item.id_ != id_:
				continue
			return index
		return -1

	def _getIndex_SubTask_ID_(self, log_todo: LogTodo, id_: int) -> int:
		for index, item in enumerate(log_todo.subtask_list):
			if item.id_ != id_:
				continue
			return index
		return -1
