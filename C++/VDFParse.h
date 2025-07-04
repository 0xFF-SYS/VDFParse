#ifndef STEAM_VDF_PARSER_H
#define STEAM_VDF_PARSER_H

#include <string>
#include <map>
#include <vector>
#include <fstream>
#include <sstream>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <cctype>

namespace SteamVDF {

    class VDFNode;
    using VDFNodePtr = std::shared_ptr<VDFNode>;

    class VDFNode {
    public:
        enum class Type {
            String,
            Object
        };

        VDFNode() : NodeType(Type::Object), ObjectValue({}) {}
        explicit VDFNode(const std::string& Value) : NodeType(Type::String), StringValue(Value) {}
        explicit VDFNode(const std::map<std::string, VDFNodePtr>& Value) : NodeType(Type::Object), ObjectValue(Value) {}

        bool IsString() const { return NodeType == Type::String; }
        bool IsObject() const { return NodeType == Type::Object; }

        const std::string& AsString() const {
            if (!IsString()) throw std::runtime_error("VDF value is not a string");
            return StringValue;
        }

        const std::map<std::string, VDFNodePtr>& GetObject() const {
            if (!IsObject()) throw std::runtime_error("VDF value is not an object");
            return ObjectValue;
        }

        void SetValue(const std::string& Key, VDFNodePtr Value) {
            if (!IsObject()) throw std::runtime_error("Cannot set key on a string value");
            ObjectValue[Key] = Value;
        }

        VDFNodePtr operator[](const std::string& Key) const {
            if (!IsObject()) return nullptr;
            auto It = ObjectValue.find(Key);
            if (It == ObjectValue.end()) return nullptr;
            return It->second;
        }

        VDFNodePtr operator[](const char* Key) const {
            return (*this)[std::string(Key)];
        }

        operator bool() const {
            return !((IsString() && StringValue.empty()) ||
                (IsObject() && ObjectValue.empty()));
        }

        std::string ToString(int Indent = 0) const {
            std::string IndentStr(Indent, ' ');

            if (IsString()) {
                return IndentStr + "\"" + StringValue + "\"";
            }
            else {
                std::ostringstream Oss;
                Oss << IndentStr << "{\n";

                for (const auto& Pair : ObjectValue) {
                    Oss << IndentStr << "  \"" << Pair.first << "\"\n";
                    Oss << Pair.second->ToString(Indent + 2) << "\n";
                }

                Oss << IndentStr << "}";
                return Oss.str();
            }
        }

    private:
        Type NodeType;
        std::string StringValue;
        std::map<std::string, VDFNodePtr> ObjectValue;
    };

    class VDFValue {
    public:
        VDFValue() : Node(std::make_shared<VDFNode>()) {}
        VDFValue(VDFNodePtr NodePtr) : Node(NodePtr ? NodePtr : std::make_shared<VDFNode>()) {}

        operator bool() const {
            return Node && (*Node);
        }

        VDFValue operator[](const std::string& Key) const {
            if (!Node || !Node->IsObject()) return VDFValue(nullptr);
            return VDFValue((*Node)[Key]);
        }

        VDFValue operator[](const char* Key) const {
            return (*this)[std::string(Key)];
        }

        operator std::string() const {
            if (!Node || !Node->IsString()) return "";
            return Node->AsString();
        }

        operator const char* () const {
            static std::string EmptyStr;
            if (!Node || !Node->IsString()) return EmptyStr.c_str();
            return Node->AsString().c_str();
        }

        VDFNodePtr GetNode() const {
            return Node;
        }

        std::string ToString() const {
            if (!Node) return "null";
            std::string str = Node->ToString();

            if (!str.empty() && str.front() == '"' && str.back() == '"') {
                str = str.substr(1, str.size() - 2);
            }
            return str;
        }

        bool IsNull() const {
            return !Node;
        }

        bool IsString() const {
            return Node && Node->IsString();
        }

        bool IsObject() const {
            return Node && Node->IsObject();
        }

        friend std::ostream& operator<<(std::ostream& os, const VDFValue& Value) {
            if (!Value.Node) {
                os << "null";
            }
            else if (Value.Node->IsString()) {
                os << Value.Node->AsString();
            }
            else {
                os << "[VDF Object]";
            }
            return os;
        }

    private:
        VDFNodePtr Node;
    };

    class VDFParser {
    public:
        static VDFValue ParseFile(const std::string& FilePath) {
            std::ifstream File(FilePath);
            if (!File.is_open()) {
                throw std::runtime_error("Failed to open file: " + FilePath);
            }

            std::stringstream Buffer;
            Buffer << File.rdbuf();
            return ParseString(Buffer.str());
        }

