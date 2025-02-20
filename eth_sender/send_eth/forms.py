from django import forms

class SendEthForm(forms.Form):
    mnemonic_phrase = forms.CharField(label="Mnemonic Phrase", widget=forms.Textarea(attrs={'rows': 2}))
    sender_address = forms.CharField(label="Sender Wallet Address")
    recipient_address = forms.CharField(label="Recipient Wallet Address")
