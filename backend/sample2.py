import sqlite3

def get_average(numbers):
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)

def find_user(db, username):
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    return db.execute(query).fetchall()

def add_item(item, items=[]):
    items.append(item)
    return items

def read_config(path):
    f = open(path)
    data = f.read()
    return data

def safe_divide(a, b):
    try:
        return a / b
    except:
        pass

print(get_average([]))