import simplearith as sa

print("add:", sa.add(2, 3))
print("subtract:", sa.subtract(10, 3))
print("multiply:", sa.multiply(6, 7))
print("divide:", sa.divide(10, 4))
print("dot:", sa.dot([1, 2, 3], [4, 5, 6]))
print("vector_add:", sa.vector_add([1, 2, 3], [10, 20, 30]))

try:
    sa.divide(1, 0)
except ZeroDivisionError as exc:
    print("divide by zero:", exc)
