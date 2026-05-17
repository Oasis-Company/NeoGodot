class_name TemplateEngine

var _template_dir := "res://addons/neo_godot/generators/templates/"

func load_template(name: String) -> String:
	var path := _template_dir + name
	if not name.ends_with(".gd"):
		path += ".gd"
	
	if not FileAccess.file_exists(path):
		push_warning("[TemplateEngine] Template not found: " + path)
		return ""
	
	var file := FileAccess.open(path, FileAccess.READ)
	if not file:
		push_warning("[TemplateEngine] Cannot open template: " + path)
		return ""
	
	var content := file.get_as_text()
	file.close()
	
	return content

func render(template: String, context: Dictionary) -> String:
	if template.is_empty():
		return ""
	
	var result := template
	
	result = _render_variables(result, context)
	result = _render_conditionals(result, context)
	result = _render_loops(result, context)
	
	return result

func _render_variables(template: String, context: Dictionary) -> String:
	var pattern := RegEx.new()
	var result := template
	
	if pattern.compile("\\{\\{([^}]+)\\}\\}") != OK:
		return template
	
	var matches := pattern.search_all(result)
	var reversed := matches.duplicate()
	reversed.reverse()
	
	for match in reversed:
		var var_name := match.get_string(1).strip_edges()
		var parts := var_name.split(".")
		var value = context
		
		for part in parts:
			if value is Dictionary and value.has(part):
				value = value[part]
			else:
				value = null
				break
		
		if value != null:
			var replacement := ""
			if value is String:
				replacement = value
			elif value is int or value is float:
				replacement = str(value)
			elif value is bool:
				replacement = "true" if value else "false"
			elif value is Array:
				replacement = str(value)
			else:
				replacement = str(value)
			
			result = result.substr(0, match.get_start()) + replacement + result.substr(match.get_end())
	
	return result

func _render_conditionals(template: String, context: Dictionary) -> String:
	var result := template
	
	var if_pattern := RegEx.new()
	if if_pattern.compile("{%\\s*if\\s+([^%]+)%}") != OK:
		return result
	
	var elif_pattern := RegEx.new()
	if elif_pattern.compile("{%\\s*elif\\s+([^%]+)%}") != OK:
		return result
	
	var else_pattern := RegEx.new()
	if else_pattern.compile("{%\\s*else\\s*%}") != OK:
		return result
	
	var endif_pattern := RegEx.new()
	if endif_pattern.compile("{%\\s*endif\\s*%}") != OK:
		return result
	
	while true:
		var if_matches := if_pattern.search_all(result)
		if if_matches.is_empty():
			break
		
		var if_match := if_matches[0]
		var block_start := if_match.get_start()
		
		var after_if := result.substr(if_match.get_end())
		var endif_matches := endif_pattern.search(after_if)
		
		if not endif_matches:
			break
		
		var block_end := if_match.get_end() + endif_matches.get_start()
		var full_block := result.substr(block_start, block_end - block_start)
		
		var condition := if_match.get_string(1).strip_edges()
		var block_body := full_block.substr(if_match.get_end() - block_start)
		block_body = block_body.substr(0, block_body.length() - endif_matches.get_length() - (after_if.substr(0, endif_matches.get_start()).length()))
		
		var else_body := ""
		var elseif_parts := elif_pattern.search_all(block_body)
		var endif_pos := -1
		
		for elif_match in elseif_parts:
			if endif_pos == -1 or elif_match.get_start() < endif_pos:
				endif_pos = elif_match.get_start()
		
		var else_match := else_pattern.search(block_body)
		if else_match and (endif_pos == -1 or else_match.get_start() < endif_pos):
			endif_pos = else_match.get_start()
		
		var content_to_render := block_body
		if endif_pos > 0:
			content_to_render = block_body.substr(0, endif_pos)
		
		var rendered := _evaluate_condition(condition, context) if _evaluate_condition(condition, context) else ""
		
		if else_match and not _evaluate_condition(condition, context):
			var else_start := else_match.get_end()
			var else_content := block_body.substr(else_start)
			
			for extra_endif in endif_pattern.search_all(block_body):
				if extra_endif.get_start() >= endif_pos:
					else_content = block_body.substr(else_start, extra_endif.get_start() - else_start)
					break
			
			rendered = else_content.strip_edges()
		
		var block_length := endif_match.get_end() - if_match.get_start()
		result = result.substr(0, if_match.get_start()) + rendered + result.substr(if_match.get_start() + block_length)
	
	return result

