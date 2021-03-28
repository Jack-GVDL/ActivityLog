from typing import *
import json
from enum import IntEnum, auto
from .Interface_DictData import Interface_DictData


# Data Structure
class LogEvent(Interface_DictData):

	# Enum
	class Label(IntEnum):
		TIME_START	= 0
		TIME_END	= 1
		TAG_LIST	= 2

	# Data Static
	label = Label

	def __init__(
		self, 
		time_start: List[int]	= (0, 0),
		time_end: 	List[int]	= (0, 0),
		tag_list: 	List[str] 	= ()) -> None:
		
		super().__init__()

		# data
		self.tag:           List[str]   = []
		self.time_start:    List[int]   = [0, 0]  # HH, MM
		self.time_end:      List[int]   = [0, 0]  # HH, MM

		# operation
		# tag
		for tag in tag_list:
			self.tag.append(tag)

		# time
		self.start(list(time_start))
		self.end(list(time_end))

	def __del__(self) -> None:
		return

	# Property
	# duration: in minute
	@property
	def duration(self) -> int:
		# assume: time_end is later than time_start
		hour: 	int = self.time_end[0] - self.time_start[0]
		minute:	int = self.time_end[1] - self.time_start[1]

		minute = hour * 60 + minute
		return minute

	# Operation
	def start(self, time: List[int]) -> None:
		self.time_start[0]	= int(time[0])
		self.time_start[1]	= int(time[1])

		# adjust the end time if start time is later than end time
		if self.time_start > self.time_end:
			self.time_end = self.time_start.copy()
	
	def end(self, time: List[int]) -> None:
		self.time_end[0] 	= int(time[0])
		self.time_end[1]	= int(time[1])

		# adjust the start time if end time is earlier than start time
		if self.time_end < self.time_start:
			self.time_start = self.time_end.copy()

	def setTag(self, tag_list: List[str]) -> None:
		self.tag.clear()
		self.tag.extend(tag_list)

	def addTag(self, tag: str) -> None:
		self.tag.append(tag)

	# Interface
	def getDictData(self) -> Dict:
		return {
			self.label.TAG_LIST.value:		self.tag,
			self.label.TIME_START.value:	self.time_start,
			self.label.TIME_END.value:		self.time_end
		}

	def setDictData(self, data: Dict) -> None:
		self.tag  = data[str(self.label.TAG_LIST.value)]
		self.start(	data[str(self.label.TIME_START.value)]	)
		self.end(	data[str(self.label.TIME_END.value)]		)


class LogDate(Interface_DictData):

	# TODO: require other lib
	class Label:
		# data
		DATE:		int = 0
		EVENT_LIST:	int = 1

	def __init__(self, date: List[int] = (0, 0, 0)) -> None:
		super().__init__()

		# data
		self.event_list:	List[LogEvent] 	= []
		self.date:			List[int]		= [0, 0, 0]  # YYYY, MM, DD 

		# operation
		self.setDate(list(date))

	def __del__(self) -> None:
		return

	# Operation
	def addEvent(self, event: LogEvent, is_update: bool = True) -> bool:
		self.event_list.append(event)
		if is_update:
			self._update_()
		return True

	def rmEvent(self, index: int, is_update: bool = True) -> bool:
		if index < 0 or index >= len(self.event_list):
			return False
		self.event_list.pop(index)
		
		if is_update:
			self._update_()
		return True

	def setDate(self, date: List[int]) -> None:
		self.date[0] = int(date[0])
		self.date[1] = int(date[1])
		self.date[2] = int(date[2])

	def update(self) -> None:
		self._update_()

	# Interface
	def getDictData(self) -> Dict:
		result: Dict = {
			self.Label.DATE:	self.date,
		}

		# ----- event -----
		# get list of event
		event_list: List[Dict] = []
		for event in self.event_list:
			event_list.append(event.getDictData())

		# add to result
		result[self.Label.EVENT_LIST] = event_list

		return result

	def setDictData(self, data: Dict) -> None:
		# ----- date -----
		self.setDate(data[str(self.Label.DATE)])

		# ----- event list -----
		self.event_list.clear()

		event_list: List[Dict] = data[str(self.Label.EVENT_LIST)]
		for event in event_list:
			temp = LogEvent()
			temp.setDictData(event)
			self.event_list.append(temp)

	# Protected
	def _update_(self) -> None:
		# sort the event_list based on the start time
		self.event_list.sort(key=lambda x: x.time_start)


class LogControl:

	# TODO: require lib
	class Label:
		DATA_LIST:	int = 0

	def __init__(self) -> None:
		super().__init__()
		
		# data
		self.file: 		str = ""
		self.date_list: List[LogDate] = []

		# operation
		# ...

	def __del__(self) -> None:
		return

	# Operation
	def addDate(self, date: List[int]) -> bool:
		log_date = LogDate(date)
		
		if self._addDate_(log_date) is False:
			return False

		# update
		self._update_()
	
		return True

	def addEvent(self, date: List[int], log_event: LogEvent) -> bool:
		log_date = LogDate(date)
		log_date.addEvent(log_event)
		
		if self._addDate_(log_date) is False:
			return False

		# update
		self._update_()
		
		return True
	
	def rmEvent(self, date: List[int], index: int) -> bool:
		# get log_date
		log_date: LogDate = self._getDate_(date)
		if log_date is None:
			return False

		# remove log_event from log_date
		if log_date.rmEvent(index) is False:
			return False

		# remove log_date if event_list in log_date is empty
		if not log_date.event_list:
			index: int = self.date_list.index(log_date)
			self._rmDate_(index)

		# update
		self._update_()

		return True

	def getEvent(self, date: List[int], index) -> LogEvent:
		# get log_date
		log_date: LogDate = self._getDate_(date)
		if log_date is None:
			return None

		# check if the index is valid or not
		if index < 0 or index >= len(log_date.event_list):
			return None

		return log_date.event_list[index]

	def getDate(self, date: List[int]) -> LogDate:
		return self._getDate_(date)

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

	def update(self) -> None:
		self._update_()

	# Protected
	def _load_(self, data: Dict) -> None:
		# ----- date -----
		date_list: List[Dict] = data[str(self.Label.DATA_LIST)]
		for date in date_list:
			temp = LogDate()
			temp.setDictData(date)
			self._addDate_(temp)

		# update
		self._update_()
	
	def _dump_(self) -> Dict:
		# ----- date -----
		date_list: List[Dict] = []
		for date in self.date_list:
			date_list.append(date.getDictData())

		# ----- result -----
		result: Dict = {
			self.Label.DATA_LIST: date_list
		}

		return result

	def _addDate_(self, log_date: LogDate) -> bool:
		date_old: LogDate = self._getDate_(log_date.date)

		# check if the date existed or not
		# not exist, append
		if date_old is None:
			self.date_list.append(log_date)
			return True

		# exist, merge
		for event in log_date.event_list:
			date_old.addEvent(event, is_update=False)
		date_old.update()

		return True

	def _rmDate_(self, index: int) -> bool:
		self.date_list.pop(index)
		return True

	def _getDate_(self, date: List[int]) -> LogDate:
		for log_date in self.date_list:
			if date != log_date.date:
				continue
			return log_date
		return None

	def _update_(self) -> None:
		# update task
		# - merge log_date (that is the same date)
		# - sort log_date (key=log_date.date)

		# merge
		# ...

		# sort
		self.date_list.sort(key=lambda x: x.date)
