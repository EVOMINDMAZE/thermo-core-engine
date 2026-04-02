import subprocess
import sys

print(sys.executable)
result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_e2e.py"], capture_output=True, text=True)
print("STDOUT:")
print(result.stdout)
print("STDERR:")
print(result.stderr)
print("Exit code:", result.returncode)
