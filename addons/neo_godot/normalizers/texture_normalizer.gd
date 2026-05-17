extends RefCounted
class_name TextureNormalizer

const MAX_TEXTURE_SIZE: int = 4096
const DEFAULT_COMPRESS_QUALITY: float = 0.7

signal normalization_progress(progress: float, status: String)
signal normalization_complete(result: Dictionary)
signal normalization_error(error_message: String)

func normalize(texture_path: String, options: Dictionary) -> bool:
	if not FileAccess.file_exists(texture_path):
		normalization_error.emit("Texture file not found: " + texture_path)
		return false
	
	var image: Image = _load_image(texture_path)
	if image == null:
		normalization_error.emit("Failed to load image: " + texture_path)
		return false
	
	normalization_progress.emit(0.2, "Checking texture dimensions")
	
	var max_size: int = options.get("max_size", MAX_TEXTURE_SIZE)
	if image.get_width() > max_size or image.get_height() > max_size:
		image = _resize_image(image, max_size)
	
	normalization_progress.emit(0.4, "Applying compression settings")
	
	var compression_mode: int = options.get("compression_mode", 0)
	_apply_compression(image, compression_mode)
	
	normalization_progress.emit(0.6, "Applying texture flags")
	
	var texture: ImageTexture = ImageTexture.create_from_image(image)
	var flags: int = options.get("flags", Texture.FLAG_FILTER)
	_apply_flags(texture, flags)
	
	normalization_progress.emit(0.8, "Applying filter settings")
	
	if options.get("filter_enabled", true):
		texture.set_flags(texture.get_flags() | Texture.FLAG_FILTER)
	
	var save_path: String = options.get("save_path", texture_path)
	var success: bool = _save_texture(texture, save_path)
	
	if success:
		normalization_progress.emit(1.0, "Normalization complete")
		normalization_complete.emit({
			"original_path": texture_path,
			"output_path": save_path,
			"original_size": image.get_size(),
			"compression_mode": compression_mode
		})
	else:
		normalization_error.emit("Failed to save texture: " + save_path)
	
	return success

func _load_image(path: String) -> Image:
	var image: Image = Image.new()
	var error: Error = image.load(path)
	if error != OK:
		return null
	return image

func _resize_image(image: Image, max_size: int) -> Image:
	var width: int = image.get_width()
	var height: int = image.get_height()
	
	if width <= max_size and height <= max_size:
		return image
	
	var ratio: float = mini(float(max_size) / float(width), float(max_size) / float(height))
	var new_width: int = int(float(width) * ratio)
	var new_height: int = int(float(height) * ratio)
	
	var resized: Image = image.resize(new_width, new_height, Image.INTERPOLATE_CUBIC)
	return resized

func _apply_compression(image: Image, mode: int) -> void:
	match mode:
		0:
			pass
		1:
			pass
		2:
			pass

func _apply_flags(texture: ImageTexture, flags: int) -> void:
	texture.set_flags(flags)

func _save_texture(texture: ImageTexture, save_path: String) -> bool:
	var success: bool = texture.save_png(save_path)
	return success == OK
