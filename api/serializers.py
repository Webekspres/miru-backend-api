import os

from rest_framework import serializers

from .models import *
from .services import create_setoran_with_side_effects
from .services.deposits import (
    MIN_BERAT_KG,
    build_bukti_digital,
    prepare_details_data,
    validate_nasabah_for_setoran,
    validate_petugas_for_setoran,
)

PROTECTED_USER_FIELDS = ('role', 'saldo', 'poin', 'is_active', 'is_staff', 'is_superuser')


class UserProfileSerializer(serializers.ModelSerializer):
    qr = serializers.SerializerMethodField()
    kelurahan_nama = serializers.CharField(
        source='kelurahan.kelurahan', read_only=True, default=None,
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'role', 'nama_lengkap', 'nik', 'no_hp', 'alamat',
            'kelurahan', 'kelurahan_nama', 'rt', 'rw',
            'saldo', 'poin', 'is_active', 'date_joined', 'qr', 'foto_ktp',
        ]
        read_only_fields = [
            'id', 'username', 'role', 'saldo', 'poin', 'is_active', 'date_joined', 'qr',
            'foto_ktp',
        ]
        extra_kwargs = {
            'foto_ktp': {'required': False, 'allow_null': True},
        }

    def get_qr(self, obj) -> dict:
        return {
            'id': obj.id,
            'nama_lengkap': obj.nama_lengkap,
            'no_hp': obj.no_hp,
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Decrypt NIK for display
        data['nik'] = instance.get_nik()
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    setuju_kebijakan_data = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'nama_lengkap', 'nik', 'no_hp', 'alamat',
            'kelurahan', 'rt', 'rw',
            'setuju_kebijakan_data', 'role', 'saldo', 'poin', 'is_active',
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

    def validate_setuju_kebijakan_data(self, value):
        if not value:
            raise serializers.ValidationError(
                'Anda harus menyetujui kebijakan data pribadi.'
            )
        return value

    def create(self, validated_data):
        validated_data.pop('setuju_kebijakan_data')
        from django.utils import timezone
        nik = validated_data.get('nik', '')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            nama_lengkap=validated_data['nama_lengkap'],
            nik=nik,
            no_hp=validated_data.get('no_hp', ''),
            alamat=validated_data.get('alamat', ''),
            role='nasabah',
            saldo=0,
            poin=0,
        )
        # Encrypt NIK at-rest
        if nik:
            user.encrypt_nik(nik)
            user.save(update_fields=['nik_encrypted'])
        user.setuju_kebijakan_data = True
        user.tanggal_persetujuan_kebijakan = timezone.now()
        user.save(update_fields=['setuju_kebijakan_data', 'tanggal_persetujuan_kebijakan'])
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password', None)
        return data


STAFF_ROLES = ('petugas', 'admin', 'koordinator')


class NasabahLookupSerializer(serializers.ModelSerializer):
    """Data nasabah untuk petugas (scan QR / cari nasabah)."""

    class Meta:
        model = User
        fields = ['id', 'username', 'nama_lengkap', 'no_hp', 'is_active']
        read_only_fields = fields


class UserAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=6)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'role', 'nama_lengkap', 'nik', 'no_hp',
            'alamat', 'kelurahan', 'rt', 'rw',
            'saldo', 'poin', 'is_active',
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
        nik = validated_data.get('nik', '')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        # Encrypt NIK at-rest
        if nik:
            user.encrypt_nik(nik)
            user.save(update_fields=['nik_encrypted'])
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        nik = validated_data.get('nik')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        if nik is not None:
            instance.encrypt_nik(nik)
            instance.save(update_fields=['nik', 'nik_encrypted'])
        else:
            instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password', None)
        # Decrypt NIK for display
        data['nik'] = instance.get_nik()
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
    tanggal_berlaku = serializers.DateTimeField(
        required=False,
        help_text='Tanggal harga baru mulai berlaku (min H+3 dari sekarang). '
                  'Kosongkan untuk default H+3.',
    )

    class Meta:
        model = KategoriSampah
        fields = ['id', 'nama', 'harga_beli_per_kg', 'stok_terkini_kg', 'tanggal_berlaku']
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

    def update(self, instance, validated_data):
        # Extract tanggal_berlaku (not a model field on KategoriSampah)
        tanggal_berlaku = validated_data.pop('tanggal_berlaku', None)

        # Check if price is being changed
        new_harga = validated_data.get('harga_beli_per_kg')
        old_harga = instance.harga_beli_per_kg

        if new_harga is not None and new_harga != old_harga:
            # Don't update harga_beli_per_kg on category yet — schedule instead
            validated_data.pop('harga_beli_per_kg', None)

            from api.services.price_history import (
                record_price_change,
                validate_tanggal_berlaku,
            )
            if tanggal_berlaku is not None:
                try:
                    validate_tanggal_berlaku(tanggal_berlaku)
                except ValueError as exc:
                    raise serializers.ValidationError(
                        {'tanggal_berlaku': str(exc)},
                    )

            record_price_change(
                instance, old_harga, new_harga,
                tanggal_berlaku=tanggal_berlaku,
            )

        # Update other fields (nama, dll.)
        instance = super().update(instance, validated_data)

        return instance


