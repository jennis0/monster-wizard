from typing import Optional, Union, List

def get_input(title: str, text: str, default: Optional[Union[str, List[str]]] = None, is_list: bool=False) -> str:
    '''Get user input with optional default'''
    if default:
        default_text = " [default={}]".format(default)
    else:
        default_text = ""
    result = input("{title}: {text}{default_text}:".format(title=title, text=text, default_text=default_text)).strip()

    if len(result) == 0 and default:
        if is_list and not isinstance(default, list):
            return [default]
        return default

    if is_list:
        result = [r.strip() for r in result.split(",")]

    return result