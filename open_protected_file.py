import subprocess
import os

protected_file = "something.txt"

print("🔐 Gesture Authentication Required")

# Run authentication program
result = subprocess.run(["python", "gestolocks.py"])

# If authentication successful
if result.returncode == 0:

    if os.path.exists(protected_file):
        print("📂 Opening protected file...")
        os.startfile(protected_file)
    else:
        print("❌ File not found")

else:

    print("🚫 Authentication Failed. File will not open.")