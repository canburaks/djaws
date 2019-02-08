from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Video, List, Movie, MovieImage, Topic, Article, Rating, Prediction
from items.resources import ArticleResource, VideoResource

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
    inlines = [ImageMovieInline, ListMovieInline, TopicMovieInline]
    search_fields = ('name', 'imdb_id',"tmdb_id", 'id', )
    def get_data_director(self, obj):
        if obj.data:
            return obj.data.get("Director")
        else:
            return ""

# Register your models here.
@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ("id",'name', "owner")
    raw_id_fields = ['movies', "owner", "related_persons"]
    list_select_related = ('owner',)
    exclude = ('related_persons',)


    autocomplete_lookup_fields = {
        'm2m': ['movies', ],
    }



@admin.register(Video)
class VideoAdmin(ImportExportModelAdmin):
    list_display = ("id",'title',"link")
    search_fields = ('id','title',"tags" )
    raw_id_fields = ['related_movies', 'related_persons', 'related_topics']
    resource_class = VideoResource

    autocomplete_lookup_fields = {
#        'fk': ['related_fk'],
        'm2m': ['related_persons',"related_movies", "related_topics", ],
    }

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("id",'name',)
    inlines = [VideoTopicInline,]
    raw_id_fields = ['movies', 'persons', 'lists',]
    


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("profile",'movie',"rating", "created_at",)
    search_fields = ('profile',"movie", 'rating', )


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ("profile",'movie',"prediction", "created_at","profile_points")







@admin.register(Article)
class ArticleAdmin(ImportExportModelAdmin):
    list_display = ("id",'name',)
    raw_id_fields = ['related_movies', 'related_persons', 'related_topics']
    resource_class = ArticleResource
