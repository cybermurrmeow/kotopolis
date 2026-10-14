WEAK_PASSWORDS = {
    "password1",
    "password123",
    "qwerty123",
    "qwerty1234",
    "qwerty12345",
    "12345678a",
    "123456789a",
    "admin123",
    "admin1234",
    "admin12345",
}


def password_errors(password, username="", email=""):
    errors = []
    lowered = password.lower()

    if not 8 <= len(password) <= 128:
        errors.append("Пароль должен быть от 8 до 128 символов")
    if not any(character.isalpha() for character in password) or not any(
        character.isdigit() for character in password
    ):
        errors.append("Пароль должен содержать хотя бы одну букву и одну цифру")
    if username and lowered == username.lower():
        errors.append("Пароль не должен совпадать с логином")
    if email and lowered == email.lower():
        errors.append("Пароль не должен совпадать с email")
    if lowered in WEAK_PASSWORDS:
        errors.append("Этот пароль слишком простой. Придумайте другой")

    return errors
