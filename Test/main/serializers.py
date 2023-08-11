from rest_framework import serializers


class FormDataSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=255)
    interval = serializers.FloatField()
    bound = serializers.CharField(max_length=255)
    bound_unit = serializers.CharField(max_length=5)
    start_data = serializers.CharField(max_length=255)
    end_data = serializers.CharField(max_length=255)
