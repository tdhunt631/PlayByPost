from Game.models import Game, Character, Post, Comments, Round
from django.forms import ModelForm


class CreateGameForm(ModelForm):
    class Meta:
        model = Game
        fields = ['title','description','game_system','is_public']
        
class UpdateColorForm(ModelForm):
    class Meta:
        model = Character
        fields = ['color']        
        
class EditCharacterForm(ModelForm):
    class Meta:
        model = Character     
        fields = ['name','color']
    
class UpdateLocationForm(ModelForm):
    class Meta:
        model = Character
        fields = ['row', 'column']   
        
class EditMapForm(ModelForm):
    class Meta:
        model = Game
        fields = ['map']

class EditDescriptionForm(ModelForm):
    class Meta:
        model = Game
        fields = ['description']

class JoinGameForm(ModelForm):
    class Meta:
        model = Game
        exclude =('owner','players','pub_date','map','title','description','game_system','is_public')

class EditRoundForm(ModelForm):
    class Meta:
        model = Round
        fields = ['round_number', 'expiration_date']
        
class CreateRoundForm(ModelForm):
    class Meta:
        model = Round
        fields = ['round_number', 'expiration_date', 'game']
        
class CreateCharacterForm(ModelForm):
    class Meta:
        model = Character
        exclude = ('user', 'color', 'column', 'row', 'game')
        
class CharacterPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['post']

class CommentForm(ModelForm):
    class Meta:
        model = Comments
        fields = ['comment']
