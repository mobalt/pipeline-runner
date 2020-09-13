from jinja2 import Environment, FileSystemLoader, StrictUndefined


class TemplateLoader:
    def __init__(self, templates_folder):
        self.env = Environment(
            loader=FileSystemLoader(templates_folder), undefined=StrictUndefined
        )

    def render(self, template_name, variables):
        t = self.env.get_template(template_name)
        return t.render(**variables)
