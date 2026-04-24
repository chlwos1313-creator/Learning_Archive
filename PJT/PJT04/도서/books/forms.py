from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    """
    Book 모델 기반의 ModelForm (F403)
    - 사용자가 직접 입력하는 필드만 포함 (title, author, description)
    - author_info는 AI가 자동으로 채워주므로 폼에서 제외
    """

    class Meta:
        model = Book
        # author_info는 AI API로 자동 채워지므로 사용자 입력 대상에서 제외
        fields = ["title", "author", "description"]

        labels = {
            "title": "도서 제목",
            "author": "저자",
            "description": "도서 설명",
        }

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "도서 제목을 입력하세요",
                }
            ),
            "author": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "저자명을 입력하세요",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "도서 설명을 입력하세요",
                    "rows": 5,
                }
            ),
        }
