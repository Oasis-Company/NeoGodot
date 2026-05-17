extends RefCounted
class_name ImportConfigGenerator

func generate_texture_config(source_path: String, options: Dictionary) -> Dictionary:
	var config: Dictionary = {}
	
	config["remap"] = {
		"dest_path": options.get("dest_path", source_path.get_basename() + ".tres")
	}
	
	config["deps"] = {
		"source_file": source_path,
		"dest_files": []
	}
	
	config["params"] = {
		"compress/mode": options.get("compress_mode", 0),
		"compress/hdr_mode": options.get("hdr_mode", 0),
		"compress/bptc_ldr": options.get("bptc_ldr", 0),
		"compress/normal_map": options.get("normal_map", 0),
		"compress/channel_pack": options.get("channel_pack", 0),
		"mipmaps/generate": options.get("generate_mipmaps", true),
		"mipmaps/limit": options.get("mipmap_limit", -1),
		"roughness/mode": options.get("roughness_mode", 0),
		"roughness/src_normal": options.get("roughness_src_normal", ""),
		"process/fix_alpha_border": options.get("fix_alpha_border", true),
		"process/premult_alpha": options.get("premult_alpha", false),
		"process/normal_map_invert_y": options.get("normal_map_invert_y", false),
		"process/hq_noise_api": options.get("hq_noise_api", true),
		"stream": options.get("stream", false),
		"svg/scale": options.get("svg_scale", 1.0)
	}
	
	return config

func generate_script_config(source_path: String, options: Dictionary) -> Dictionary:
	var config: Dictionary = {}
	
	config["remap"] = {
		"dest_path": options.get("dest_path", source_path.get_basename() + ".gd.res")
	}
	
	config["deps"] = {
		"source_file": source_path,
		"dest_files": []
	}
	
	config["params"] = {
		"load_steps": options.get("load_steps", 0),
		"uses_nanoid": options.get("uses_nanoid", false),
		"opaque_variant": options.get("opaque_variant", false),
		"completion_mode": options.get("completion_mode", 0)
	}
	
	return config

func write_import_file(config: Dictionary, output_path: String) -> bool:
	var file: FileAccess = FileAccess.open(output_path, FileAccess.WRITE)
	if file == null:
		return false
	
	for section: String in ["remap", "deps", "params"]:
		if section in config:
			file.store_line("[" + section + "]")
			for key: String in config[section]:
				var value = config[section][key]
				file.store_line(str(key) + "=" + str(value))
			file.store_line("")
	
	file.close()
	return true
