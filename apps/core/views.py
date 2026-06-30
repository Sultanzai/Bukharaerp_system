from django.views.generic import TemplateView

from apps.core.services.dashboard import financial_overview


class DashboardView(TemplateView):

    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["financial"] = financial_overview()

        return context