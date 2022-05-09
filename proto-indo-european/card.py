
def batch_replace(string, replacements):
	result = string
	for replaced, replacement in replacements:
		result = result.replace(replaced, replacement) 
	return result

def card(emoji, en, ie):
	emoji_style = "font-size:5em; font-family: 'Twemoji', 'Twemoji Mozilla','Segoe UI Emoji','Noto Color Emoji', 'DejaVu Sans', 'sans-serif'"
	return f'<div style="{emoji_style}">{emoji}</div><div style="font-size:small">{en}</div><div style="font-size:large">{ie}</div>'
