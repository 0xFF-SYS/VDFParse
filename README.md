# VDFParse

**VDFParse** is available as both a lightweight, single-header C++ parser and a Python module for Valve's KeyValue (VDF/ACF/VCF) formatted files. It reads `.acf`, `.vdf`, `.vcf`, and similar files used by Steam and parses them into a structured data format for easy access and manipulation.

## Features

- 📄 Available as a single-header C++ library and a Python module
- 🧠 Parses Steam VDF, ACF, VCF files  
- 🔄 Outputs data in a structured, JSON-like format  
- 🧪 Input from file path or raw string  
- 🛠️ Simple API with exception handling
- 🐍 Python implementation with similar API to C++

## Example Usage

### C++ Usage

```cpp
#include "VDFParse.h"
#include <iostream>

int main() {
    try {
        auto Data = SteamVDF::VDFParse("C:\\Program Files (x86)\\Steam\\steamapps\\appmanifest_252490.acf");
        auto AppState = Data["AppState"];
        auto AppID = AppState["appid"];
        auto Name = AppState["name"];
        auto LastUpdated = AppState["lastupdated"];
        auto SizeOnDisk = AppState["SizeOnDisk"];
        auto LastPlayed = AppState["LastPlayed"];
        auto BuildID = AppState["buildid"];
        auto LastOwner = AppState["LastOwner"];

        std::cout << "AppID: " << AppID << std::endl;
        std::cout << "Name: " << Name << std::endl;
        std::cout << "Last Updated: " << LastUpdated << std::endl;
        std::cout << "Size On Disk: " << SizeOnDisk << std::endl;
        std::cout << "Last Played: " << LastPlayed << std::endl;
        std::cout << "Build ID: " << BuildID << std::endl;
        std::cout << "Last Owner: " << LastOwner << std::endl;
    }
    catch (const std::exception& e) {
        std::cout << "Exception: " << e.what() << std::endl;
    }

    return 0;
}
```

#### Parsing from a String in C++

```cpp
std::string vdfText = R"
"AppState"
{
    "appid" "252490"
    "name" "Rust"
}
";

auto Data = SteamVDF::VDFParse(vdfText);
```

### Python Usage

```python
from VDFParse import VDFParse

def main():
    try:
        data = VDFParse("C:\\Program Files (x86)\\Steam\\steamapps\\appmanifest_252490.acf")
        app_state = data["AppState"]
        
        app_id = app_state["appid"]
        name = app_state["name"]
        last_updated = app_state["lastupdated"]
        size_on_disk = app_state["SizeOnDisk"]
        
        print(f"AppID: {app_id}")
        print(f"Name: {name}")
        print(f"Last Updated: {last_updated}")
        print(f"Size On Disk: {size_on_disk}")
    except RuntimeError as e:
        print(f"Exception: {str(e)}")

if __name__ == "__main__":
    main()
```

#### Parsing from a String in Python

```python
vdf_text = """
"AppState"
{
    "appid" "252490"
    "name" "Rust"
}
"""

data = VDFParse(vdf_text)
```

#### Converting to Python Dictionary

```python
from VDFParse import VDFParse, ConvertVDFToDict
import json

data = VDFParse(vdf_text)
dict_data = ConvertVDFToDict(data)
print(json.dumps(dict_data, indent=2))
```

## Getting Started

### C++

1. **Include the header:**

   Copy `VDFParse.h` into your project and include it:

   ```cpp
   #include "VDFParse.h"
   ```

2. **Compile your project:**

   This is a header-only library; no linking required.

### Python

1. **Use the Python module:**
   Either run ```python
   pip install vdfparse
   ``` or
   Copy `VDFParse.py` into your project and import it:

   ```python
   from VDFParse import VDFParse, VDFValue, ConvertVDFToDict
   ```

2. **Run your script:**

   No additional installation required, just make sure `VDFParse.py` is in your project directory or Python path.



## API

### C++ API

```cpp
SteamVDF::VDFParse(path_or_string);
```

- Accepts either a file path (`std::string`) or raw VDF text as input.
- Returns a nested structure that can be accessed with operator[].
- Throws `std::runtime_error` on parsing errors.

### Python API

```python
VDFParse(path_or_string)
```

- Accepts either a file path (`str`) or raw VDF text as input.
- Returns a `VDFValue` object that can be accessed with dictionary-like syntax.
- Throws `RuntimeError` on parsing errors.

Additional Python Utility Functions:

```python
ConvertVDFToDict(vdf_value)  # Convert VDFValue to a Python dictionary
ParseSteamCmdOutput(output)  # Parses steamCMD output
DebugPrint(vdf_value)        # Print a VDFValue for debugging
```

## License

MIT License – free for personal and commercial use.

## Contribution

Feel free to open issues or submit pull requests. Suggestions and improvements are welcome!
