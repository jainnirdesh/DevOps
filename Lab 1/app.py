def greet(name):
    return f"Hello, {name}!"


def farewell(name):
    return f"Goodbye, {name}!"


def shout(message):
    return message.upper()


if __name__ == "__main__":
    print(greet("DevOps"))
    print(farewell("DevOps"))
    print(shout("DevOps automation"))
