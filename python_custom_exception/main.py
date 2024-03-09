class ARandomError(Exception):
    """This is a random error"""
    def __init__(self, reason=None):
        self.reason = reason
        message = "This is a random exception caused by: %s" % reason

class AnotherRandomError(Exception):
    """
    This is another random error
    """

    def __init__(self, reason=None):
        self.reason = reason

        message = "Max retries exceeded with url: %s (Caused by %r)" % ("https://url.com", reason)

def main(causeException=False):
    if causeException:
        variable = "Hello"
        raise ARandomError(
            "This is an example exception: %s" % variable
        )
    else:
        return
    
class programcontainer():
    def init():
        print("This is the init() function inside the programcontainer class")
    def doanything():
        print("This is the doanything() function inside the programcontainer class")

# Me testing it
"""
Python 3.9.2 (default, Feb 28 2021, 17:03:44) 
[GCC 10.2.1 20210110] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import ExceptionTest
>>> ExceptionTest.main(True)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/jotalea/Descargas/ExceptionTest.py", line 27, in main
    raise ARandomError(
ExceptionTest.ARandomError: This is an example exception: Hello
>>> raise ARandomError(
...             "This is an example exception: %s" % variable
...         )
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'ARandomError' is not defined
>>> variable = "Hello"
>>> raise ExceptionTest.ARandomError(
...             "This is an example exception: %s" % variable
...         )
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ExceptionTest.ARandomError: This is an example exception: Hello
>>> raise ExceptionTest.ARandomError("This is an example exception: %s" % variable)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ExceptionTest.ARandomError: This is an example exception: Hello
>>> variable = "Hello world"
>>> raise ExceptionTest.ARandomError("This is an example exception: %s" % variable)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ExceptionTest.ARandomError: This is an example exception: Hello world
>>> try:
...     raise ExceptionTest.ARandomError("This is an example exception: %s" % variable)
... except ExceptionTest.ARandomError:
...     print("ARandomError exception prevented")
... 
ARandomError exception prevented
"""
