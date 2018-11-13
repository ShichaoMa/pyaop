# -*- coding:utf-8 -*-
from pyaop import Proxy, AOP, Return


class A(object):
    a = 3

    def __init__(self):
        self.b = 3

    def __getitem__(self, item):
        return 1

    def __call__(self, a):
        return a * 3

    def fun(self, d, e):
        return d * e

    def bar(self, f, g):
        return f + g


class TestProxy(object):

    def test_callable_before(self):
        def before1(proxy, a):
            """
            before在被代理的方法调用之前调用，用来改变输入
            :param proxy: 代理实例
            :param a: 被代理的方法传入的参数，需要与代理的方法形参列表保持一致
            :return:
            """
            if a == 1:
                a = 5
                return (a, ), dict()

            if a == 3:
                Return(1000)

        def before2(proxy, a):
            return (a//2, ), dict()

        aa = A()
        a = Proxy(aa, before=[
            AOP.Hook(before1, ["__call__"]),
            AOP.Hook(before2, ["__call__"])])

        # 传入1，走到before1之后被改成了5，走到before2的时候被改成了2， 最后得到结果2*3
        assert a(1) == 6
        # 传入3，走到before1直接被返回了1000,不再走before2和被代理的方法。
        assert a(3) == 1000
        # 传入7，无修改通过before1， 随后在before2被改成3，最后得到结果3*3
        assert a(7) == 9

    def test_callable_after(self):
        def after1(proxy, ret_val):
            """
            after在被代理的方法调用之后调用，用来改变输出
            :param proxy: 代理实例
            :param ret_val: 被代理的方法返回值
            :return:
            """
            if ret_val < 10:
                return 10

            if ret_val < 100:
                Return(100)

            return ret_val

        def after2(proxy, ret_val):
            return ret_val//2

        aa = A()
        a = Proxy(aa, after=[
            AOP.Hook(after1, ["__call__"]),
            AOP.Hook(after2, ["__call__"])])

        # 传入1，得到结果1*3，走到after1之后被改成了10，走到after2的时候被改成了5
        assert a(1) == 5
        # 传入4，得到结果4*3，走到after1直接被返回了100,不再走after2
        assert a(4) == 100
        # 传入70，得到结果70*3，无修改通过after1，随后在after2被改成105
        assert a(70) == 105

    def test_nomal(self):
        aa = A()

        def common(proxy, name, value=None):
            if name == "b":
                Return(2)

        a = Proxy(aa, before=[
            AOP.Hook(common, ["__getattribute__", "__setattr__", "__delattr__"])])

        assert aa.b == 3
        assert a.b == 2
        a.b = 10
        assert aa.b == 3
        a.c = 10
        assert aa.c == 10
        assert a.c == 10
        del a.b
        assert hasattr(a, "b")
        assert hasattr(aa, "b")
        del a.c
        assert not hasattr(a, "c")
        assert not hasattr(aa, "c")

    def test_customize(self):

        class FunProxy(Proxy):
            proxy_methods = ["fun", "bar"]

        def common(proxy, name):
            return 2

        aa = A()
        a = FunProxy(aa,
                     before=[AOP.Hook(lambda *args, **kwargs:None, ["fun"])],
                     after=[AOP.Hook(common, ["__getitem__", "__call__", "fun"])])

        assert a.b == 3
        assert aa.b == 3
        assert a.__dict__ == {"b": 3}
        assert aa.__dict__ == {"b": 3}
        a.b = 5
        assert a.b == 5
        assert aa.b == 5
        assert a.__dict__ == {"b": 5}
        assert aa.__dict__ == {"b": 5}
        assert a["333"] == 2
        assert aa["333"] == 1
        assert a(3) == 2
        assert aa(3) == 9
        assert a.fun(3, 4) == 2
        assert aa.fun(3, 4) == 12
        assert a.bar(3, 4) == 7

    def test_object_del(self):
        aa = A()
        assert hasattr(aa, "b")
        AOP.object_del(aa, "b")
        assert not hasattr(aa, "b")
