"""
Author: Chonghan Chen (paulcccccch@gmail.com)
-----
Last Modified: Friday, 10th March 2023 4:48:58 pm
Modified By: Chonghan Chen (paulcccccch@gmail.com)
-----
"""
import threading
from objects.RServer import RServer
from utils.path_utils import to_unix
from utils.predict import get_image_prediction, convert_predict_to_array
from objects.RImageFolder import REvalImageFolder
from os import path as osp
from objects.RTask import RTask, TaskType


class TestThread(threading.Thread):
    def __init__(self, split):
        super(TestThread, self).__init__()

        self.dataManager = RServer.get_data_manager()
        if split == "validation":
            self.dataset: REvalImageFolder = self.dataManager.validationset
        elif split == "test":
            self.dataset: REvalImageFolder = self.dataManager.testset
        else:
            raise NotImplementedError("Test called with wrong data split")

    def run(self):
        print("Starting testing thread")
        try:
            # TODO(chonghan): If we don't get a flask context here we are going to
            # get error. Are we going to have concurrency issues if we use the
            # same context as the main thread?
            with RServer.get_server().get_flask_app().app_context():
                self.start_test_thread()
        except Exception as e:
            raise e
        finally:
            RServer.get_model_wrapper().release_model()

    def start_test_thread(self):
        samples = self.dataset.samples
        dataset_length = len(samples)

        correct_buffer = []
        incorrect_buffer = []

        task = RTask(TaskType.Test, dataset_length)
        model_wrapper = RServer.get_model_wrapper()
        model_wrapper.model.eval()
        for img_path, label in samples:

            output = get_image_prediction(
                model_wrapper,
                img_path,
                self.dataManager.image_size,
                argmax=False,
            )
            output_array = convert_predict_to_array(output.cpu().detach().numpy())

            # TODO: replace this snippet with numpy argmax function
            max_value = 0
            max_index = -1
            index = 0
            for output_value in output_array:
                if output_value > max_value:
                    max_value = output_value
                    max_index = index
                index += 1

            is_correct = max_index == label
            if is_correct:
                correct_buffer.append((img_path, label))
            else:
                incorrect_buffer.append((img_path, label))

            # task update
            task_update_res = task.update()
            if not task_update_res:
                break
        else:
            # exit task if normal end of the test iteration
            # task.exit()
            pass
        self.dataset.post_records(correct_buffer, incorrect_buffer)
        calc_acc(correct_buffer, incorrect_buffer)
        print("Testing complete")

def calc_acc(correct_buffer, incorrect_buffer):
    counts = dict() # {label: [correct, total]}
    for _, label in correct_buffer:
        if label not in counts:
            counts[label] = [0, 0]
        counts[label][0] += 1 
        counts[label][1] += 1
    for _, label in incorrect_buffer:
        if label not in counts:
            counts[label] = [0, 0]
        counts[label][1] += 1
    
    for label, (correct, total) in counts.items():
        print(f"Label: {label}, correct: {correct}, total: {total}, accuracy: {correct / total}")
    

def start_test(split):
    model_wrapper = RServer.get_model_wrapper()
    if not model_wrapper.acquire_model():
        raise Exception(
            "Cannot start testing because model is occupied by another thread"
        )

    try:
        test_thread = TestThread(split)
        test_thread.start()
    except Exception as e:
        model_wrapper.release_model()
        raise e