class RiwayatHargaSerializer(serializers.ModelSerializer):
    diubah_oleh_nama = serializers.CharField(
        source='diubah_oleh.nama_lengkap', read_only=True, default=None,
    )

    class Meta:
        model = RiwayatHarga
        fields = [
            'id', 'kategori', 'harga_lama', 'harga_baru',
            'tanggal_berlaku', 'diubah_oleh', 'diubah_oleh_nama',
        ]
        read_only_fields = fields


class DetailSetoranWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailSetoran
        fields = ['kategori', 'berat_kg']

    def validate_berat_kg(self, value):
        if value < MIN_BERAT_KG:
            raise serializers.ValidationError('Minimal 1 kg per jenis sampah.')
        return value


class DetailSetoranReadSerializer(serializers.ModelSerializer):
    kategori_nama = serializers.CharField(source='kategori.nama', read_only=True)

    class Meta:
        model = DetailSetoran
        fields = [
            'id', 'kategori', 'kategori_nama', 'berat_kg',
            'harga_saat_itu', 'subtotal',
        ]


class DetailSetoranSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailSetoran
        fields = '__all__'
        read_only_fields = ['transaksi']


class TransaksiSetoranCreateSerializer(serializers.ModelSerializer):
    details = DetailSetoranWriteSerializer(many=True)

    class Meta:
        model = TransaksiSetoran
        fields = [
            'id', 'nasabah', 'petugas', 'tanggal', 'total_nilai',
            'status', 'details',
        ]
        read_only_fields = [
            'id', 'petugas', 'tanggal', 'total_nilai', 'status',
        ]

    def validate_nasabah(self, value):
        return validate_nasabah_for_setoran(value)

    def validate(self, attrs):
        request = self.context.get('request')
        if request and self.instance is None:
            validate_petugas_for_setoran(request.user)
        return attrs

    def validate_details(self, value):
        if not value:
            raise serializers.ValidationError('Minimal satu detail setoran diperlukan.')
        return value

    def create(self, validated_data):
        details_input = validated_data.pop('details')
        details_data = prepare_details_data(details_input)

        validated_data['petugas'] = self.context['request'].user
        validated_data['status'] = 'selesai'

        return create_setoran_with_side_effects(validated_data, details_data)


class TransaksiSetoranReadSerializer(serializers.ModelSerializer):
    details = DetailSetoranReadSerializer(many=True, read_only=True)
    nasabah_nama = serializers.CharField(source='nasabah.nama_lengkap', read_only=True)
    petugas_nama = serializers.CharField(
        source='petugas.nama_lengkap', read_only=True, default=None,
    )
    poin_didapat = serializers.SerializerMethodField()
    saldo_nasabah_baru = serializers.SerializerMethodField()
    bukti_digital = serializers.SerializerMethodField()

    class Meta:
        model = TransaksiSetoran
        fields = [
            'id', 'nasabah', 'nasabah_nama', 'petugas', 'petugas_nama',
            'tanggal', 'total_nilai', 'status', 'details',
            'poin_didapat', 'saldo_nasabah_baru', 'bukti_digital',
        ]

    def get_poin_didapat(self, obj):
        return int(obj.total_nilai / 1000)

    def get_saldo_nasabah_baru(self, obj):
        obj.nasabah.refresh_from_db()
        return str(obj.nasabah.saldo)

    def get_bukti_digital(self, obj):
        return build_bukti_digital(obj)


