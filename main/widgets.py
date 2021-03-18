from django.forms.widgets import Widget

class PlusMinusWidget(Widget):
    template_name = 'widgets/plus-minus-template.html'
    class Media:
        css = {
            ('all','style/plusminusnumber.css')
        }
        js = ('script/plusminusnumber.js')