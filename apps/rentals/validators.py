from django.core.exceptions import ValidationError


def validate_tc_no(value):
    """T.C. Kimlik No 11 haneli checksum algoritmasıyla doğrular."""
    if not value:
        return
    if not value.isdigit() or len(value) != 11:
        raise ValidationError("T.C. Kimlik No 11 haneli rakamlardan oluşmalıdır.")
    digits = [int(d) for d in value]
    if digits[0] == 0:
        raise ValidationError("T.C. Kimlik No 0 ile başlayamaz.")
    odd_sum = sum(digits[0:9:2])
    even_sum = sum(digits[1:8:2])
    check_digit_10 = ((odd_sum * 7) - even_sum) % 10
    check_digit_11 = sum(digits[0:10]) % 10
    if check_digit_10 != digits[9] or check_digit_11 != digits[10]:
        raise ValidationError("Geçersiz T.C. Kimlik No.")


def validate_tax_no(value):
    """Vergi No için basit format kontrolü (10 haneli rakam)."""
    if not value:
        return
    if not value.isdigit() or len(value) != 10:
        raise ValidationError("Vergi No 10 haneli rakamlardan oluşmalıdır.")
