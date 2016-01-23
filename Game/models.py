from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import get_object_or_404
    
class Game(models.Model):
    owner = models.ForeignKey(User, related_name='owner')
    players = models.ManyToManyField(User, related_name='players')
    is_public = models.BooleanField(default=True)
    description = models.TextField()
    title = models.CharField(max_length=100, unique=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    game_system = models.CharField(max_length=100)
    map = models.TextField(blank=True, null=True)
      
    def __unicode__(self):
        return self.title
    
    def getGrid(self, *args, **kwargs):
        size = 36
        grid = '<table class="map" cellspacing="0" cellpadding="0" border="0">'
        for i in xrange(size):
            grid += '<tr>'
            for j in xrange(size):                   
                grid += '<td id="' + str(i) + '-' + str(j) + '" class="gridCell"> </td>'
            grid += '</tr>'
        grid += '</table>'
        return grid
    
    def getLocations(self,*args, **kwargs):
        characters = Character.objects.filter(game=self.id)
        locations = []
        for character in characters:
            locations.append(str(character.row) + '-' + str(character.column))
        return locations
    
    def getColors(self,*args,**kwargs):
        characters = Character.objects.filter(game=self.id)
        colors = []
        for character in characters:
            colors.append(character.color);
        return colors   
    
    def getRoundEnd(self,*args,**kwargs):
        current_round = get_object_or_404(Round, game=self.id)
        return current_round.expiration_date
    
    def getPending(self,*args,**kwargs):
        characters = Character.objects.filter(game=self.id)       
        count = 0
        pendingCharacters = "<div class=\"panel panel-default\"><div class=\"panel-heading\"><h4 class=\"panel-title\"><strong>Pending Characters</strong></h4></div><table class=\"table\">"
        for character in characters:
            if character.pending == True:
                pendingCharacters += "<tr><td>"+ str(character.name)+ "</td><td>"+ "<a href=\"/activateCharacter/" + str(character.id) + "/\" class=\"btn btn-success btn-xs pull-right\">Activate</a></td></tr>"
                count += 1
        pendingCharacters += "</table></div>"
        if count > 0:
            return pendingCharacters
        else:
            return " "
    
#---#

class Round(models.Model):
    game = models.ForeignKey(Game);
    round_number = models.CharField(max_length=4, default="1")
    expiration_date = models.DateTimeField()
    
    def __unicode__(self):
        return self.round_number
    
#---#

class Character(models.Model):
    game = models.ForeignKey(Game);
    user = models.ForeignKey(User)
    name = models.CharField(max_length=32)
    color = models.CharField(max_length=20, default="rgb(0, 0, 0)")
    column = models.IntegerField(blank=True, null=True) #Store cordinates for character token
    row = models.IntegerField(blank=True, null=True)
    pending = models.BooleanField(default=False)
        
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return '/game/'

#---#
    
class Post(models.Model):    
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game);
    character = models.ForeignKey(Character)
    post = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.post
    
    def getComments(self,*args,**kwargs):
        comments = Comments.objects.filter(post=self.id).order_by('-pub_date')
        return comments

#---#
    
class Comments(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    comment = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.comment
    