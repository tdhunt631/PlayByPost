from django.contrib import admin
from Game.models import Game, Character, Post, Round, Comments

class GameAdmin(admin.ModelAdmin):
    pass

class CharacterAdmin(admin.ModelAdmin):
    pass

class PostAdmin(admin.ModelAdmin):
    pass

class RoundAdmin(admin.ModelAdmin):
    pass

class CommentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Game, GameAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Comments, CommentAdmin)
