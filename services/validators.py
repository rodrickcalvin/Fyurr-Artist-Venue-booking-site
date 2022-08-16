from wtforms import ValidationError

def validate_selection(form, field):
    """
    Validates the selection of the user on the select field.
    """
    if field.data == "" or field.data is None:
        raise ValidationError("Please select an option...")
