#!/usr/bin/env python3
# VDFParse.py - Valve Data Format parser
# A Python implementation matching the functionality of VDFParse.h

import os
import re


class VDFNode:
    """
    Represents a node in a VDF structure, which can be either a string value or an object (dictionary).
    """
    class Type:
        String = "string"
        Object = "object"
    
    def __init__(self, value=None):
        """Initialize a VDF node with either a string value or object (dict)"""
        if isinstance(value, dict):
            self.NodeType = self.Type.Object
            self.ObjectValue = value
            self.StringValue = ""
        else:
            self.NodeType = self.Type.String
            self.StringValue = str(value) if value is not None else ""
            self.ObjectValue = {}
    
    def IsString(self):
        """Check if the node is a string type"""
        return self.NodeType == self.Type.String
    
    def IsObject(self):
        """Check if the node is an object type"""
        return self.NodeType == self.Type.Object
    
    def AsString(self):
        """Get the string value, throws an error if not a string node"""
        if not self.IsString():
            raise RuntimeError("VDF value is not a string")
        return self.StringValue
    
    def GetObject(self):
        """Get the object value, throws an error if not an object node"""
        if not self.IsObject():
            raise RuntimeError("VDF value is not an object")
        return self.ObjectValue
    
    def SetValue(self, key, value):
        """Set a key-value pair in an object node"""
        if not self.IsObject():
            raise RuntimeError("Cannot set key on a string value")
        self.ObjectValue[key] = value
    
    def __getitem__(self, key):
        """Access a child node by key, returns None if not found or not an object"""
        if not self.IsObject():
            return None
        return self.ObjectValue.get(key)
    
    def __bool__(self):
        """Boolean check for emptiness"""
        if self.IsString():
            return bool(self.StringValue)
        else:
            return bool(self.ObjectValue)
    
    def ToString(self, indent=0):
        """Convert the node to a VDF string representation with proper indentation"""
        indent_str = ' ' * indent
        
        if self.IsString():
            return indent_str + f'"{self.StringValue}"'
        else:
            lines = [indent_str + "{"]
            
            for key, value in self.ObjectValue.items():
                lines.append(indent_str + f'  "{key}"')
                lines.append(value.ToString(indent + 2))
            
            lines.append(indent_str + "}")
            return "\n".join(lines)


class VDFValue:
    """
    A wrapper class for VDFNode that provides additional convenience methods
    and ensures null-safety.
    """
    def __init__(self, node=None):
        """Initialize with a node or create an empty object node if None"""
        self.Node = node if node is not None else VDFNode({})
    
    def __bool__(self):
        """Boolean check for existence and non-emptiness"""
        return bool(self.Node) if self.Node else False
    
    def __getitem__(self, key):
        """Access a child value by key, returns empty VDFValue if not found"""
        if not self.Node or not self.Node.IsObject():
            return VDFValue(None)
        
        child_node = self.Node[key]
        return VDFValue(child_node)
    
    def __str__(self):
        """String representation of the value"""
        if not self.Node or not self.Node.IsString():
            return ""
        return self.Node.AsString()
    
    def GetNode(self):
        """Get the underlying VDFNode"""
        return self.Node
    
    def ToString(self):
        """Convert to VDF string format"""
        if not self.Node:
            return "null"
        return self.Node.ToString()
    
    def IsNull(self):
        """Check if the value is null (has no node)"""
        return self.Node is None
    
    def IsString(self):
        """Check if the value contains a string node"""
        return self.Node and self.Node.IsString()
    
    def IsObject(self):
        """Check if the value contains an object node"""
        return self.Node and self.Node.IsObject()


