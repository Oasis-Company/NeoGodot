class_name CodeFormatter

const INDENT_SIZE := 4
const INDENT_CHAR := " "

var _keywords := ["extends", "class_name", "func", "var", "const", "enum", 
	"signal", "class", "static", "enum", "match", "case", "if", "elif", 
	"else", "for", "while", "do", "break", "continue", "return", "pass",
	"yield", "await", "assert", "rem", "and", "or", "not", "in", "is",
	"true", "false", "null", "self", "tool", "remote", "master", 
	"puppet", "remotesync", "puppetsync", "sync", "remote", "static",
	"virtual", "override"]

func format_gdscript(script: String) -> String:
	var lines := script.split("\n")
	var formatted_lines: Array[String] = []
	var indent_level := 0
	var in_string := false
	var string_char := ""
	var in_multiline_comment := false
	var previous_line_was_content := false
	
	for raw_line in lines:
		var line := raw_line
		
		if line.strip_edges().is_empty():
			if previous_line_was_content and formatted_lines.size() > 0:
				formatted_lines.append("")
			previous_line_was_content = false
			continue
		
		previous_line_was_content = true
		
		line = _remove_trailing_whitespace(line)
		
		if line.strip_edges().begins_with("\"\"\""):
			in_multiline_comment = not in_multiline_comment
		
		if not in_multiline_comment:
			line = _process_indentation(line, indent_level)
			indent_level = _calculate_next_indent(line, indent_level)
		else:
			var indent := INDENT_CHAR.repeat(indent_level * INDENT_SIZE)
			line = indent + line.strip_edges()
		
		formatted_lines.append(line)
	
	var result := "\n".join(formatted_lines)
	result = _normalize_blank_lines(result)
	result = _align_comments(result)
	
	return result.strip_edges() + "\n"

func _remove_trailing_whitespace(line: String) -> String:
	var end := line.length()
	while end > 0 and (line[end - 1] == " " or line[end - 1] == "\t"):
		end -= 1
	return line.substr(0, end)

func _process_indentation(line: String, indent_level: int) -> String:
	var stripped := line.strip_edges(true, false)
	
	if stripped.is_empty():
		return ""
	
	var indent := INDENT_CHAR.repeat(indent_level * INDENT_SIZE)
	
	return indent + stripped

func _calculate_next_indent(line: String, current_indent: int) -> int:
	var stripped := line.strip_edges()
	
	if stripped.begins_with("}"):
		return max(0, current_indent - 1)
	
	if stripped.ends_with(":") or stripped.ends_with("{"):
		return current_indent + 1
	
	return current_indent

func _normalize_blank_lines(script: String) -> String:
	var lines := script.split("\n")
	var result_lines: Array[String] = []
	var empty_count := 0
	
	for line in lines:
		if line.strip_edges().is_empty():
			empty_count += 1
			if empty_count <= 1:
				result_lines.append("")
		else:
			empty_count = 0
			result_lines.append(line)
	
	while result_lines.size() > 0 and result_lines[-1].strip_edges().is_empty():
		result_lines.pop_back()
	
	return "\n".join(result_lines)

func _align_comments(script: String) -> String:
	var lines := script.split("\n")
	var result_lines: Array[String] = []
	var max_code_width := 0
	
	for line in lines:
		var stripped := line.strip_edges()
		if stripped.is_empty():
			continue
		
		var code_end := -1
		for i in range(line.length() - 1, -1, -1):
			if line[i] == "#":
				code_end = i
				break
		
		if code_end > 0:
			var code_part := line.substr(0, code_end).strip_edges()
			max_code_width = max(max_code_width, code_part.length())
	
	for line in lines:
		var stripped := line.strip_edges()
		if stripped.is_empty():
			result_lines.append("")
			continue
		
		var code_end := -1
		for i in range(line.length() - 1, -1, -1):
			if line[i] == "#":
				code_end = i
				break
		
		if code_end > 0:
			var leading_spaces := line.length() - line.lstrip().length()
			var code_part := line.substr(0, code_end).strip_edges()
			var comment_part := line.substr(code_end).strip_edges()
			var padded_code := code_part + " ".repeat(max_code_width - code_part.length() + 2)
			result_lines.append(" ".repeat(leading_spaces) + padded_code + comment_part)
		else:
			result_lines.append(line)
	
	return "\n".join(result_lines)

func validate_syntax(script: String) -> bool:
	if script.is_empty():
		return true
	
	var bracket_count := 0
	var paren_count := 0
	var brace_count := 0
	
	var in_string := false
	var string_char := ""
	var in_multiline_comment := false
	var in_single_line_comment := false
	
	var lines := script.split("\n")
	
	for line in lines:
		var i := 0
		while i < line.length():
			var char := line[i]
			
			if in_single_line_comment:
				break
			
			if in_multiline_comment:
				if i + 2 < line.length() and line.substr(i, 3) == "\"\"\"":
					in_multiline_comment = false
					i += 3
					continue
				i += 1
				continue
			
			if in_string:
				if char == "\\" and i + 1 < line.length():
					i += 2
					continue
				if char == string_char:
					in_string = false
				i += 1
				continue
			
			match char:
				"\"":
					if i + 2 < line.length() and line.substr(i, 3) == "\"\"\"":
						in_multiline_comment = true
						i += 3
					else:
						in_string = true
						string_char = "\""
						i += 1
				"#":
					in_single_line_comment = true
					i += 1
				"(":
					paren_count += 1
					i += 1
				")":
					paren_count -= 1
					if paren_count < 0:
						return false
					i += 1
				"{":
					brace_count += 1
					i += 1
				"}":
					brace_count -= 1
					if brace_count < 0:
						return false
					i += 1
				"[":
					bracket_count += 1
					i += 1
				"]":
					bracket_count -= 1
					if bracket_count < 0:
						return false
					i += 1
				_:
					i += 1
		
		in_single_line_comment = false
	
	if bracket_count != 0 or paren_count != 0 or brace_count != 0:
		return false
	
	if not _validate_keywords(script):
		return false
	
	return true

func _validate_keywords(script: String) -> bool:
	var pattern := RegEx.new()
	
	var keyword_regex := "^\\s*(" + "|".join(_keywords) + ")\\b"
	
	if pattern.compile(keyword_regex) != OK:
		return true
	
	var lines := script.split("\n")
	for line in lines:
		var stripped := line.strip_edges()
		if stripped.is_empty() or stripped.begins_with("#"):
			continue
		
		for keyword in _keywords:
			var escaped := "^\\s*" + keyword + "\\b.*"
			pattern.compile(escaped)
			if pattern.search(stripped):
				var correct_keyword := keyword
				var found := stripped.strip_edges()
				if not found.begins_with(correct_keyword):
					var test_pattern := RegEx.new()
					test_pattern.compile("[a-z_]+")
					var results := test_pattern.search_all(found)
					if results.size() > 0:
						var first_word := results[0].get_string()
						if first_word != correct_keyword and first_word.to_lower() != correct_keyword.to_lower():
							continue
	
	return true
