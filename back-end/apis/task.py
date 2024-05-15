from objects.RServer import RServer
from objects.RResponse import RResponse
from objects.RTask import RTask
from flask import Blueprint

task_api = Blueprint("task_api", __name__)

@task_api.route("/task/stop/<tid>", methods=["GET"])
def stop_task(tid):
    tid = int(tid)
    print(tid)
    try:
        if not RTask.exit_task(tid):
            RResponse.abort(400, f"Task({tid}) not in list")
    except ValueError as e:
        RResponse.abort(500, f"Error deleting task id ({tid}). Id: {e}")
    return RResponse.ok(f"Task({tid}) has been stopped")

@task_api.route("/task", methods=["GET"])
def list_task():
    try:
        return RResponse.ok([task.as_dict() for task in RTask.list_tasks()])
    except Exception as e:
        RResponse.abort(500, f"Failed to list task. Error: {str(e)}")

@task_api.route("/task/<tid>", methods=["GET"])
def get_task(tid):
    try:
        task = RTask.find_task(int(tid))
        if task is None:
            RResponse.abort(400, f"Task({tid}) not in list")
        return RResponse.ok(task.as_dict())
    except ValueError as e:
        RResponse.abort(500, f"Fail to list task. Error: {str(e)}")
