import graphene

from graphene_django.types import DjangoObjectType, ObjectType
from models import Actor, Movie


class ActorType(DjangoObjectType):
    class Meta:
        model = Actor


class MovieType(DjangoObjectType):
    class Meta:
        model = Movie


class Query(ObjectType):
    actor = graphene.Field(ActorType, id=graphene.Int())
    movie = graphene.Field(MovieType, id=graphene.Int())
    actors = graphene.List(ActorType)
    movies = graphene.List(MovieType)

    def resolve_actor(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            actor = Actor.objects.get(pk=id)
            return actor

        return None

    def resolve_movie(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            movie = Movie.objects.get(pk=id)
            return movie

        return None

    def resolve_actors(self, info, **kwargs):
        return Actor.objects.all()

    def resolve_movies(self, info, **kwargs):
        return Movie.objects.all()


class ActorInput(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String()


class MovieInput(graphene.InputObjectType):
    id = graphene.ID()
    title = graphene.String()
    actors = graphene.List(ActorInput)
    years = graphene.Int()


class CreateActor(graphene.Mutation):
    class Arguments:
        input = ActorInput(required=True)

    ok = graphene.Boolean()
    actor = graphene.Field(ActorType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        actor_instance = Actor(name=input.name)
        actor_instance.save()
        return CreateActor(ok=ok, actor=actor_instance)


class UpdateActor(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ActorInput(required=True)

    ok = graphene.Boolean()
    actor = graphene.Field(ActorType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        actor_instance = Actor.objects.get(pk=id)
        if actor_instance:
            ok = True
            actor_instance.name = input.name
            actor_instance.save()
            return UpdateActor(ok=ok, actor=actor_instance)

        return UpdateActor(ok=ok, actor=None)


class CreateMovie(graphene.Mutation):
    class Arguments:
        input = MovieInput(required=True)

    ok = graphene.Boolean()
    movie = graphene.Field(MovieType)

    @staticmethod
    def mutate(root, info, input=None):
        actors = []
        ok = True
        for actor_input in input.actors:
            actor_instance = Actor.objects.get(pk=actor_input.id)
            if actor_instance is None:
                return CreateMovie(ok=False, actor=None)
            actors.append(actor_instance)
        movie = Movie(title=input.title, years=input.years)
        movie.save()
        movie.actors.set(actors)
        return CreateMovie(ok=ok, movie=movie)


class UpdateMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = MovieInput(required=True)

    ok = graphene.Boolean()
    movie = graphene.Field(MovieType)

    @staticmethod
    def mutate(root, info, id, input):
        ok = False
        movie = Movie.objects.get(pk=id)
        if movie:
            actors = []
            ok = True
            for actor_input in input.actors:
                actor_instance = Actor.objects.get(pk=actor_input.id)
                if actor_instance is None:
                    return CreateMovie(ok=False, actor=None)
                actors.append(actor_instance)
            movie = Movie(title=input.title, years=input.years)
            movie.save()
            movie.actors.set(actors)
            UpdateMovie(ok=ok, movie=movie)
        return UpdateMovie(ok=ok, movie=None)