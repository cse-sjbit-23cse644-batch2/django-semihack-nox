from django import forms
from .models import Participant, Event, ScheduleItem, EventUpdate
from .validators import validate_receipt_file


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['student_id', 'name', 'email', 'phone', 'college', 'event', 'transaction_id', 'receipt']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1SJ21CS001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9876543210'}),
            'college': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'College / Institution'}),
            'event': forms.Select(attrs={'class': 'form-select'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UPI/Bank reference no.'}),
            'receipt': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_transaction_id(self):
        txn_id = self.cleaned_data.get('transaction_id')
        qs = Participant.objects.filter(transaction_id=txn_id)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This Transaction ID has already been used.")
        return txn_id

    def clean_student_id(self):
        sid = self.cleaned_data.get('student_id')
        qs = Participant.objects.filter(student_id=sid)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A participant with this Student ID is already registered.")
        return sid

    def clean_receipt(self):
        receipt = self.cleaned_data.get('receipt')
        if receipt:
            validate_receipt_file(receipt)
        return receipt


class FeedbackForm(forms.Form):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Overall Rating (1–5)"
    )
    comments = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                     'placeholder': 'Share your experience...'}),
        required=False,
        label="Comments"
    )


class EventUpdateForm(forms.ModelForm):
    class Meta:
        model = EventUpdate
        fields = ['title', 'message', 'is_important']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Update title'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_important': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ScheduleItemForm(forms.ModelForm):
    class Meta:
        model = ScheduleItem
        fields = ['time', 'title', 'description', 'speaker', 'is_current', 'order']
        widgets = {
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'speaker': forms.TextInput(attrs={'class': 'form-control'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
