import traceback
from flask import request
from utils.train_utils import *
from objects.RResponse import RResponse
from objects.RTask import RTask, TaskType
from flask import Blueprint

train_api = Blueprint("train_api", __name__)


@train_api.route("/train/stop", methods=["GET"])
def stop_training():
    """
    Stops the training thread
    ---
    tags:
      - train
    produces:
      - "application/json"
    responses:
      200:
        description: Training stopped or training cannot be stopped
        schema:
          properties:
            code:
              type: integer
              example: 0
            data:
              type: string
              example: Training stopped!
            msg:
              type: string
              example: Success
    """
    try:
        RTask.exit_tasks_of_type(TaskType.Training)
    except:
        RResponse.abort(500, "Failed to stop training", -1)

    return RResponse.ok("Training stopped!")


@train_api.route("/train", methods=["POST"])
def start_training():
    """
    Takes in a training config and start the training thread
    The server will check the configs before start training
    ---
    tags:
      - train
    consumes:
      - "application/json"
    produces:
      - "application/json"
    parameters:
      - in: "body"
        name: "body"
        description: "The training config"
        required: true
        schema:
          properties:
            configs:
              type: object
              example: {
                'use_paired_train': True,
                'mixture': 'random_pure',
                'auto_save_model': True,
                'batch_size': 128,
                'shuffle': True,
                'learn_rate': 0.1,
                'paired_train_reg_coeff': 0.001,
                'epoch': 20,
                'num_workers': 8,
                'user_edit_buffering': False,
                'save_every': 5,
                'use_tensorboard': True
              }
    responses:
      200:
        description: Training started or training cannot be started
        schema:
          properties:
            code:
              type: integer
              example: 0
            data:
              type: string
              example: Training started!
            msg:
              type: string
              example: Success
    """
    print("Requested to training with the following configuration: ")
    configs = request.get_json().get('configs')
    if not configs:
        RResponse.abort(400, f"Receiving empty training config. Aborted.")
    print(configs)

    # Return error message if config is invalid
    try:
        configs = TrainingConfig.from_dict(configs)
    except Exception as e: 
        RResponse.abort(400, f"Invalid Configuration!: {str(e)}")

    if not RServer.get_model_wrapper().model:
        RResponse.abort(400, "Current model not set!")

    # Try to start training thread
    print("DEBUG: Training request received! Setting up training...")

    # start the training thread
    try:
        start_train(configs)
    except ValueError as e:
        traceback.print_exc()
        RResponse.abort(400, f"Invalid parameters. {str(e)}")
    except Exception as e:
        traceback.print_exc()
        RResponse.abort(500, f"Failed to start training thread. {str(e)}")

    # Training started succesfully!
    print("Training started!")
    return RResponse.ok("Training started!")
