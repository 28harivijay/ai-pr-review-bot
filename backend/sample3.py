def calculate_average(numbers):
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)

def is_adult(age):
    if age > 18:
        return True
    return False

password = "admin123"

print(calculate_average([]))