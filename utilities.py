def normalizePath(path):
	parts = path.split("/")
	normalized = list()
	if not parts[0]:
		parts.pop(0)
	for part in parts:
		if part != ".":
			if part == ".." and len(normalized) > 0 and normalized[len(normalized)-1] != ".." :
				normalized.pop()
			elif part:
				normalized.append(part)
	return normalized