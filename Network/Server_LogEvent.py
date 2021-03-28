from typing import *
from shutil import copyfile
import json
import datetime
from flask import Flask, request
from flask_cors import CORS
import logging
from LogEvent import *


# Data
# TODO: find a way to remove this ugly thing
control_log: 		LogControl 			= LogControl()
control_todo:		Control_LogTodo		= Control_LogTodo()

data_control_log:	List[LogControl]		= [control_log]
data_control_todo:	List[Control_LogTodo]	= [control_todo]


# Operation
app = Flask(__name__)
CORS(app)
log = logging.getLogger("werkzeug")
log.disabled = True


# Function
# utility
def convertDate_Str_List(x: str, separator="_") -> List[int]:
	return [int(item) for item in x.split("_")][:3]


def convertTime_Str_List(x: str, separator="_") -> List[int]:
	return [int(item) for item in x.split("_")][:2]


def convertDate_List_Str(x: List[int], separator="-") -> str:
	if x is None:
		return "NA"
	return f"{x[0]:02d}{separator}{x[1]:02d}{separator}{x[2]:02d}"


def convertTime_List_Str(x: List[int], separator=":") -> str:
	if x is None:
		return "NA"
	return f"{x[0]:02d}{separator}{x[1]:02d}"


def checkFormat_TimeList(x: Any, is_none: bool = True) -> bool:
	if x is None:
		return is_none

	if type(x) != list or len(x) != 2:
		return False
	if type(x[0]) != int or type(x[1]) != int:
		return False
	return True


def getArgument(target: List[Any], name: str, func_convert: Callable[[str], Any]) -> bool:
	try:
		data = request.args.get(name)
		data = func_convert(data)

	except Exception:
		return False

	# if there is existing item
	# it is assumed that that item is the default value
	if not target:
		target.append(data)
	else:
		target[0] = data
	return True


# ----- route -----
@app.route("/GetDateList")
def getDateList():
	# ----- compute return data -----
	date_list: List[List[int]] = []

	for log_date in control_log.date_list:
		date_list.append(log_date.date)

	# ----- log -----
	print(
		f"date_list queried: "
		f"size of date_list: {len(date_list)}")

	# ----- return -----
	result = json.dumps(date_list)
	return result


@app.route("/GetEvent_Date")
def getEvent_Date():
	# ----- get data -----
	date: Any = []
	if not getArgument(date, "date", convertDate_Str_List):
		return "{}"
	date: List[int] = date[0]

	# ----- compute return data -----
	# get LogDate
	log_date: 	LogDate 		= control_log.getDate(date)
	event_list:	List[LogEvent]	= log_date.event_list if log_date is not None else []

	# compute return data
	data: List[Any] = []
	for log_event in event_list:

		# ----- time -----
		# # HH:MM - HH:MM
		# time: str = \
		# 	f"{log_event.time_start[0]:02d}:{log_event.time_start[1]:02d} - " \
		# 	f"{log_event.time_end[0]:02d}:{log_event.time_end[1]:02d}"

		time: List[int] = [
			log_event.time_start[0],	log_event.time_start[1],
			log_event.time_end[0],		log_event.time_end[1]]

		# ----- event string -----
		# get list of tag
		tag_list: List[str] = []
		for tag in log_event.tag:
			tag_list.append(tag)

		# sort the tag_list (abcde...)
		tag_list.sort()

		# generate event name based on tag_list
		event: str = ""
		for tag in tag_list:
			if len(event) != 0:
				event += ", "
			event += tag

		# ----- merge data -----
		data.append([
			time,
			tag_list
		])

	# ----- log -----
	print(
		f"list of event queried: "
		f"date: {convertDate_List_Str(date)}, size of event: {len(event_list)}")

	# ----- return -----
	# to json string, then return 
	result = json.dumps(data)
	return result


@app.route("/AddDate", methods=["POST"])
def addDate():
	# ----- get data -----
	# config
	date: Any = []

	# necessary
	if not getArgument(date, "date", convertDate_Str_List):
		return "{}"

	# unpack
	date: List[int] = date[0]

	# ----- add date -----
	control_log.addDate(date)

	# ----- dump -----
	control_log.dump()
	
	# ----- log -----
	print(
		f"date created: "
		f"date: {		convertDate_List_Str(date)}, ")

	# ----- return -----
	return "{}"


