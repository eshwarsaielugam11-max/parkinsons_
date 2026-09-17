import sys
import platform
import fastapi
import sqlalchemy
import anthropic

print("Python Executable:", sys.executable)
print("Architecture:", platform.machine())
print("FastAPI version:", fastapi.__version__)
print("SQLAlchemy version:", sqlalchemy.__version__)
print("Anthropic version:", anthropic.__version__)

if sys.executable == "/usr/bin/python3":
    print("FAILED: Running under system python.")
    sys.exit(1)
elif platform.machine() != "arm64":
    print(f"FAILED: Architecture is {platform.machine()} instead of arm64.")
    sys.exit(1)
else:
    print("SUCCESS: Environment is isolated and ARM64-native.")
    sys.exit(0)
