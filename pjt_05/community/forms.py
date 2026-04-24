from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    """게시글 작성/수정 폼"""

    class Meta:
        model = Post
        fields = ["title", "content"]
        labels = {
            "title": "제목",
            "content": "내용",
        }
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "제목을 입력하세요",
                "class": "form-input-full",
                "maxlength": 200,
            }),
            "content": forms.Textarea(attrs={
                "placeholder": "내용을 입력하세요",
                "class": "form-textarea",
                "rows": 10,
            }),
        }
        error_messages = {
            "title": {"required": "제목을 입력해 주세요."},
            "content": {"required": "내용을 입력해 주세요."},
        }