@app.route("/AddEvent", methods=["POST"])
def addEvent():
	# ----- get data -----
	# config
	date:		Any = []
	time_start: Any = [None]
	time_end:	Any = [None]
	tag_list:	Any = [None]

	# necessary
	if not getArgument(date, 		"date", 		convertDate_Str_List) or \
		not getArgument(time_start, "time_start", 	convertTime_Str_List) or \
		not getArgument(tag_list,	"tag",			lambda x: x.split(",")):
		return "{}"

	# optional
	getArgument(time_end, "time_end", convertTime_Str_List)

	# unpack
	date:		List[int]	= date[0]
	time_start:	List[int]	= time_start[0]
	time_end:	List[int]	= time_end[0]
	tag_list:	List[str]	= tag_list[0]

	# ----- add event -----
	# create LogEvent
	log_event = LogEvent()

	log_event.start(time_start)
	log_event.end(time_end)
	for tag in tag_list:
		log_event.addTag(tag)

	# add event to LogControl
	control_log.addEvent(date, log_event)

	# ----- dump -----
	control_log.dump()
	
	# ----- log -----
	print(
		f"event created: "
		f"date: {		convertDate_List_Str(date)}, "
		f"time start: {	convertTime_List_Str(time_start)}, "
		f"time end: {	convertTime_List_Str(time_end)}, "
		f"tag: {		tag_list}")

	# ----- return -----
	return "{}"


@app.route("/RmEvent", methods=["POST"])
def rmEvent():
	# ----- get data -----
	date: 	Any = []
	index:	Any = []

	# necessary
	if not getArgument(date, 	"date", 	convertDate_Str_List) or \
		not getArgument(index,	"index",	lambda x: int(x)):
		return "{}"

	# unpack
	date:	List[int]	= date[0]
	index:	int			= index[0]

	# ----- rm event -----
	# remove event
	if not control_log.rmEvent(date, index):
		return "{}"

	# ----- dump -----
	control_log.dump()
	
	# ----- log -----
	print(
		f"event deleted: "
		f"date: {	convertDate_List_Str(date) }, "
		f"index: {	index }")
	
	# ----- return -----
	return "{}"


@app.route("/ConfigEvent", methods=["POST"])
def configEvent():
	# ----- get data -----
	# config
	date:		Any = []
	index:		Any = []
	time_start: Any = [None]
	time_end:	Any = [None]
	tag_list:	Any = [None]

	# necessary
	if not getArgument(date, 	"date", 	convertDate_Str_List) or \
		not getArgument(index,	"index",	lambda x: int(x)):
		return "{}"

	# optional
	getArgument(time_start, "time_start", 	convertTime_Str_List)
	getArgument(time_end,	"time_end", 	convertTime_Str_List)
	getArgument(tag_list,	"tag",			lambda x: x.split(","))

	# unpack
	date:		List[int]	= date[0]
	index:		int			= index[0]
	time_start:	List[int]	= time_start[0]
	time_end:	List[int]	= time_end[0]
	tag_list:	List[str]	= tag_list[0]

	# ----- verify -----
	# time
	if not checkFormat_TimeList(time_start):
		return "{}"
	if not checkFormat_TimeList(time_end):
		return "{}"

	# TODO: check tag_list

	# ----- config event -----
	# get event
	log_event: LogEvent = control_log.getEvent(date, index)
	if log_event is None:
		return "{}"

	# config event
	if time_start is not None:
		log_event.start(time_start)
	if time_end is not None:
		log_event.end(time_end)
	if tag_list is not None:
		log_event.setTag(tag_list)

	# ----- dump -----
	control_log.dump()

	# ----- log -----
	print(
		f"event configured: "
		f"date: {		convertDate_List_Str(date)}, "
		f"index: {		index}, "
		f"time start: {	convertTime_List_Str(time_start)}, "
		f"time end: {	convertTime_List_Str(time_end)}, "
		f"tag: {		tag_list}")

	# ----- return -----
	return "{}"


@app.route("/GetTodoList")
def getTodoList():
	# ----- get data -----
	# ...

	# ----- compute return data -----
	todo_list: List[Any] = []

	for log_todo in control_todo.todo_list:
		temp: List[Any] = []

		# id, name, note
		temp.append(log_todo.id_)
		temp.append(log_todo.name)
		temp.append(log_todo.note)
		
		# sub-task
		subtask_list = []
		for log_subtask in log_todo.subtask_list:
			subtask_list.append([
				log_subtask.id_,
				log_subtask.name,
				log_subtask.is_done])

		temp.append(subtask_list)

		# add to todo_list
		todo_list.append(temp)

	# ----- log -----
	print(
		f"todo_list queried: "
		f"size of todo_list: {len(todo_list)}")

	# ----- return -----
	result = json.dumps(todo_list)
	return result


@app.route("/AddTodo", methods=["POST"])
def addTodo():
	# ----- get data -----
	# config
	name:	Any	= []
	note:	Any = []

	# necessary
	if not getArgument(name, "name", lambda x: x):
		return "{}"

	# optional
	getArgument(note, "note", lambda x: x)

	# unpack
	name:	str	= name[0]
	note:	str = note[0]

	# ----- add todo -----
	if not control_todo.addLog_Todo(name, note):
		return "{}"

	# ----- dump -----
	control_todo.dump()

	# ----- log -----
	print(
		f"todo created: "
		f"name: {name}, "
		f"note: {note}")

	# ----- return -----
	return "{}"


