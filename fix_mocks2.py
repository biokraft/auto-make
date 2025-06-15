#!/usr/bin/env python3

# Read the test file
with open("tests/test_main.py") as f:
    lines = f.readlines()

# Line numbers where we need to add the mock (0-indexed, so subtract 1)
line_numbers = [129, 217, 254, 296, 340, 377, 420]

# Process from the end to avoid shifting line numbers
for line_num in reversed(line_numbers):
    # Insert the mock run method after the mock_runner_instance line
    indent = "                "  # Same indentation as the original line
    new_line = f"{indent}mock_runner_instance.run = MagicMock(return_value=None)"
    "# Mock the run method\n"
    lines.insert(line_num, new_line)

# Write back to the file
with open("tests/test_main.py", "w") as f:
    f.writelines(lines)

print("Added run method mocks to test_main.py")
