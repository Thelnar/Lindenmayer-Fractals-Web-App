import numpy as np
import json


def jeffson_numpy_ndarray_handler(obj, bEncoding):
    """
    Encode or Decode a numpy ndarray object for storage in JSON
    :param obj: numpy.ndarray or list.  The object to be Encoded/Decoded
    :param bEncoding: Boolean. True to encode, where it will take an ndarray and return a list.
    :return: list or numpy.ndarray.  The Encoded or Decoded object.
    """
    if bEncoding:
        return obj.tolist()
    else:
        return np.array(obj)


dctJeffSONFunctions = {
    "<class 'numpy.ndarray'>": jeffson_numpy_ndarray_handler
}


class JeffSONEncoder(json.JSONEncoder):
    """
    JSON Encoder class meant to be passed for the json.dumps function. Calls default encoding for the following types:
    dict, list, tuple, str, int, float, bool
    For types beyond that, it looks up an encoding function from dctJeffSONFunctions
    """
    def default(self, obj):
        if obj is not None and not isinstance(obj, (dict, list, tuple, str, int, float, bool)):
            return {"_type": str(type(obj)),
                    "_contents": dctJeffSONFunctions[str(type(obj))](obj, True)}
        return json.JSONEncoder.default(self, obj)


class JeffSONDecoder(json.JSONDecoder):
    """
    JSON Decoder class meant to be passed for the json.dumps function. Calls default decoding for the following types:
    dict, list, tuple, str, int, float, bool
    For types beyond that, it looks up an decoding function from dctJeffSONFunctions
    """
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    @staticmethod
    def object_hook(obj):
        if "_type" in obj:
            return dctJeffSONFunctions[obj["_type"]](obj["_contents"], False)
        return obj


def generator_looper(fncGeneratorPartial, lMaxLoops=None):
    itTemp = fncGeneratorPartial()
    try:
        next(itTemp)
    except StopIteration:
        raise Exception("Generator Partial passed in generates nothing!")
    if lMaxLoops is None:
        while True:
            itTemp = fncGeneratorPartial()
            try:
                yield from itTemp
            except StopIteration:
                continue
    else:
        for i in range(lMaxLoops):
            itTemp = fncGeneratorPartial()
            try:
                yield from itTemp
            except StopIteration:
                continue
