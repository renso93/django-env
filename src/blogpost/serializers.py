from rest_framework import serializers
from .models import BlogPost, Category, Tag, CustomUser


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'avatar']


class BlogPostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    # use slug related fields for more friendly API (read/write via slug)
    category = serializers.SlugRelatedField(slug_field='slug', queryset=Category.objects.all(), allow_null=True, required=False)
    tags = serializers.SlugRelatedField(many=True, slug_field='slug', queryset=Tag.objects.all(), required=False)
    featured_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'content', 'author', 'category', 'tags',
            'status', 'featured_image', 'created_at', 'updated_at', 'views'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'views']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        request = self.context.get('request')
        validated_data['author'] = request.user
        post = BlogPost.objects.create(**validated_data)
        if tags:
            # tags are Tag instances because SlugRelatedField returns model instances
            post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        if tags is not None:
            instance.tags.set(tags)
        return instance
