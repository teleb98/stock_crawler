import OpenDartReader
import inspect

api_key = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"
dart = OpenDartReader(api_key)

print("Methods in OpenDartReader:")
methods = [m for m in dir(dart) if not m.startswith('_')]
for m in methods:
    print(f"- {m}")

# Check for terms like 'all' or 'bulk'
print("\nPossible bulk methods:")
for m in methods:
    if 'all' in m or 'list' in m:
        print(f" -> {m}")
