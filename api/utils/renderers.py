from rest_framework.renderers import JSONRenderer

from .response import get_action_message, success_envelope

SKIP_ENVELOPE_PREFIXES = (
    '/api/schema',
    '/api/docs',
    '/api/redoc',
)


class EnvelopeJSONRenderer(JSONRenderer):
    """Wraps all DRF JSON responses in the standard MIRU envelope."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context is None:
            return super().render(data, accepted_media_type, renderer_context)

        request = renderer_context.get('request')
        response = renderer_context.get('response')

        if request and any(request.path.startswith(p) for p in SKIP_ENVELOPE_PREFIXES):
            return super().render(data, accepted_media_type, renderer_context)

        if isinstance(data, dict) and 'success' in data and 'status_code' in data:
            return super().render(data, accepted_media_type, renderer_context)

        if response is None:
            return super().render(data, accepted_media_type, renderer_context)

        status_code = response.status_code

        if status_code == 204:
            envelope = success_envelope(
                data=None,
                message='Data berhasil dihapus.',
                status_code=204,
                request=request,
            )
            return super().render(envelope, accepted_media_type, renderer_context)

        view = renderer_context.get('view')
        action = getattr(view, 'action', None) if view else None
        method = request.method if request else 'GET'
        message = get_action_message(action, method, status_code)

        envelope = success_envelope(
            data=data,
            message=message,
            status_code=status_code,
            request=request,
        )
        return super().render(envelope, accepted_media_type, renderer_context)