class TransaksiSetoranCorrectionSerializer(serializers.ModelSerializer):
    """Admin-only: koreksi data transaksi setoran."""

    class Meta:
        model = TransaksiSetoran
        fields = ['total_nilai']

    def validate_total_nilai(self, value):
        if value < 0:
            raise serializers.ValidationError('Nilai total tidak boleh negatif.')
        return value

    def validate(self, attrs):
        new_total = attrs.get('total_nilai', self.instance.total_nilai)
        old_total = self.instance.total_nilai
        delta = new_total - old_total
        if delta < 0:
            nasabah = self.instance.nasabah
            if nasabah.saldo + delta < 0:
                raise serializers.ValidationError(
                    'Koreksi tidak dapat dilakukan: saldo nasabah tidak mencukupi.'
                )
            poin_delta = int(new_total / 1000) - int(old_total / 1000)
            if nasabah.poin + poin_delta < 0:
                raise serializers.ValidationError(
                    'Koreksi tidak dapat dilakukan: poin nasabah tidak mencukupi.'
                )
        return attrs

    def update(self, instance, validated_data):
        from api.services.ledger import adjust_setoran_correction

        new_total = validated_data['total_nilai']
        old_total = instance.total_nilai
        if new_total != old_total:
            adjust_setoran_correction(instance.nasabah, old_total, new_total)
            instance.total_nilai = new_total
            instance.save(update_fields=['total_nilai'])
        return instance


# Backward-compatible alias
TransaksiSetoranSerializer = TransaksiSetoranCreateSerializer


class PenjemputanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Penjemputan
        fields = ['estimasi_berat', 'alamat_jemput', 'jadwal']

    def validate_estimasi_berat(self, value):
        from .services.pickups import validate_estimasi_berat
        return validate_estimasi_berat(value)

    def validate_jadwal(self, value):
        from .services.pickups import validate_jadwal_h_plus_one
        validate_jadwal_h_plus_one(value)
        return value

    def validate(self, attrs):
        request = self.context['request']
        from .services.pickups import (
            validate_max_pickups_per_week,
            validate_nasabah_owner,
            validate_wilayah_layanan,
        )
        validate_nasabah_owner(request.user)
        validate_wilayah_layanan(request.user)
        validate_max_pickups_per_week(request.user)
        return attrs

    def create(self, validated_data):
        validated_data['nasabah'] = self.context['request'].user
        validated_data['status'] = 'menunggu'
        return Penjemputan.objects.create(**validated_data)


class PenjemputanUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Penjemputan
        fields = ['status', 'petugas', 'jadwal']

    def validate_petugas(self, value):
        if value is not None:
            from .services.pickups import validate_petugas_user
            validate_petugas_user(value)
        return value

    def validate(self, attrs):
        instance = self.instance
        request = self.context['request']
        new_status = attrs.get('status', instance.status)
        new_petugas = attrs.get('petugas', instance.petugas)

        if request.user.role not in ('admin', 'petugas'):
            raise serializers.ValidationError(
                'Anda tidak memiliki izin untuk memperbarui penjemputan.'
            )

        if 'petugas' in attrs and request.user.role != 'admin':
            raise serializers.ValidationError(
                {'petugas': ['Hanya admin yang dapat menugaskan petugas.']}
            )

        if 'status' in attrs or 'petugas' in attrs:
            from .services.pickups import validate_status_transition
            validate_status_transition(
                instance, new_status, request.user, petugas=new_petugas,
            )

        return attrs


class PickupAssignSerializer(serializers.Serializer):
    petugas_id = serializers.IntegerField()

    def validate_petugas_id(self, value):
        from .services.pickups import validate_petugas_user
        try:
            petugas = User.objects.get(pk=value)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError('Petugas tidak ditemukan.') from exc
        validate_petugas_user(petugas)
        return value


class PickupStatusActionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Penjemputan.STATUS_CHOICES)


