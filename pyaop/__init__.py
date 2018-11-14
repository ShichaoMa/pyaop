# -*- coding:utf-8 -*-
"""
@Created on 2018/11/13
@Modify on 2018/11/13
@author cnaafhvk888@gmail.com
"""
import six

from collections import namedtuple


__version__ = "0.0.6"


class AOPReturn(Exception):
    pass


def Return(value):
    raise AOPReturn(value)


class AOP(object):
    """
    代理服务AOP类
    """
    Hook = namedtuple("ProxyHook", "func,types")

    def __init__(self, before, after):
        self.before = before or []
        self.after = after or []

    def __call__(self, func, proxy, *args, **kwargs):
        # 单独处理一下使用getattribute返回方法的情况
        # 这种情况如果是要代理的方法名则直接代理的方法。
        try:
            proxy_methods = self.object_get(proxy, "proxy_methods")
        except AttributeError:
            proxy_methods = []

        if func.__name__ == "__getattribute__" and args[0] in proxy_methods:
            return self.object_get(proxy, args[0])

        try:
            for before in self.before:
                if func.__name__ in before.types:
                    ret = before.func(proxy, *args, **kwargs)
                    # 有返回值，才设置新的实参
                    if ret:
                        args, kwargs = ret
            ret_val = func(*args, **kwargs)

            for after in self.after:
                if func.__name__ in after.types:
                    ret_val = after.func(proxy, ret_val)

            return ret_val
        except AOPReturn as ret:
            return ret.args[0]

    @staticmethod
    def object_get(obj, name):
        return object.__getattribute__(obj, name)

    @staticmethod
    def object_set(obj, name, value):
        return object.__setattr__(obj, name, value)

    @staticmethod
    def object_del(obj, name):
        return object.__delattr__(obj, name)


def aop_decorator(name, module=__name__):
    def inner(*args, **kwargs):
        aop = AOP.object_get(args[0], "_proxy_aop")
        proxy_obj = AOP.object_get(args[0], "_proxy_obj")
        return aop(AOP.object_get(proxy_obj, name), *args, **kwargs)

    inner.__name__ = name
    inner.__module__ = module
    return inner


class ProxyMeta(type):
    magic_methods = {"__getslice__",
                     "__setslice__",
                     "__delslice__",
                     "__setattr__",
                     "__getattr__",
                     "__delattr__",
                     "__str__",
                     "__lt__",
                     "__le__",
                     "__eq__",
                     "__ne__",
                     "__gt__",
                     "__ge__",
                     "__cmp__",
                     "__hash__",
                     "__call__",
                     "__len__",
                     "__getitem__",
                     "__setitem__",
                     "__delitem__",
                     "__iter__",
                     "__contains__",
                     "__add__",
                     "__sub__",
                     "__mul__",
                     "__floordiv__",
                     "__mod__",
                     "__divmod__",
                     "__pow__",
                     "__lshift__",
                     "__rshift__",
                     "__and__",
                     "__xor__",
                     "__or__",
                     "__div__",
                     "__truediv__",
                     "__neg__",
                     "__pos__",
                     "__abs__",
                     "__invert__",
                     "__complex__",
                     "__int__",
                     "__long__",
                     "__float__",
                     "__oct__",
                     "__hex__",
                     "__index__",
                     "__coerce__",
                     "__enter__",
                     "__exit__",
                     "__radd__",
                     "__rsub__",
                     "__rmul__",
                     "__rdiv__",
                     "__rtruediv__",
                     "__rfloordiv__",
                     "__rmod__",
                     "__rdivmod__",
                     "__copy__",
                     "__deepcopy__",
                     "__dir__",
                     "__bool__",
                     "__repr__",
                     "__unicode__",
                     "__getattribute__"}

    def __new__(cls, name, bases, props):
        for magic_method in cls.magic_methods:
            props[magic_method] = aop_decorator(magic_method)

        for proxy_method in props.get("proxy_methods", []):
            props[proxy_method] = aop_decorator(proxy_method)

        return super(cls, ProxyMeta).__new__(cls, name, bases, props)


@six.add_metaclass(ProxyMeta)
class Proxy(object):
    """
    代理层，为指定对象代理一个属性
    """
    def __init__(self, proxy_obj, before=None, after=None):
        AOP.object_set(self, "_proxy_obj", proxy_obj)
        AOP.object_set(self, "_proxy_aop", AOP(before, after))
