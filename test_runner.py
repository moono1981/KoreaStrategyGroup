import subprocess
import sys

result = subprocess.run(
    [sys.executable, "ksg_procurement.py", "--to", "test@example.com"],
    cwd=r"d:\Claude_VSCode_20260618\KCG\KoreaStrategyGroup",
    capture_output=True,
    text=True
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print("Return code:", result.returncode)
