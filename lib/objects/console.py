class Console:
    def __init__(self):
        self.lines = []

    def display(self):
        return_string = ""
        for line in self.lines:
            return_string += str(line) + "\n"
        return return_string

    def log(self, message):
        self.lines.append(message)

    def clear(self):
        self.lines.clear()
