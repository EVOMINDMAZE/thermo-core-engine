import subprocess
import sys

print(sys.executable)
result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_anomaly.py"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
print("Exit code:", result.returncode)
