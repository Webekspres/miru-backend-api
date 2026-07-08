from rest_framework import serializers

from .models import *
from .services import create_setoran_with_side_effects

PROTECTED_USER_FIELDS = ('role', 'saldo', 'poin', 'is_active', 'is_staff', 'is_superuser')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'role', 'nama_lengkap', 'nik', 'no_hp', 'alamat',
            'saldo', 'poin', 'is_active', 'date_joined',
        ]
        read_only_fields = [
            'id', 'username', 'role', 'saldo', 'poin', 'is_active', 'date_joined',
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'nama_lengkap', 'nik', 'no_hp', 'alamat',
            'role', 'saldo', 'poin', 'is_active',
        ]
        read_only_fields = ['id', 'role', 'saldo', 'poin', 'is_active']

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('Username sudah digunakan.')
        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError('Password minimal 6 karakter.')
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            nama_lengkap=validated_data['nama_lengkap'],
            nik=validated_data.get('nik', ''),
            no_hp=validated_data.get('no_hp', ''),
            alamat=validated_data.get('alamat', ''),
            role='nasabah',
            saldo=0,
            poin=0,
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password', None)
        return data


STAFF_ROLES = ('petugas', 'admin', 'koordinator')


class UserAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=6)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'role', 'nama_lengkap', 'nik', 'no_hp',
            'alamat', 'saldo', 'poin', 'is_active',
        ]
        read_only_fields = ['id']

    def validate_username(self, value):
        qs = User.objects.filter(username__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Username sudah digunakan.')
        return value

    def validate(self, attrs):
        if self.instance is None and not attrs.get('password'):
            raise serializers.ValidationError({'password': ['Password wajib diisi.']})
        return attrs

    def validate_role(self, value):
        if value not in dict(User.ROLE_CHOICES):
            raise serializers.ValidationError('Role tidak valid.')
        if self.instance is None and value == 'nasabah':
            raise serializers.ValidationError(
                'Nasabah didaftarkan melalui registrasi publik.'
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.setdefault('saldo', 0)
        validated_data.setdefault('poin', 0)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password', None)
        return data


class UserSerializer(serializers.ModelSerializer):
    """Backward-compatible alias used by admin views."""
    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'role', 'nama_lengkap', 'nik', 'no_hp',
            'alamat', 'saldo', 'poin', 'is_active',
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class KategoriSampahSerializer(serializers.ModelSerializer):
    class Meta:
        model = KategoriSampah
        fields = ['id', 'nama', 'harga_beli_per_kg', 'stok_terkini_kg']
        read_only_fields = ['id', 'stok_terkini_kg']

    def validate_nama(self, value):
        qs = KategoriSampah.objects.filter(nama__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Nama kategori sudah digunakan.')
        return value

    def validate_harga_beli_per_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError('Harga harus lebih dari 0.')
        return value


class DetailSetoranSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailSetoran
        fields = '__all__'
        read_only_fields = ['transaksi']


class TransaksiSetoranSerializer(serializers.ModelSerializer):
    details = DetailSetoranSerializer(many=True, write_only=True)

    class Meta:
        model = TransaksiSetoran
        fields = '__all__'

    def create(self, validated_data):
        details_data = validated_data.pop('details', [])
        return create_setoran_with_side_effects(validated_data, details_data)


class PenjemputanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Penjemputan
        fields = '__all__'


class PenarikanSaldoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PenarikanSaldo
        fields = '__all__'


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = '__all__'


class PenukaranPoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = PenukaranPoin
        fields = '__all__'


class MitraPengepulSerializer(serializers.ModelSerializer):
    class Meta:
        model = MitraPengepul
        fields = '__all__'


class PenjualanMitraSerializer(serializers.ModelSerializer):
    class Meta:
        model = PenjualanMitra
        fields = '__all__'


class PengaduanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pengaduan
        fields = '__all__'