class PenjemputanSerializer(serializers.ModelSerializer):
    nasabah_nama = serializers.CharField(source='nasabah.nama_lengkap', read_only=True)
    petugas_nama = serializers.CharField(
        source='petugas.nama_lengkap', read_only=True, default=None,
    )

    class Meta:
        model = Penjemputan
        fields = [
            'id', 'nasabah', 'nasabah_nama', 'petugas', 'petugas_nama',
            'estimasi_berat', 'alamat_jemput', 'jadwal', 'status',
        ]
        read_only_fields = fields


ALLOWED_UPLOAD_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_UPLOAD_SIZE_MB = 2


class PenarikanSaldoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PenarikanSaldo
        fields = [
            'nominal', 'metode', 'nama_bank', 'no_rekening',
            'nama_pemilik_rekening', 'lampiran_ktp',
        ]
        extra_kwargs = {
            'lampiran_ktp': {'required': False, 'allow_null': True},
        }

    def validate_nominal(self, value):
        from .services.withdrawals import validate_nominal
        return validate_nominal(value)

    def validate_lampiran_ktp(self, value):
        if value is None:
            return value
        # Validasi tipe file — hanya gambar
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ALLOWED_UPLOAD_EXTENSIONS:
            raise serializers.ValidationError(
                f'Format file tidak didukung. Gunakan: {", ".join(sorted(ALLOWED_UPLOAD_EXTENSIONS))}.'
            )
        # Validasi ukuran maksimal
        if value.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(
                f'Ukuran file maksimal {MAX_UPLOAD_SIZE_MB} MB.'
            )
        # Larang executable — cek magic bytes header
        header = value.read(4)
        value.seek(0)
        executable_magic = {b'\x4d\x5a', b'\x7fELF', b'\xca\xfe\xba\xbe', b'\xcf\xfa\xed\xfe'}
        if header[:2] in {b'MZ', b'\x7f\x45'} or header in executable_magic:
            raise serializers.ValidationError(
                'File executable tidak diizinkan untuk diunggah.'
            )
        return value

    def validate(self, attrs):
        request = self.context['request']
        if request.user.role != 'nasabah':
            raise serializers.ValidationError(
                'Hanya nasabah yang dapat mengajukan penarikan saldo.'
            )
        from .services.withdrawals import (
            validate_create_withdrawal,
            is_besar,
        )
        nominal = attrs['nominal']
        lampiran_ktp = attrs.get('lampiran_ktp')
        if is_besar(nominal) and not lampiran_ktp:
            raise serializers.ValidationError({
                'lampiran_ktp': [
                    'Penarikan ≥ Rp1.000.000 wajib melampirkan foto KTP.'
                ],
            })
        validate_create_withdrawal(request.user, nominal)
        return attrs

    def create(self, validated_data):
        validated_data['nasabah'] = self.context['request'].user
        validated_data['status'] = 'menunggu'
        return PenarikanSaldo.objects.create(**validated_data)


class PenarikanSaldoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PenarikanSaldo
        fields = ['status']

    def validate(self, attrs):
        from api.exceptions import AlreadyProcessedError

        if self.instance.status in ('selesai', 'ditolak'):
            raise AlreadyProcessedError('Penarikan saldo sudah diproses.')

        new_status = attrs.get('status', self.instance.status)
        if new_status != 'selesai':
            raise serializers.ValidationError(
                {'status': ['Status hanya dapat diubah menjadi selesai.']}
            )

        from .services.withdrawals import validate_approve_withdrawal
        validate_approve_withdrawal(self.instance)
        return attrs