func _render_loops(template: String, context: Dictionary) -> String:
	var result := template
	
	var for_pattern := RegEx.new()
	if for_pattern.compile("{%\\s*for\\s+([^%]+)%}") != OK:
		return result
	
	var endfor_pattern := RegEx.new()
	if endfor_pattern.compile("{%\\s*endfor\\s*%}") != OK:
		return result
	
	while true:
		var for_matches := for_pattern.search_all(result)
		if for_matches.is_empty():
			break
		
		var for_match := for_matches[0]
		var block_start := for_match.get_start()
		
		var after_for := result.substr(for_match.get_end())
		var endfor_matches := endfor_pattern.search(after_for)
		
		if not endfor_matches:
			break
		
		var block_end := for_match.get_end() + endfor_matches.get_start()
		var full_block := result.substr(block_start, block_end - block_start)
		
		var loop_expr := for_match.get_string(1).strip_edges()
		var parts := loop_expr.split(" in ")
		if parts.size() != 2:
			break
		
		var loop_var := parts[0].strip_edges()
		var iterable_expr := parts[1].strip_edges()
		
		var loop_body := full_block.substr(for_match.get_length(), 
			full_block.length() - for_match.get_length() - endfor_matches.get_length())
		
		var items = _get_iterable_value(iterable_expr, context)
		if items == null:
			items = []
		
		var rendered_lines: Array[String] = []
		
		if items is Array:
			for i in range(items.size()):
				var item = items[i]
				var iteration_context := context.duplicate(true)
				iteration_context[loop_var] = item
				iteration_context[loop_var + "_index"] = i
				iteration_context[loop_var + "_first"] = (i == 0)
				iteration_context[loop_var + "_last"] = (i == items.size() - 1)
				
				var rendered := render(loop_body, iteration_context)
				for line in rendered.split("\n"):
					if not line.strip_edges().is_empty():
						rendered_lines.append(line)
		
		var rendered := "\n".join(rendered_lines)
		result = result.substr(0, block_start) + rendered + result.substr(block_end)
	
	return result

func _evaluate_condition(condition: String, context: Dictionary) -> bool:
	condition = condition.strip_edges()
	
	if condition.begins_with("not "):
		var inner := condition.substr(4).strip_edges()
		return not _get_value(inner, context)
	
	var value := _get_value(condition, context)
	
	if value is bool:
		return value
	elif value is String:
		return not value.is_empty()
	elif value is Array or value is Dictionary:
		return value.size() > 0
	elif value is int or value is float:
		return value != 0
	
	return false

func _get_value(expr: String, context: Dictionary):
	expr = expr.strip_edges()
	
	if context.has(expr):
		return context[expr]
	
	if "." in expr:
		var parts := expr.split(".")
		var value = context
		for part in parts:
			if value is Dictionary and value.has(part):
				value = value[part]
			else:
				return null
		return value
	
	if expr == "true":
		return true
	elif expr == "false":
		return false
	elif expr.is_valid_int():
		return expr.to_int()
	elif expr.is_valid_float():
		return expr.to_float()
	
	return null

func _get_iterable_value(expr: String, context: Dictionary):
	var value = _get_value(expr, context)
	
	if value is Array or value is Dictionary:
		return value
	
	return []

func set_template_directory(path: String) -> void:
	_template_dir = path
	if not _template_dir.ends_with("/"):
		_template_dir += "/"

func get_template_directory() -> String:
	return _template_dir
