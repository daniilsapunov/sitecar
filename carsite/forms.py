from django.forms import ModelForm

from .models import Comment, ChildComment


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)


class ChildCommentForm(ModelForm):
    class Meta:
        model = ChildComment
        fields = ('text',)
