
def fizzBuzz(input, fizz = 3, buzz = 5):
    '''run a game of fizzBuzz with fizz as the first number and buzz as the second number'''
    output = ""
    if i % fizz == 0:
        output += "Fizz"
    if i % buzz == 0:
        output += "Buzz"
    if output == "":
        output = i
    return output

if __name__ == "__main__":
    for i in range(1,101):
        print(fizzBuzz(i))
