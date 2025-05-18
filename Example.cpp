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
