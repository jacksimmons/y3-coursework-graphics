class Logger:
    def __init__(self, infos: bool, warnings: bool, errors: bool):
        self.infos = infos
        self.warnings = warnings
        self.errors = errors
    
    
    def info(self, msg):
        if self.infos:
            print("(I) " + msg)
    
    
    def warning(self, msg):
        if self.warnings:
            print("(W) " + msg)
    
    
    def error(self, msg):
        if self.errors:
            input("(E) " + msg)
    
    
    def type_error(self, desired_type: str, value):
        self.error(f"Expected {desired_type}, got {type(value)}.\n{value}")
