from .models import Video, List, Movie, MovieImage, Topic, Article, Rating, Prediction
from import_export import resources

class ArticleResource(resources.ModelResource):
    class Meta:
        model = Article

class VideoResource(resources.ModelResource):
    class Meta:
        model = Video