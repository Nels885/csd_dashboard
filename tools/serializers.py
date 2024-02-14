from rest_framework import serializers

from .models import TagXelon, RaspiTime


TAG_XELON_COLUMN_LIST = ['xelon', 'calibre', 'telecode', 'comments', 'created_at', 'created_by__username']


class TagXelonSerializer(serializers.ModelSerializer):
    calibre = serializers.CharField(source='get_calibre_display', read_only=True)
    telecode = serializers.CharField(source='get_telecode_display', read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    created_by = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = TagXelon
        fields = ('id', 'xelon', 'calibre', 'telecode', 'comments', 'created_at', 'created_by')


RASPI_TIME_COLUMN_LIST = ['name', 'type', 'date', 'start_time', 'end_time', 'duration', 'xelon']


class RaspiTimeSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format='%Y-%m-%d')
    start_time = serializers.TimeField(format='%H:%M:%S', read_only=True)
    end_time = serializers.TimeField(format='%H:%M:%S', read_only=True)
    duration = serializers.IntegerField(default="", read_only=True)

    class Meta:
        model = RaspiTime
        fields = ('id', 'name', 'type', 'date', 'start_time', 'end_time', 'duration', 'xelon')
