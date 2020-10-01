COMPONENT_DELIMITER = "#"


def split_file_component(text):
    if COMPONENT_DELIMITER in text:
        i = text.index(COMPONENT_DELIMITER)
        return text[:i], text[i + 1 :]
    else:
        return None, text
