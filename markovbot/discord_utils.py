import re

def extract_id_from_mention(mention: str) -> int:
    search = re.search('<@!(.*)>', mention, re.IGNORECASE)

    if search:
        return int(search.group(1))

    return None