"""Base form class that auto-applies Bootstrap 5 styling to all widgets."""

from django import forms


class BootstrapForm(forms.ModelForm):
    """
    ModelForm base that injects Bootstrap 5 classes into every widget.
    Subclasses inherit form-control/form-select automatically.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault('class', 'form-select')
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-check-input')
            else:
                widget.attrs.setdefault('class', 'form-control')
            widget.attrs.setdefault('placeholder', ' ')
