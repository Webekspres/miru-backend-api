from rest_framework.exceptions import APIException


class InvalidStatusTransitionError(APIException):
    status_code = 409
    default_detail = 'Transisi status tidak diizinkan.'
    default_code = 'invalid_status_transition'


class AlreadyProcessedError(APIException):
    status_code = 409
    default_detail = 'Permintaan sudah diproses sebelumnya.'
    default_code = 'already_processed'
