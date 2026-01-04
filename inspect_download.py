import OpenDartReader
import inspect

api_key = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"
dart = OpenDartReader(api_key)

print("--- download doc ---")
print(inspect.getdoc(dart.download))

print("\n--- extract of signature ---")
print(inspect.signature(dart.download))
