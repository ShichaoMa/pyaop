# pyaop
pyaop实现了一个代理类，用来代理一个对象，不破坏被代理对象的内部结构的前提下，改变被代理中方法调用的行为
pyaop可以从方法调用的开始前和结束后两个切面切入一个方法，改变其入参及出参。该方法可以是magic方法或者用户自定义的方法。

## pyaop代理流程图
![](https://github.com/ShichaoMa/pyaop/blob/master/resources/pyaop.jpg)