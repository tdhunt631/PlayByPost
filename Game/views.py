from Game.forms import *
from Game.models import *
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import simplejson as json
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, UpdateView, CreateView

# CLASS DECORATOR FOR MAKING VIEWS LOGIN REQUIRED
def class_view_decorator(decorator):
    def my_decorator(View):
        View.dispatch = method_decorator(decorator)(View.dispatch)
        return View
    return my_decorator

# INDEX PAGE
class Index(ListView):
    template_name = 'Game/index.html'
    model = Game
    context_object_name = 'games'

    def get_queryset(self):
        return Game.objects.all()
    
# GAME INDEX PAGE
@class_view_decorator(login_required)
class GameIndex(DetailView):
    template_name = 'Game/game_index.html'
    model = Game
    context_object_name = 'game'
     
    def get_context_data(self, **kwargs):
        context = super(GameIndex, self).get_context_data(**kwargs)
        currentGame = get_object_or_404(Game, id=self.kwargs['pk'])                    
        context['game'] = currentGame
        context['posts'] = Post.objects.filter(game = currentGame).order_by('-pub_date')
        context['characters'] = Character.objects.filter(game = currentGame)
        context['round'] = get_object_or_404(Round, id=self.kwargs['pk'])            
        return context
    
# List of users games
@class_view_decorator(login_required)
class MyGames(ListView):
    template_name = 'Game/myGames.html'
    model = Game
    context_object_name = 'games'

    def get_queryset(self):
        #return games that the user owns or is a players of
        return Game.objects.filter(Q(owner = self.request.user.id) | Q(players = self.request.user.id)).distinct().order_by('-pub_date')
    
# List of users characters
@class_view_decorator(login_required)
class MyCharacters(ListView):
    template_name = 'Game/myCharacters.html'
    model = Character
    context_object_name = 'characters'

    def get_queryset(self):
        return Character.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super(MyCharacters, self).get_context_data(**kwargs)
        #currentPlayers = Game.objects.filter(players=self.request.user.id)
        #context['games'] =  Game.objects.filter(Q(owner = self.request.user.id) | Q(players__in=currentPlayers)).distinct().order_by('-pub_date')
        return context
    
# CREATE A GAME
@class_view_decorator(login_required)
class CreateGame(CreateView):
    form_class = CreateGameForm
    template_name = 'Game/createGame.html'
    success_url = '/createRound/'
                
    def form_valid(self, form):                
        currentUser = User.objects.filter(id=self.request.user.id)
        form.instance.owner = self.request.user   
        form.save()              
        form.instance.players = currentUser
        form.save()
                
        currentGame = get_object_or_404(Game, id=form.instance.id)
        
        character = Character()
        character.game = currentGame
        character.user = self.request.user
        character.name = self.request.POST['character']
        character.save()
        
        newRound = Round()
        newRound.game = currentGame
        newRound.round_number = "1"
        d = timedelta(days=3)
        newRound.expiration_date = datetime.now() + d
        newRound.save()
        
        return super(CreateGame, self).form_valid(form)
        
    def get_success_url(self):
        return reverse('Game:game_index', args=[str(self.object.id)])
                        
# CREATE A ROUND
@class_view_decorator(login_required)
class CreateRound(CreateView):
    form_class = CreateRoundForm
    template_name = 'Game/createRound.html'   

    def get_success_url(self):
        return "/createCharacter/?id=" + str(self.object.pk)
    
# CREATE A CHARACTER
@class_view_decorator(login_required)
class CreateCharacter(CreateView):
    form_class = CreateCharacterForm
    template_name = 'Game/createCharacter.html'   
    success_url = "/myGames/"

    def get_form(self, form_class):
        if self.request.user.is_authenticated():
            form = super(CreateCharacter, self).get_form(form_class)            
            form.instance.user = self.request.user
            form.instance.game = get_object_or_404(Game, id=self.kwargs['pk'])
            return form    
    
    def get_context_data(self, **kwargs):
        context = super(CreateCharacter, self).get_context_data(**kwargs)        
        context['game'] = get_object_or_404(Game, id=self.kwargs['pk'])
        return context    
    
    def get_success_url(self):
        return "/game/" + str(self.object.pk) + "/"
        
# EDIT CHARACTER
@class_view_decorator(login_required)
class EditCharacter(UpdateView):
    form_class= EditCharacterForm
    model = Character
    template_name = 'Game/editCharacter.html'
    success_url = '/myCharacters/'
    
    def get_object(self):
        return get_object_or_404(Character, id=self.kwargs['pk'])
    
# UPDATE CHARACTER COLOR
@class_view_decorator(login_required)
class UpdateColor(UpdateView):
    form_class= UpdateColorForm
    model = Character
    template_name = 'Game/updateColor.html'
    
    def get_object(self):
        return get_object_or_404(Character, id=self.kwargs['pk'])
    
    def form_valid(self, form):
        if self.request.is_ajax():
            self.object = form.save()
            return HttpResponse(json.dumps(self.object.color),
                mimetype="application/json")
        return super(UpdateColor, self).form_valid(form)
    
# JOIN A GAME
@class_view_decorator(login_required)
class JoinGame(UpdateView):
    form_class= JoinGameForm
    model = Game
    template_name = 'Game/joinGame.html'
    context_name = 'game'
    
    def get_object(self):
        return get_object_or_404(Game, id=self.kwargs['pk'])
           
    def form_valid(self, form):               
        obj = form.save(commit=False)
        p = User.objects.get(id=self.request.user.id)
        obj.players.add(p)        
        obj.save()
        form.save_m2m()
                
        currentGame = get_object_or_404(Game, id=form.instance.id)
        
        if obj.is_public == True:        
            character = Character()
            character.game = currentGame
            character.pending = False
            character.user = self.request.user
            character.name = self.request.POST['name']
            character.save()
        else:
            character = Character()
            character.game = currentGame
            character.pending = True
            character.user = self.request.user
            character.name = self.request.POST['name']
            character.save()
            
        return super(JoinGame, self).form_valid(form)

    def get_success_url(self):
        return "/game/"+self.kwargs['pk']+"/"
    
