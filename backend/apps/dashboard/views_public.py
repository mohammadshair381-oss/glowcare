from django.views.generic import TemplateView


class HomePageView(TemplateView):
  """
  Public homepage.
  Uses the existing premium frontend design and hydrates content via /api/v1/homepage/.
  """

  template_name = "public/index.html"

