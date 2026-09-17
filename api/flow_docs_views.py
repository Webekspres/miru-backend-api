from django.views.generic import TemplateView

from .flow_docs_data import DEMO_USERS, FLOW_SECTIONS, get_demo_user, get_nav_groups


class FlowDocsView(TemplateView):
    template_name = 'api/flow_docs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sections = []
        for section in FLOW_SECTIONS:
            item = dict(section)
            role_key = section.get('demo_user')
            item['demo_user_data'] = get_demo_user(role_key) if role_key else None
            endpoints = []
            for ep in section.get('endpoints', []):
                ep_item = dict(ep)
                ep_role = ep.get('demo_user') or role_key
                ep_item['demo_user_data'] = get_demo_user(ep_role) if ep_role else None
                endpoints.append(ep_item)
            item['endpoints'] = endpoints
            sections.append(item)
        context['sections'] = sections
        context['demo_users'] = DEMO_USERS
        context['nav_groups'] = get_nav_groups()
        context['base_url'] = self.request.build_absolute_uri('/').rstrip('/')
        return context
