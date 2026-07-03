from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role', 'nama_lengkap', 'nik', 'no_hp', 'alamat', 'saldo', 'poin']
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class KategoriSampahSerializer(serializers.ModelSerializer):
    class Meta:
        model = KategoriSampah
        fields = '__all__'

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
        transaksi = TransaksiSetoran.objects.create(**validated_data)
        
        total_nilai = 0
        total_poin = 0
        
        for detail in details_data:
            detail_obj = DetailSetoran.objects.create(transaksi=transaksi, **detail)
            total_nilai += detail_obj.subtotal
            
            # Update Stok
            kat = detail['kategori']
            kat.stok_terkini_kg += detail['berat_kg']
            kat.save()
            
        transaksi.total_nilai = total_nilai
        transaksi.save()
        
        # Update User Saldo & Poin (1 poin per Rp1000)
        nasabah = transaksi.nasabah
        nasabah.saldo += total_nilai
        nasabah.poin += int(total_nilai / 1000)
        nasabah.save()
        
        return transaksi

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