class PenarikanSaldoSerializer(serializers.ModelSerializer):
    nasabah_nama = serializers.CharField(source='nasabah.nama_lengkap', read_only=True)

    class Meta:
        model = PenarikanSaldo
        fields = [
            'id', 'nasabah', 'nasabah_nama', 'nominal', 'metode',
            'nama_bank', 'no_rekening', 'nama_pemilik_rekening',
            'lampiran_ktp',
            'status', 'tanggal',
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.status == 'selesai':
            instance.nasabah.refresh_from_db()
            data['saldo_nasabah_baru'] = str(instance.nasabah.saldo)
        return data


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = ['id', 'nama', 'poin_dibutuhkan', 'stok']

    def validate_poin_dibutuhkan(self, value):
        if value <= 0:
            raise serializers.ValidationError('Poin dibutuhkan harus lebih dari 0.')
        return value

    def validate_stok(self, value):
        if value < 0:
            raise serializers.ValidationError('Stok tidak boleh negatif.')
        return value


class PenukaranPoinCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PenukaranPoin
        fields = ['reward']

    def validate(self, attrs):
        request = self.context['request']
        if request.user.role != 'nasabah':
            raise serializers.ValidationError(
                'Hanya nasabah yang dapat menukar poin.'
            )
        from .services.redemptions import validate_create_redemption
        validate_create_redemption(request.user, attrs['reward'])
        return attrs

    def create(self, validated_data):
        validated_data['nasabah'] = self.context['request'].user
        validated_data['status'] = 'menunggu'
        return PenukaranPoin.objects.create(**validated_data)


class PenukaranPoinUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PenukaranPoin
        fields = ['status']

    def validate(self, attrs):
        from api.exceptions import AlreadyProcessedError

        if self.instance.status == 'selesai':
            raise AlreadyProcessedError('Penukaran poin sudah diproses.')

        new_status = attrs.get('status', self.instance.status)
        if new_status != 'selesai':
            raise serializers.ValidationError(
                {'status': ['Status hanya dapat diubah menjadi selesai.']}
            )

        from .services.redemptions import validate_approve_redemption
        validate_approve_redemption(self.instance.nasabah, self.instance.reward)
        return attrs


class PenukaranPoinSerializer(serializers.ModelSerializer):
    reward_nama = serializers.CharField(source='reward.nama', read_only=True)
    poin_dibutuhkan = serializers.IntegerField(
        source='reward.poin_dibutuhkan', read_only=True,
    )
    nasabah_nama = serializers.CharField(source='nasabah.nama_lengkap', read_only=True)

    class Meta:
        model = PenukaranPoin
        fields = [
            'id', 'nasabah', 'nasabah_nama', 'reward', 'reward_nama',
            'poin_dibutuhkan', 'status', 'tanggal',
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.status == 'selesai':
            instance.nasabah.refresh_from_db()
            instance.reward.refresh_from_db()
            data['poin_nasabah_baru'] = instance.nasabah.poin
            data['stok_reward_baru'] = instance.reward.stok
        return data


class MitraPengepulSerializer(serializers.ModelSerializer):
    class Meta:
        model = MitraPengepul
        fields = ['id', 'nama', 'kontak']

    def validate_nama(self, value):
        qs = MitraPengepul.objects.filter(nama__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Nama mitra sudah digunakan.')
        return value


class PenjualanMitraCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PenjualanMitra
        fields = ['mitra', 'kategori', 'berat_jual_kg', 'harga_jual_per_kg']

    def validate_berat_jual_kg(self, value):
        from .services.partner_sales import validate_berat_jual
        return validate_berat_jual(value)

    def validate_harga_jual_per_kg(self, value):
        from .services.partner_sales import validate_harga_jual
        return validate_harga_jual(value)

    def validate(self, attrs):
        from .services.partner_sales import validate_stok_cukup
        validate_stok_cukup(attrs['kategori'], attrs['berat_jual_kg'])
        return attrs

    def create(self, validated_data):
        from .services.partner_sales import create_partner_sale_with_side_effects
        return create_partner_sale_with_side_effects(validated_data)


class PenjualanMitraSerializer(serializers.ModelSerializer):
    mitra_nama = serializers.CharField(source='mitra.nama', read_only=True)
    kategori_nama = serializers.CharField(source='kategori.nama', read_only=True)

    class Meta:
        model = PenjualanMitra
        fields = [
            'id', 'mitra', 'mitra_nama', 'kategori', 'kategori_nama',
            'berat_jual_kg', 'harga_jual_per_kg', 'total_penjualan', 'tanggal',
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        instance.kategori.refresh_from_db()
        data['stok_kategori_baru'] = str(instance.kategori.stok_terkini_kg)
        return data


class WilayahLayananSerializer(serializers.ModelSerializer):
    """CRUD wilayah layanan — admin/koordinator."""

    class Meta:
        model = WilayahLayanan
        fields = ['id', 'kelurahan', 'rt', 'rw', 'aktif', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_kelurahan(self, value):
        if not value.strip():
            raise serializers.ValidationError('Nama kelurahan wajib diisi.')
        return value


class KontenEdukasiSerializer(serializers.ModelSerializer):
    """CRUD konten edukasi — admin/koordinator."""

    kategori_terkait_nama = serializers.CharField(
        source='kategori_terkait.nama', read_only=True, default=None,
    )

    class Meta:
        model = KontenEdukasi
        fields = [
            'id', 'judul', 'isi', 'kategori_terkait', 'kategori_terkait_nama',
            'aktif', 'urutan', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_judul(self, value):
        if not value.strip():
            raise serializers.ValidationError('Judul wajib diisi.')
        return value

    def validate_isi(self, value):
        if not value.strip():
            raise serializers.ValidationError('Isi konten wajib diisi.')
        return value

    def validate_urutan(self, value):
        if value < 0:
            raise serializers.ValidationError('Urutan tidak boleh negatif.')
        return value


class KontenEdukasiPublicSerializer(serializers.ModelSerializer):
    """List/detail publik untuk mobile — hanya konten aktif, tanpa updated_at."""

    kategori_terkait_nama = serializers.CharField(
        source='kategori_terkait.nama', read_only=True, default=None,
    )

    class Meta:
        model = KontenEdukasi
        fields = [
            'id', 'judul', 'isi', 'kategori_terkait_nama',
            'urutan', 'created_at',
        ]


class PengaduanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pengaduan
        fields = ['jenis_pengaduan', 'keluhan']

    def validate_jenis_pengaduan(self, value):
        from .services.complaints import validate_jenis_pengaduan
        return validate_jenis_pengaduan(value)

    def validate_keluhan(self, value):
        if not value.strip():
            raise serializers.ValidationError('Keluhan wajib diisi.')
        return value

    def create(self, validated_data):
        validated_data['nasabah'] = self.context['request'].user
        validated_data['status'] = 'terbuka'
        return Pengaduan.objects.create(**validated_data)


class PengaduanUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pengaduan
        fields = ['tindak_lanjut', 'status']

    def validate(self, attrs):
        tindak_lanjut = attrs.get('tindak_lanjut', self.instance.tindak_lanjut)
        status = attrs.get('status', self.instance.status)
        from .services.complaints import validate_admin_close
        validate_admin_close(tindak_lanjut, status)
        return attrs


class AuditLogSerializer(serializers.ModelSerializer):
    user_nama = serializers.CharField(
        source='user.nama_lengkap', read_only=True, default=None,
    )

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_nama', 'action', 'model_name', 'object_id',
            'changes', 'timestamp', 'ip_address',
        ]
        read_only_fields = fields


class PengaturanInstitusiSerializer(serializers.ModelSerializer):
    class Meta:
        model = PengaturanInstitusi
        fields = [
            'nama_institusi', 'alamat', 'kontak', 'email',
            'logo_url', 'jam_operasional', 'pengumuman',
        ]

    def validate_nama_institusi(self, value):
        if not value.strip():
            raise serializers.ValidationError('Nama institusi wajib diisi.')
        return value


class PengumumanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pengumuman
        fields = ['id', 'judul', 'isi', 'aktif', 'tanggal']
        read_only_fields = fields


class NotifikasiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifikasi
        fields = ['id', 'user', 'judul', 'deskripsi', 'kategori', 'is_read', 'created_at']
        read_only_fields = ['id', 'user', 'judul', 'deskripsi', 'kategori', 'created_at']


class DeviceTokenSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    token = serializers.CharField(max_length=512)
    platform = serializers.ChoiceField(
        choices=('android', 'ios', 'web'),
        default='android',
        required=False,
    )
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate_token(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('Token tidak boleh kosong.')
        if len(value) < 20:
            raise serializers.ValidationError('Token FCM tidak valid.')
        return value


class PengaduanSerializer(serializers.ModelSerializer):
    nasabah_nama = serializers.CharField(source='nasabah.nama_lengkap', read_only=True)

    class Meta:
        model = Pengaduan
        fields = [
            'id', 'nasabah', 'nasabah_nama', 'jenis_pengaduan', 'keluhan',
            'tindak_lanjut', 'status', 'tanggal',
        ]
        read_only_fields = fields
