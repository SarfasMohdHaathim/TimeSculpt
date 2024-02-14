from rest_framework import serializers
from .models import Watch,WatchImage,OrderPlaced,Payment,Address
from api.models import User

class WatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watch
        fields = '__all__'

    def create(self, validated_data):
        watch_thumbnail = validated_data.pop('watch_thumbnail', None)
        instance = Watch.objects.create(**validated_data)
        if watch_thumbnail:
            instance.watch_thumbnail = watch_thumbnail
            instance.save()
        return instance
    
    def update(self, instance, validated_data):
        try:
            print('=========== Update Method Called ===========')
            watch_thumbnail = validated_data.pop('watch_thumbnail', None)
            
            for key, value in validated_data.items():
                print(f'Setting {key} to {value}')
                setattr(instance, key, value)
            
            instance.save()
            
            if watch_thumbnail:
                print('Updating watch_thumbnail')
                instance.watch_thumbnail = watch_thumbnail
                instance.save()
        except Exception as e:
            print(f'Error in update method: {e}')
            for key, value in validated_data.items():
                print(f'Setting {key} to {value}')
                setattr(instance, key, value)
            instance.save()
    
        return instance



class WatchImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchImage
        fields = '__all__'

    def create(self, validated_data):
        return WatchImage.objects.create(**validated_data)

    def delete(self, instance):
        instance.delete()



class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['country', 'street_address', 'city', 'zipcode', 'phone']


class UserSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    class Meta:
        model = User
        fields = ['id', 'username','email', 'address']

class OrderPlacedSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer()
    user = UserSerializer()
    product=WatchSerializer()

    class Meta:
        model = OrderPlaced
        fields = ['id', 'user', 'product', 'ordered_date', 'payment']