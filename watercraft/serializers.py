from rest_framework import serializers
from .models import Watercraft


class WatercraftSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    display_image = serializers.SerializerMethodField()

    class Meta:
        model = Watercraft
        fields = [
            'id', 'name', 'type', 'type_display', 'description',
            'image', 'image_url', 'display_image',
            'price_per_hour', 'passenger_capacity', 'is_available',
            'location', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_display_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            url = obj.image.url
            return request.build_absolute_uri(url) if request else url
        return obj.image_url or ''
