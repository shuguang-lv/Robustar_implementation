import binascii
import traceback

from apis.api_configs import PARAM_NAME_IMAGE_PATH
from objects.RServer import RServer
from objects.RResponse import RResponse
from flask import request
import base64
from utils.edit_utils import (
    propose_edit,
    save_edit,
    start_auto_annotate,
    remove_edit,
    clear_edit,
)
from utils.path_utils import to_unix
from flask import Blueprint
from utils.image_utils import image_to_base64_string

edit_api = Blueprint("edit_api", __name__)


@edit_api.route("/edit/<split>", methods=["POST"])
def api_user_edit(split):
    """
    Save user's edit for an image
    ---
    tags:
      - edit
    consumes:
      - "application/json"
    produces:
      - "application/json"
    parameters:
      - name: "split"
        in: "path"
        description: "name of the split, valid values are 'train' or 'annotated'"
        required: true
        type: "string"
      - name: "path"
        in: "path"
        description: "If `split` is 'train', then this is the path to the training image. If `split` is `annotated`, then it is the path to annotated image"
        required: true
        type: "integer"
      - in: "body"
        name: "body"
        description: "The edit config"
        required: true
        schema:
          properties:
            image:
              type: string
              example: the base64 encoding of the image
            image_height:
              type: integer
            image_width:
              type: integer
    responses:
      200:
        description: edit success
    """
    path = request.args.get(PARAM_NAME_IMAGE_PATH)
    path = to_unix(path)

    # TODO: Maybe support editing other splits as well? Or not?
    if split not in ["train", "annotated", "proposed"]:
        RResponse.abort(400, "Split {} not supported".format(split))

    json_data = request.get_json()
    encoded_string = json_data["image"].split(",")[1]
    h = int(json_data["image_height"])
    w = int(json_data["image_width"])

    try:
        decoded = base64.b64decode(encoded_string)
        save_edit(split, path, decoded, h, w)
        return RResponse.ok("Success!")
    except binascii.Error:
        traceback.print_exc()
        RResponse.abort(400, "Broken image, fail to decode")
    except ValueError as e:
        traceback.print_exc()
        RResponse.abort(400, str(e))
    except Exception as e:
        traceback.print_exc()
        RResponse.abort(500, str(e))


@edit_api.route("/edit/<split>", methods=["DELETE"])
def api_delete_edit(split):
    path = request.args.get(PARAM_NAME_IMAGE_PATH)
    try:
        remove_edit(path)
        return RResponse.ok("Success!")
    except Exception as e:
        RResponse.abort(500, f"Failed to delete edit path. ({e})", -1)


@edit_api.route("/edit/clear", methods=["DELETE"])
def api_clear_edit():
    try:
        clear_edit()
        return RResponse.ok("Success!")
    except Exception as e:
        RResponse.abort(500, f"Failed to clear edit path. ({e})", -1)


@edit_api.route("/propose/<split>")
def api_propose_edit(split):
    """
    Get edited image proposed by auto annotator

    TODO: This function may be called twice redundantly if front end user
    clicked on 'auto edit' while 'ProposedEditVue' component is still
    generating a proposed annotation. This needs to be fixed with some
    kind of lock.

    args:
        split:    'train' or 'annotated'
        image_id: The index of the image within the dataset
    returns:
        proposed image path that can be placed in <img> tag with proper
        server url as prefix
    """
    path = request.args.get(PARAM_NAME_IMAGE_PATH)

    if split not in ["annotated", "train"]:
        return RResponse.ok(
            None,
            "Split {} not supported! Currently we only support editing the `train` or `annotated` splits!".format(
                split
            ),
            -1,
        )

    path = to_unix(path)
    proposed_image_path, _ = propose_edit(split, path)
    base64 = image_to_base64_string(proposed_image_path)

    response = {"path": proposed_image_path, "base64": base64}

    return RResponse.ok(response)


@edit_api.route("/auto-annotate/<split>", methods=["POST"])
def api_auto_annotate(split):
    """ 
    Batch auto-annotate training set from start_idx to end_idx 
    """

    if split != "train":
        RResponse.abort(
            400,
            "Split {} not supported! Currently we only support editing the `train` or `annotated` splits!".format(
                split
            ),
        )

    json_data = request.get_json()


    try:
        start = int(json_data["start_idx_to_gen"])
        end = int(json_data["end_idx_to_gen"])
    except Exception:
        raise Exception(f"Bad input indices: {start}, {end}")

    try:
        start_auto_annotate(split, start, end)
    except Exception as e:
        RResponse.abort(500, "Auto annotation failed: " + str(e))

    return RResponse.ok("success")
