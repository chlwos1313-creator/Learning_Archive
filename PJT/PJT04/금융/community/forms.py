from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # 사용자로부터 입력받을 필드 설정 (F404, F406)
        fields = ['title', 'content', 'author']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '제목을 입력하세요'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '내용을 입력하세요'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '작성자(선택)'}),
        }