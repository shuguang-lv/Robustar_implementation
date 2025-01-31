import { getRequest, postRequest } from './common';

/**
 * @param {object} configs the training configuration
 */
export const APIStartTrain = async (configs) => {
  return postRequest(`/train`, configs);
};

export const APIStopTrain = async () => {
  return getRequest(`/train/stop`);
};