class VDFParser:
    """
    Parser for Valve Data Format (VDF) files and strings.
    """
    @staticmethod
    def ParseFile(file_path):
        """Parse a VDF file at the given path"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return VDFParser.ParseString(f.read())
        except Exception as e:
            raise RuntimeError(f"Failed to open or parse file: {file_path} - {str(e)}")

    @staticmethod
    def ParseString(content):
        """Parse a VDF string into a VDFValue object"""
        pos = [0]  # Use list to allow modification in nested functions
        content_len = len(content)
        
        def SkipWhitespace():
            """Skip whitespace and comments"""
            while pos[0] < content_len:
                char = content[pos[0]]
                
                if char.isspace():
                    pos[0] += 1
                    continue
                
                if char == '/' and pos[0] + 1 < content_len and content[pos[0] + 1] == '/':
                    # Skip line comment
                    pos[0] += 2
                    while pos[0] < content_len and content[pos[0]] != '\n':
                        pos[0] += 1
                    continue
                
                break
        
        def ParseString():
            """Parse a string value, which may or may not be quoted"""
            SkipWhitespace()
            
            if pos[0] >= content_len:
                raise RuntimeError("Unexpected end of input while parsing string")
            
            is_quoted = content[pos[0]] == '"'
            if is_quoted:
                pos[0] += 1
            
            result = ""
            escaped = False
            
            while pos[0] < content_len:
                char = content[pos[0]]
                pos[0] += 1
                
                if escaped:
                    # Handle escape sequences
                    if char == 'n':
                        result += '\n'
                    elif char == 'r':
                        result += '\r'
                    elif char == 't':
                        result += '\t'
                    elif char == '\\':
                        result += '\\'
                    elif char == '"':
                        result += '"'
                    else:
                        result += char
                    escaped = False
                elif char == '\\':
                    escaped = True
                elif is_quoted and char == '"':
                    break
                elif not is_quoted and (char.isspace() or char == '{' or char == '}'):
                    pos[0] -= 1  # Put back the character
                    break
                else:
                    result += char
            
            if is_quoted and (pos[0] > content_len or content[pos[0] - 1] != '"'):
                raise RuntimeError("Unterminated string")
            
            return result
        
        def ParseValue():
            """Parse a value, which could be a string or an object"""
            SkipWhitespace()
            
            if pos[0] >= content_len:
                raise RuntimeError("Unexpected end of input")
            
            if content[pos[0]] == '{':
                return ParseObject()
            
            return VDFNode(ParseString())
        
        def ParseObject():
            """Parse an object (a collection of key-value pairs)"""
            obj = {}
            
            if content[pos[0]] != '{':
                raise RuntimeError(f"Expected '{{' at position {pos[0]}")
            pos[0] += 1
            
            SkipWhitespace()
            
            while pos[0] < content_len and content[pos[0]] != '}':
                key = ParseString()
                SkipWhitespace()
                
                value = ParseValue()
                obj[key] = value
                
                SkipWhitespace()
            
            if pos[0] >= content_len or content[pos[0]] != '}':
                raise RuntimeError(f"Expected '}}' at position {pos[0]}")
            pos[0] += 1
            
            return VDFNode(obj)
        
        # Start parsing
        root = VDFNode({})
        SkipWhitespace()
        
        while pos[0] < content_len:
            key = ParseString()
            if not key:
                break
            
            SkipWhitespace()
            value = ParseValue()
            
            root.SetValue(key, value)
            SkipWhitespace()
        
        return VDFValue(root)


def VDFParse(path):
    """
    Parse a VDF file or string, automatically detecting which one it is.
    If the input contains newlines or braces, it's treated as a string,
    otherwise as a file path.
    """
    if '\n' in path or '{' in path:
        return VDFParser.ParseString(path)
    else:
        return VDFParser.ParseFile(path)


def DebugPrint(value, indent=0):
    """
    Print a VDFValue or VDFNode for debugging purposes,
    with proper indentation and structure.
    """
    indent_str = ' ' * indent
    
    if value.IsNull():
        print(f"{indent_str}null")
        return
    
    if value.IsString():
        print(f"{indent_str}\"{value}\"")
    elif value.IsObject():
        print(f"{indent_str}{{")
        
        node = value.GetNode()
        if node:
            for key, val in node.GetObject().items():
                print(f"{indent_str}  \"{key}\"")
                DebugPrint(VDFValue(val), indent + 4)
        
        print(f"{indent_str}}}")


# Additional compatibility functions for the existing code
def FindAppInfoBlock(output):
    """Find app info block in steamcmd output"""
    lines = output.split('\n')
    app_id_line = None
    app_id = None
    
    # Find the start of the AppID section and extract the app id
    for i, line in enumerate(lines):
        if 'AppID : ' in line:
            parts = line.split(',')[0].strip()
            try:
                app_id = parts.split(':')[1].strip()
                app_id_line = i
                break
            except:
                pass
    
    if app_id_line is None or app_id is None:
        return None
    
    # Extract the VDF content
    vdf_lines = []
    brace_count = 0
    start_found = False
    
    for i in range(app_id_line + 1, len(lines)):
        line = lines[i].strip()
        
        quoted_app_id = f'"{app_id}"'
        if not start_found and line == quoted_app_id:
            start_found = True
            vdf_lines.append(line)
        elif not start_found and line == f'{quoted_app_id} {{':
            start_found = True
            vdf_lines.append(quoted_app_id)
            vdf_lines.append('{')
            brace_count = 1
        elif start_found:
            vdf_lines.append(line)
            if '{' in line and '}' not in line:
                brace_count += line.count('{')
            if '}' in line:
                brace_count -= line.count('}')
                if brace_count == 0:
                    break
    
    return '\n'.join(vdf_lines)


def ParseSteamCmdOutput(output):
    """Extract and parse the app block from steamcmd output"""
    app_block = FindAppInfoBlock(output)
    if not app_block:
        print("DEBUG: Failed to extract app block. Full output saved to debug_output.txt")
        with open("debug_output.txt", "w", encoding="utf-8") as debug_file:
            debug_file.write(output)
        return None
    
    with open("raw_vdf.txt", "w", encoding="utf-8") as vdf_file:
        vdf_file.write(app_block)
    
    try:
        parsed_data = VDFParse(app_block)
        # Convert to a dict for compatibility with existing code
        return ConvertVDFToDict(parsed_data)
    except Exception as error:
        print(f"Parser failed: {str(error)}")
        return None


def ConvertVDFToDict(vdf_value):
    """Convert a VDFValue to a regular Python dictionary structure"""
    if vdf_value.IsNull():
        return None
    
    if vdf_value.IsString():
        return str(vdf_value)
    
    if vdf_value.IsObject():
        result = {}
        node = vdf_value.GetNode()
        
        for key, val in node.GetObject().items():
            if val.IsString():
                result[key] = val.AsString()
            else:
                result[key] = ConvertVDFToDict(VDFValue(val))
        
        return result
    
    return None


def FindAppId(output):
    """Extract AppID from steamcmd output"""
    for line in output.split('\n'):
        if 'AppID : ' in line:
            try:
                app_id = line.split(':')[1].strip().split(',')[0].strip()
                return app_id
            except:
                pass
    return "740"  # Default to CSGO


def FindManifestInfo(app_data):
    """Extract manifest info from parsed app data"""
    app_id = None
    for key in app_data:
        if isinstance(key, str) and key.isdigit():
            app_id = key
            break
    
    if not app_id:
        return None
    
    app_content = app_data[app_id]
    
    if 'depots' not in app_content:
        return None
    
    depots = app_content['depots']
    
    # Find manifest info in any depot
    for depot_id, depot_info in depots.items():
        if depot_id != "branches" and isinstance(depot_info, dict) and "manifests" in depot_info:
            if "public" in depot_info["manifests"]:
                return {
                    "depot_id": depot_id,
                    "app_id": app_id,
                    **depot_info["manifests"]["public"]
                }
    
    # Fall back to branch info
    if 'branches' in depots and 'public' in depots['branches']:
        return {
            "app_id": app_id,
            **depots['branches']['public']
        }
    
    return None


def UltimateVdfBlockExtractor(output):
    """Last resort VDF block extractor when other methods fail"""
    # Find any app ID pattern like "123456" {
    match = re.search(r'"(\d+)"\s*\n\s*{', output)
    if not match:
        return None
    
    app_id = match.group(1)
    start_pos = match.start()
    
    # Extract everything from this position to the matching closing brace
    content_from_match = output[start_pos:]
    brace_count = 0
    end_pos = 0
    
    for i, c in enumerate(content_from_match):
        if c == '{':
            brace_count += 1
        elif c == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = i + 1
                break
    
    if end_pos > 0:
        return content_from_match[:end_pos]
    
    return None


# Test function
if __name__ == "__main__":
    # Simple test
    test_vdf = '''
    "740"
    {
        "common"
        {
                "name"          "CS:GO - DS"
                "type"          "Tool"
        }
        "depots"
        {
                "branches"
                {
                        "public"
                        {
                                "buildid"       "12345678"
                                "timeupdated"   "1621234567"
                        }
                }
        }
    }
    '''
    
    result = VDFParse(test_vdf)
    print("Parsed VDF structure:")
    DebugPrint(result)
    
    # Convert to dict
    dict_result = ConvertVDFToDict(result)
    print("\nConverted to dictionary:")
    import json
    print(json.dumps(dict_result, indent=2))
    
    # Test manifest extraction
    manifest = FindManifestInfo(dict_result)
    if manifest:
        print("\nExtracted manifest info:")
        print(json.dumps(manifest, indent=2))
    else:
        print("\nNo manifest info found")
