CODE = r"^[0-9]{4}$"

PHONE = r"^1[3-9][0-9]{9}$"

USERNAME = r"^[a-zA-Z0-9\u4e00-\u9fa5]{1,16}$"

CARD = r"^[0-9]{9}$"

PASSWORD = r"^[a-zA-Z0-9-*/+.~!@#$%^&*()]{6,16}$"

EMAIL = r"^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$"

SCHOOL = r"^[a-zA-Z0-9\u4e00-\u9fa5]{1,10}$"

ARTICLE_TITLE = r"^.{1,32}$"

ARTICLE = r"^[\s\S]{1,2048}$"

URL_ENCODE = r"^[-_.!~*'()0-9a-zA-Z%]+$"
