import operator


class RpcMethod(object):

    __slots__ = ('_methodType', '_method', '_classDefine', '_isCoroutine', '_methodType')

    TYPE_WITHOUT_CLASS = 0
    TYPE_WITH_CLASS = 1

    def __init__(self, methodType, method, classDefine = None, isCoroutine = False):
        self._methodType = methodType
        self._method = method
        self._classDefine = classDefine
        self._isCoroutine = isCoroutine
        if self._methodType == self.TYPE_WITH_CLASS and self._classDefine == None:
            raise Exception('classDefine is None')

    def call(self, *args, **kwargs):
        if self._methodType == self.TYPE_WITH_CLASS:
            classInstance = self._classDefine()
            resp = operator.methodcaller(self._method.__name__, *args, **kwargs)(classInstance)
        else:
            resp = self._method(*args, **kwargs)
        return resp