# UPDATE CHARACTER location
@class_view_decorator(login_required)
class UpdateLocation(UpdateView):
    form_class = UpdateLocationForm
    model = Character
    template_name = 'Game/updateLocation.html'
    
    def get_object(self):
        return get_object_or_404(Character, id=self.kwargs['pk'])
    
    def form_valid(self, form):
        if self.request.is_ajax():
            self.object = form.save()
            return HttpResponse(json.dumps(self.object.color), mimetype="application/json")
        return super(UpdateColor, self).form_valid(form)
    
# EDIT THE GAME MAP
@class_view_decorator(login_required)
class EditMap(DetailView):
    form_class = EditMapForm
    model = Game
    template_name = 'Game/editMap.html'
    
# EDIT THE GAME ROUND
@class_view_decorator(login_required)
class EditRound(UpdateView):
    form_class = EditRoundForm
    model = Round
    success_url = '/myGames/'
    template_name = 'Game/editRound.html'
    
    def get_form(self, form_class):
        if self.request.user.is_authenticated():
            form = super(EditRound, self).get_form(form_class)
            currentRound = get_object_or_404(Round, id=self.kwargs['pk'])
            form.instance.game = get_object_or_404(Game, id=currentRound.game.id)
            return form     

# UPDATE GAME DESCRIPTION
@class_view_decorator(login_required)
class EditDescription(UpdateView):
    form_class= EditDescriptionForm
    model = Game
    template_name = 'Game/editDescription.html'
    
    def get_success_url(self):
        return "/game/"+ self.kwargs['pk'] + "/"
    
    def get_object(self):
        return get_object_or_404(Game, id=self.kwargs['pk'])        
    
# UPDATE GAME MAP
@class_view_decorator(login_required)
class SaveMap(UpdateView):
    form_class= EditMapForm
    model = Game
    template_name = 'Game/saveMap.html'
    success_url = '/myGames/'
    
    def get_object(self):
        return get_object_or_404(Game, id=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super(SaveMap, self).get_context_data(**kwargs)        
        context['game'] = get_object_or_404(Game, id=self.kwargs['pk'])
        return context    
    
    def form_valid(self, form):
        # convert the image and save it        
        return super(SaveMap, self).form_valid(form)
    
# Character post
@class_view_decorator(login_required)
class CharacterPost(CreateView):
    form_class = CharacterPostForm
    template_name = 'Game/postResponse.html'
    
    def get_form(self, form_class):
        if self.request.user.is_authenticated():
            form = super(CharacterPost, self).get_form(form_class)
            form.instance.user = get_object_or_404(User, id=self.request.user.id)
            form.instance.game = get_object_or_404(Game, id=self.kwargs['pk'])
            form.instance.character = get_object_or_404(Character, id=self.kwargs['character'])
            return form     
        
    def form_valid(self, form):
        if self.request.is_ajax():
            self.object = form.save()
            context = {'post': self.object,}
            return HttpResponse(render(self.request, 'Game/postResponse.html', context, content_type="application/xhtml"))
        return super(CharacterPost, self).form_valid(form)
   
        
# Comment post
@class_view_decorator(login_required)
class CommentPost(CreateView):
    form_class = CommentForm
    template_name = 'Game/commentResponse.html'
    
    def get_form(self, form_class):
        if self.request.user.is_authenticated():
            form = super(CommentPost, self).get_form(form_class)
            form.instance.post = get_object_or_404(Post, id=self.kwargs['pk'])
            form.instance.user = self.request.user
            return form
        
    def form_valid(self, form):
        if self.request.is_ajax():
            self.object = form.save()
            context = {'comment': self.object,}
            return HttpResponse(render(self.request, 'Game/commentResponse.html', context, content_type="application/xhtml"))
        return super(CommentPost, self).form_valid(form)
    
# Comment post
@class_view_decorator(login_required)
class Pending(DetailView):
    template_name = 'Game/pending.html'
    
    def get_object(self):
        return get_object_or_404(Game, id=self.kwargs['pk'])

# Delete a Comment
def commmentDelete(request, commentId):
    myObject = get_object_or_404(Comments, id=commentId)
    post = get_object_or_404(Post, id=myObject.post.id)
    game = get_object_or_404(Game, id=post.game.id)
    if myObject.user == request.user or request.user == game.owner:
        myObject.delete()
    return HttpResponseRedirect("/")
       
# Delete a Post
def postDelete(request, postId):
    myObject = get_object_or_404(Post, id=postId)
    game = get_object_or_404(Game, id=myObject.game.id)
    if myObject.user == request.user or request.user == game.owner:
        myObject.delete()
    return HttpResponseRedirect("/")

# Delete a character
def characterDelete(request, pk):
    myObject = get_object_or_404(Character, id=pk)
    game = get_object_or_404(Game, id=myObject.game.id)
    if myObject.user == request.user or request.user == game.owner:
        myObject.delete()
    return HttpResponseRedirect("/myGames/")

# Activate a character
def activateCharacter(request, pk):
    myObject = get_object_or_404(Character, id=pk)
    game = get_object_or_404(Game, id=myObject.game.id)
    if request.user == game.owner:
        myObject.pending = False
    myObject.save()
    return HttpResponseRedirect("/game/"+ str(game.id) +"/")