# VDFParse

**VDFParse** is a lightweight, single-header C++ parser for Valve's KeyValue (VDF/ACF/VCF) formatted files. It reads `.acf`, `.vdf`, `.vcf`, and similar files used by Steam and parses them into a JSON-like C++ data structure for easy access and manipulation.

## Features

- 📄 Single-header, zero-dependency library  
- 🧠 Parses Steam VDF, ACF, VCF files  
- 🔄 Outputs data in a structured, JSON-like format  
- 🧪 Input from file path or raw string  
- 🛠️ Simple API with exception handling  

## Example Usage

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

### Parsing from a String

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

## Getting Started

1. **Include the header:**

   Copy `VDFParse.h` into your project and include it:

   ```cpp
   #include "VDFParse.h"
   ```

2. **Compile your project:**

   This is a header-only library; no linking required.

## API

```cpp
SteamVDF::VDFParse(path_or_string);
```

- Accepts either a file path (`std::string`) or raw VDF text as input.
- Returns a nested structure (e.g., `std::map<std::string, std::any>` depending on your implementation).
- Throws `std::runtime_error` on parsing errors.

## License

MIT License – free for personal and commercial use.

## Contribution

Feel free to open issues or submit pull requests. Suggestions and improvements are welcome!
