import random
def EV_mini(a: int, b: int)-> int:
    while b:
        a, b = b, a % b
        return a

#здесь будем искать обратное по модулю число 
def EV_big(e: int, foo: int) -> int:
    


    