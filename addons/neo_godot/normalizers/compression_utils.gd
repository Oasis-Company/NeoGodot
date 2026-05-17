class_name CompressionUtils

enum CompressionMode {
	LOSSY,
	LOSSLESS,
	VRAM_COMPRESSED
}

func get_compression_params(mode: int) -> Dictionary:
	match mode:
		CompressionMode.LOSSY:
			return {
				"format": "jpg",
				"quality": 0.8,
				"lossy": true
			}
		CompressionMode.LOSSLESS:
			return {
				"format": "png",
				"quality": 1.0,
				"lossy": false
			}
		CompressionMode.VRAM_COMPRESSED:
			return {
				"format": "etc2",
				"quality": 1.0,
				"lossy": false
			}
		_:
			return {}

func estimate_compressed_size(original_size: int, mode: int) -> int:
	var params: Dictionary = get_compression_params(mode)
	
	match mode:
		CompressionMode.LOSSY:
			return int(float(original_size) * 0.1)
		CompressionMode.LOSSLESS:
			return int(float(original_size) * 0.5)
		CompressionMode.VRAM_COMPRESSED:
			return int(float(original_size) * 0.25)
		_:
			return original_size

func is_compression_supported(format: String) -> bool:
	var supported_formats: Array = ["png", "jpg", "jpeg", "webp", "etc2", "astc"]
	return format.to_lower() in supported_formats
