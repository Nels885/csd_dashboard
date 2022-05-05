from rest_framework import serializers

from .models import TagXelon

TAG_XELON_COLUMN_LIST = ['xelon', 'calibre', 'telecode', 'comments', 'created_at', 'created_by__username']


class TagXelonSerializer(serializers.ModelSerializer):
    calibre = serializers.CharField(source='get_calibre_display', read_only=True)
    telecode = serializers.CharField(source='get_telecode_display', read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    created_by = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = TagXelon
        fields = ('id', 'xelon', 'calibre', 'telecode', 'comments', 'created_at', 'created_by')