@app.route("/RmTodo", methods=["POST"])
def rmTodo():
	# ----- get data -----
	# config
	id_: Any = []

	# necessary
	if not getArgument(id_, "id", lambda x: int(x)):
		return "{}"

	# unpack
	id_: int = id_[0]

	# ----- rm todo -----
	# remove todo
	if not control_todo.rmLog_Todo(id_):
		return "{}"

	# ----- dump -----
	control_todo.dump()

	# ----- log -----
	print(
		f"todo deleted: "
		f"id: {id_}")

	# ----- return -----
	return "{}"


@app.route("/ConfigTodo", methods=["POST"])
def configTodo():
	# ----- get data -----
	# config
	id_:	Any = []
	name:	Any = [None]
	note:	Any = [None]

	# necessary
	if not getArgument(id_, "id", lambda x: int(x)):
		return "{}"

	# optional
	getArgument(name, "name", lambda x: x)
	getArgument(note, "note", lambda x: x)

	# unpack
	id_:	int = id_[0]
	name:	str = name[0]
	note:	str = note[0]

	# ----- config -----
	log_todo: LogTodo = control_todo.getLog_Todo_ID(id_)
	if log_todo is None:
		return "{}"

	if name is not None:
		log_todo.name = name
	if note is not None:
		log_todo.note = note

	# ----- dump -----
	control_todo.dump()

	# ----- log -----
	print(
		f"todo configured: "
		f"name: {name}, "
		f"note: {note}")

	# ----- return -----
	return "{}"


@app.route("/AddSubTask", methods=["POST"])
def addSubTask():
	# ----- get data -----
	# config
	id_:		Any	= []
	name:		Any = []
	is_done:	Any = []

	# necessary
	if not getArgument(id_, 		"id", 		lambda x: int(x)) or \
		not getArgument(name, 		"name", 	lambda x: x) or \
		not getArgument(is_done,	"is_done",	lambda x: True if x == "1" else False):
		return "{}"

	# unpack
	id_:		int 	= id_[0]
	name:		str 	= name[0]
	is_done:	bool	= is_done[0]

	# ----- add todo -----
	# create LogSubTask
	if not control_todo.addLog_SubTask(id_, name, is_done):
		return "{}"

	# ----- dump -----
	control_todo.dump()

	# ----- log -----
	print(
		f"subtask created: "
		f"id: {id_}, "
		f"subtask: name: {name}, "
		f"subtask: is_done: {is_done}")

	# ----- return -----
	return "{}"


@app.route("/RmSubTask", methods=["POST"])
def rmSubTask():
	# ----- get data -----
	# config
	id_todo:	Any	= []
	id_subtask:	Any = []

	# necessary
	if not getArgument(id_todo, 	"id_todo", 		lambda x: int(x)) or \
		not getArgument(id_subtask, "id_subtask", 	lambda x: int(x)):
		return "{}"

	# unpack
	id_todo:	int = id_todo[0]
	id_subtask:	int = id_subtask[0]

	# ----- rm subtask -----
	# remove subtask
	if not control_todo.rmLog_SubTask(id_todo, id_subtask):
		return "{}"

	# ----- dump -----
	print(
		f"subtask deleted: "
		f"id_todo: {id_todo}, "
		f"id_subtask: {id_subtask}")

	# ----- return -----
	return "{}"


@app.route("/ConfigSubTask", methods=["POST"])
def configSubTask():
	# ----- get data -----
	# config
	id_todo:	Any = []
	id_subtask:	Any = []
	name:		Any = [None]
	is_done:	Any = [None]

	# necessary
	if not getArgument(id_todo, "id_todo", lambda x: int(x)):
		return "{}"
	if not getArgument(id_subtask, "id_subtask", lambda x: int(x)):
		return "{}"

	# optional
	getArgument(name, 		"name", 	lambda x: x)
	getArgument(is_done, 	"is_done", 	lambda x: True if x == "1" else False)

	# unpack
	id_todo:	int 	= id_todo[0]
	id_subtask:	int		= id_subtask[0]
	name:		str 	= name[0]
	is_done:	bool 	= is_done[0]

	# ----- config -----
	log_todo: LogTodo = control_todo.getLog_Todo_ID(id_todo)
	if log_todo is None:
		return "{}"

	log_subtask: LogSubTask = control_todo.getLog_SubTask_ID(log_todo, id_subtask)
	if log_subtask is None:
		return "{}"

	if name is not None:
		log_subtask.name = name
	if is_done is not None:
		log_subtask.is_done = is_done

	# ----- dump -----
	control_todo.dump()

	# ----- log -----
	print(
		f"subtask configured: "
		f"name: {name}, "
		f"is_done: {is_done}")

	# ----- return -----
	return "{}"
