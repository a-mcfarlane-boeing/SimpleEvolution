def getVal():
    return 20

val = getVal

print(val())

def blankFunction():
    pass

val = blankFunction

print(val)

def assignFunction():
    def otherFunction():
        return 30
    
    return otherFunction


def wrapper(someFunc):
    def thirdfunction():
        print("this text")
        print(someFunc()())
    return thirdfunction
check = wrapper(assignFunction)

check()
vari = blankFunction

vari = assignFunction()

print()

print(vari())


print(f"some text")