class Logger:
    """A simple logging class to simplify messages to the console."""
    def __init__(self, infos: bool, warnings: bool, errors: bool):
        self.infos = infos
        self.warnings = warnings
        self.errors = errors
    
    
    def info(self, msg):
        if self.infos:
            print("(I) " + str(msg))
    
    
    def warning(self, msg):
        if self.warnings:
            print("(W) " + str(msg))
    
    
    def error(self, msg):
        if self.errors:
            input("(E) " + str(msg))
    
    
    def type_error(self, desired_type: str, value):
        self.error(f"Expected {desired_type}, got {type(value)}.\n{value}")
