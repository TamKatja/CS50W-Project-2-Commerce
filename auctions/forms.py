from django import forms
from django.forms import ModelForm

from .models import Listing


class AddListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = [
            "title",
            "description",
            "start_price",
            "image_link",
            "image_file",
            "category",
        ]


class CommentForm(forms.Form):
    message = forms.CharField(
        max_length=500, widget=forms.Textarea(attrs={"maxlength": 500})
    )


class BidForm(forms.Form):
    bid_price = forms.DecimalField(max_digits=10, decimal_places=2)
