from django.contrib import admin
from .models import Video, List, Movie, MovieImage, Topic, Article, Rating, Prediction

class VideoMovieInline(admin.TabularInline):
    model = Video.related_movies.through
    #filter_horizontal = ("id",)
    #extra =1
class VideoTopicInline(admin.TabularInline):
    model = Video.related_topics.through

class ImageMovieInline(admin.TabularInline):
    model = MovieImage
class ListMovieInline(admin.TabularInline):
    model = List.movies.through
class TopicMovieInline(admin.TabularInline):
    model = Topic.movies.through

class ArticleMovieInline(admin.TabularInline):
    model = Article.related_movies.through

@admin.register(MovieImage)
class MovieImageAdmin(admin.ModelAdmin):
    list_display = ("id","movie","info","image" )

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id",'name',"year","imdb_id","tmdb_id", "imdb_rating","get_data_director" )
    inlines = [ImageMovieInline, ListMovieInline, TopicMovieInline, ArticleMovieInline]
    search_fields = ('name', 'imdb_id',"tmdb_id", 'id', )
    list_select_related = (
        'director',
    )

    def get_data_director(self, obj):
        if obj.data:
            return obj.data.get("Director")
        else:
            return ""

# Register your models here.
@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ("id",'name',"summary")
    raw_id_fields = ['movies',]

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("id",'title',"link")
    search_fields = ('id',"related_persons", 'title',"summary", )
    raw_id_fields = ['related_movies', 'related_persons', 'related_topics']

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("id",'name',)
    inlines = [VideoTopicInline,]
    raw_id_fields = ['movies', 'persons', 'lists',]
    
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("id",'name',)
    raw_id_fields = ['related_movies', 'related_persons', 'related_topics']

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("profile",'movie',"rating", "created_at",)
    search_fields = ('profile',"movie", 'rating', )


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ("profile",'movie',"prediction", "created_at","profile_points")




