extends RefCounted
class_name ScriptGenerator

enum TemplateType {
	EMPTY,
	CHARACTER,
	NODE,
	AUTOLOAD,
	EDITOR_PLUGIN,
	CUSTOM
}

signal generation_started(prompt: String, template_type: int)
signal generation_progress(message: String, progress: float)
signal generation_complete(script_content: String, class_name: String)
signal generation_error(error_message: String, error_details: String)

var _template_engine: TemplateEngine
var _code_formatter: CodeFormatter

func _init() -> void:
	_template_engine = TemplateEngine.new()
	_code_formatter = CodeFormatter.new()

func generate(prompt: String, template_type: int, class_name: String) -> String:
	generation_started.emit(prompt, template_type)
	
	generation_progress.emit("分析请求...", 0.1)
	
	var template_content := _get_template_for_type(template_type)
	var generated_content: String
	
	if prompt.is_empty() and template_content.is_empty():
		generated_content = _generate_empty_script(class_name)
	elif prompt.is_empty() and not template_content.is_empty():
		generated_content = template_content
	else:
		generation_progress.emit("调用 AI 运行时...", 0.3)
		generated_content = await _call_ai_runtime(prompt, template_type, class_name)
	
	generation_progress.emit("格式化代码...", 0.8)
	var formatted_script := _format_script(generated_content)
	
	generation_progress.emit("完成生成", 1.0)
	generation_complete.emit(formatted_script, class_name)
	
	return formatted_script

func generate_from_template(template_path: String, context: Dictionary) -> String:
	generation_started.emit("从模板生成: " + template_path, TemplateType.CUSTOM)
	
	generation_progress.emit("加载模板...", 0.2)
	var template_content := _template_engine.load_template(template_path)
	
	if template_content.is_empty():
		var error_msg := "无法加载模板: " + template_path
		generation_error.emit(error_msg, "Template file not found or empty")
		return ""
	
	generation_progress.emit("渲染模板...", 0.5)
	var rendered := _template_engine.render(template_content, context)
	
	generation_progress.emit("格式化代码...", 0.8)
	var formatted := _format_script(rendered)
	
	generation_complete.emit(formatted, context.get("class_name", "CustomScript"))
	
	return formatted

func _format_script(script_content: String) -> String:
	var lines := script_content.split("\n")
	var formatted_lines: Array[String] = []
	var indent_level := 0
	var in_multiline_comment := false
	var previous_was_empty := false
	
	for line in lines:
		var processed_line := line
		if processed_line.strip_edges().is_empty():
			if not previous_was_empty and formatted_lines.size() > 0:
				formatted_lines.append("")
			previous_was_empty = true
			continue
		
		previous_was_empty = false
		var stripped := processed_line.strip_edges(false, true)
		
		if stripped.begins_with("\"\"\""):
			in_multiline_comment = not in_multiline_comment
		
		var indent := "    ".repeat(indent_level)
		var dedented := processed_line.strip_edges(true, false)
		
		if not in_multiline_comment:
			if dedented.ends_with("{") or dedented.ends_with(":"):
				formatted_lines.append(indent + stripped)
				indent_level += 1
			elif dedented.begins_with("}"):
				indent_level = max(0, indent_level - 1)
				indent = "    ".repeat(indent_level)
				formatted_lines.append(indent + stripped)
			else:
				formatted_lines.append(indent + stripped)
		else:
			formatted_lines.append(indent + stripped)
	
	var result := "\n".join(formatted_lines)
	result = result.strip_edges().dedent().strip_edges()
	
	return result + "\n"

func _get_template_for_type(template_type: int) -> String:
	var template_dir := "res://addons/neo_godot/generators/templates/"
	
	match template_type:
		TemplateType.EMPTY:
			return ""
		TemplateType.CHARACTER:
			return _load_template_file(template_dir + "character_template.gd")
		TemplateType.NODE:
			return _load_template_file(template_dir + "node_template.gd")
		TemplateType.AUTOLOAD:
			return _load_template_file(template_dir + "autoload_template.gd")
		TemplateType.EDITOR_PLUGIN:
			return _load_template_file(template_dir + "editor_plugin_template.gd")
		_:
			return ""

func _load_template_file(path: String) -> String:
	if FileAccess.file_exists(path):
		var file := FileAccess.open(path, FileAccess.READ)
		if file:
			return file.get_as_text()
	return ""

func _generate_empty_script(class_name: String) -> String:
	var script_lines := [
		"extends Node",
		"",
		"class_name " + class_name,
		"",
		"",
		"func _ready() -> void:",
		"    pass",
		"",
		"",
		"func _process(delta: float) -> void:",
		"    pass"
	]
	return "\n".join(script_lines)

func _call_ai_runtime(prompt: String, template_type: int, class_name: String) -> String:
	if not Engine.has_singleton("NeoRuntime"):
		return _generate_from_template_fallback(prompt, class_name)
	
	var runtime = Engine.get_singleton("NeoRuntime")
	var template_name := _get_template_name(template_type)
	var context := {
		"prompt": prompt,
		"template": template_name,
		"class_name": class_name
	}
	
	var result = await runtime.generate_async(context)
	
	if result is Dictionary and result.has("script"):
		return result["script"]
	elif result is String:
		return result
	
	return _generate_from_template_fallback(prompt, class_name)

func _get_template_name(template_type: int) -> String:
	match template_type:
		TemplateType.EMPTY:
			return "empty"
		TemplateType.CHARACTER:
			return "character"
		TemplateType.NODE:
			return "node"
		TemplateType.AUTOLOAD:
			return "autoload"
		TemplateType.EDITOR_PLUGIN:
			return "editor_plugin"
		_:
			return "custom"

func _generate_from_template_fallback(prompt: String, class_name: String) -> String:
	var script_lines := [
		"extends Node",
		"",
		"class_name " + class_name,
		"",
		"## Generated from prompt: " + prompt,
		"",
		"",
		"func _ready() -> void:",
		"    pass",
		"",
		"",
		"func _process(delta: float) -> void:",
		"    pass"
	]
	return "\n".join(script_lines)
