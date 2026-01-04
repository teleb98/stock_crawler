import OpenDartReader
import inspect

api_key = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"
dart = OpenDartReader(api_key)

print("--- finstate doc ---")
print(inspect.getdoc(dart.finstate))

print("\n--- finstate_all doc ---")
print(inspect.getdoc(dart.finstate_all))
