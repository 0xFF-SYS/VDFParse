#!/usr/bin/env python3
# Example.py - Demonstration of VDFParse Python library

from VDFParse import VDFParse
import json

def main():
    try:
        data = VDFParse("C:\\Program Files (x86)\\Steam\\steamapps\\appmanifest_252490.acf")
        appstate = data["AppState"]

        app_id = appstate["appid"]
        name = appstate["name"]
        last_updated = appstate["lastupdated"]
        size_on_disk = appstate["SizeOnDisk"]
        last_played = appstate["LastPlayed"]
        build_id = appstate["buildid"]
        last_owner = appstate["LastOwner"]
        
        print(f"AppID: {app_id}")
        print(f"Name: {name}")
        print(f"Last Updated: {last_updated}")
        print(f"Size On Disk: {size_on_disk}")
        print(f"Last Played: {last_played}")
        print(f"Build ID: {build_id}")
        print(f"Last Owner: {last_owner}")
        
        # This can also be used with steamcmd
        vdf_text = """
        "AppState"
        {
            "appid" "252490"
            "name" "Rust"
        }
        """
        string_data = VDFParse(vdf_text)
        
        print("\nParsed VDF as dictionary:")
        from VDFParse import ConvertVDFToDict
        dict_data = ConvertVDFToDict(string_data)
        print(json.dumps(dict_data, indent=2))
        
    except RuntimeError as e:
        print(f"Exception: {str(e)}")

if __name__ == "__main__":
    main()