        static VDFValue ParseString(const std::string& Content) {
            size_t Pos = 0;
            VDFNodePtr Root = std::make_shared<VDFNode>();

            SkipWhitespace(Content, Pos);

            while (Pos < Content.length()) {
                std::string Key = ParseString(Content, Pos);
                SkipWhitespace(Content, Pos);

                VDFNodePtr Value = ParseValue(Content, Pos);
                Root->SetValue(Key, Value);

                SkipWhitespace(Content, Pos);
            }

            return VDFValue(Root);
        }

    private:
        static VDFNodePtr ParseValue(const std::string& Content, size_t& Pos) {
            SkipWhitespace(Content, Pos);

            if (Pos >= Content.length()) {
                throw std::runtime_error("Unexpected end of input");
            }

            if (Content[Pos] == '{') {
                return ParseObject(Content, Pos);
            }

            return std::make_shared<VDFNode>(ParseString(Content, Pos));
        }

        static VDFNodePtr ParseObject(const std::string& Content, size_t& Pos) {
            std::map<std::string, VDFNodePtr> Obj;

            if (Content[Pos] != '{') {
                throw std::runtime_error("Expected '{' at position " + std::to_string(Pos));
            }
            Pos++;

            SkipWhitespace(Content, Pos);

            while (Pos < Content.length() && Content[Pos] != '}') {
                std::string Key = ParseString(Content, Pos);

                SkipWhitespace(Content, Pos);
                VDFNodePtr Value = ParseValue(Content, Pos);

                Obj[Key] = Value;

                SkipWhitespace(Content, Pos);
            }

            if (Pos >= Content.length() || Content[Pos] != '}') {
                throw std::runtime_error("Expected '}' at position " + std::to_string(Pos));
            }
            Pos++;

            return std::make_shared<VDFNode>(Obj);
        }

        static std::string ParseString(const std::string& Content, size_t& Pos) {
            SkipWhitespace(Content, Pos);

            if (Pos >= Content.length()) {
                throw std::runtime_error("Unexpected end of input while parsing string");
            }

            bool IsQuoted = (Content[Pos] == '"');
            if (IsQuoted) Pos++;

            std::string Result;
            bool Escaped = false;

            while (Pos < Content.length()) {
                char C = Content[Pos++];

                if (Escaped) {
                    switch (C) {
                    case 'n': Result += '\n'; break;
                    case 'r': Result += '\r'; break;
                    case 't': Result += '\t'; break;
                    case '\\': Result += '\\'; break;
                    case '"': Result += '"'; break;
                    default: Result += C; break;
                    }
                    Escaped = false;
                }
                else if (C == '\\') {
                    Escaped = true;
                }
                else if (IsQuoted && C == '"') {
                    break;
                }
                else if (!IsQuoted && (C == '\r' || C == '\n' || C == '\t' || C == ' ' || C == '{' || C == '}')) {
                    Pos--;
                    break;
                }
                else {
                    Result += C;
                }
            }

            if (IsQuoted && (Pos > Content.length() || Content[Pos - 1] != '"')) {
                throw std::runtime_error("Unterminated string starting at position " + std::to_string(Pos));
            }

            return Result;
        }

        static void SkipWhitespace(const std::string& Content, size_t& Pos) {
            while (Pos < Content.length()) {
                char C = Content[Pos];

                if (std::isspace(C)) {
                    Pos++;
                    continue;
                }

                if (C == '/' && Pos + 1 < Content.length() && Content[Pos + 1] == '/') {
                    Pos += 2;
                    while (Pos < Content.length() && Content[Pos] != '\n') {
                        Pos++;
                    }
                    continue;
                }

                break;
            }
        }
    };

    inline VDFValue VDFParse(const std::string& Path) {
        if (Path.find('\n') != std::string::npos) {
            return VDFParser::ParseString(Path);
        }
        else {
            return VDFParser::ParseFile(Path);
        }
    }

    inline void DebugPrint(const VDFValue& Value, int Indent = 0) {
        if (!Value || Value.IsNull()) {
            std::cout << std::string(Indent, ' ') << "null" << std::endl;
            return;
        }

        if (Value.IsString()) {
            std::cout << std::string(Indent, ' ') << "\"" << Value << "\"" << std::endl;
        }
        else if (Value.IsObject()) {
            std::cout << std::string(Indent, ' ') << "{" << std::endl;

            auto NodePtr = Value.GetNode();
            if (NodePtr) {
                for (const auto& Pair : NodePtr->GetObject()) {
                    std::cout << std::string(Indent + 2, ' ') << "\"" << Pair.first << "\"" << std::endl;
                    DebugPrint(VDFValue(Pair.second), Indent + 4);
                }
            }

            std::cout << std::string(Indent, ' ') << "}" << std::endl;
        }
    }

}

#endif
