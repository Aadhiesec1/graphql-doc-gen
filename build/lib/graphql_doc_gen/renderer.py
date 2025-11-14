import json
from typing import Dict, Any, List, Optional
from jinja2 import Template

def _unwrap_type(t: Dict[str, Any]) -> str:
    # Unwrap NON_NULL and LIST wrappers to readable type string
    if not t:
        return "Unknown"
    kind = t.get("kind")
    if kind == "NON_NULL":
        return f"{_unwrap_type(t.get('ofType'))}!"
    if kind == "LIST":
        return f"[{_unwrap_type(t.get('ofType'))}]"
    # base case
    return t.get("name") or "Unknown"

def format_args(args: List[Dict[str, Any]]) -> List[str]:
    out = []
    for a in args or []:
        t = _unwrap_type(a.get("type"))
        default = a.get("defaultValue")
        def_str = f" = {default}" if default is not None else ""
        out.append(f"- **{a['name']}**: `{t}`{def_str}")
    return out

def generate_markdown(schema: Dict[str, Any]) -> str:
    types = schema["__schema"]["types"]
    lines = ["# GraphQL API Documentation", ""]
    for t in types:
        if t["name"].startswith("__"):
            continue
        lines.append(f"## {t['name']}")
        if t.get("description"):
            lines.append(t["description"])
        # fields
        if t.get("fields"):
            lines.append("")
            lines.append("### Fields")
            for f in t["fields"]:
                ftype = _unwrap_type(f["type"])
                lines.append(f"- **{f['name']}**: `{ftype}`")
                if f.get("description"):
                    lines.append(f"  - {f['description']}")
                if f.get("args"):
                    lines.append("  - Arguments:")
                    for arg_line in format_args(f["args"]):
                        lines.append(f"    {arg_line}")
        # enum
        if t.get("enumValues"):
            lines.append("")
            lines.append("### Enum Values")
            for ev in t["enumValues"]:
                if ev.get("description"):
                    lines.append(f"- `{ev['name']}` — {ev['description']}")
                else:
                    lines.append(f"- `{ev['name']}`")
        lines.append("")  # spacing
    return "\n".join(lines)

HTML_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>GraphQL API Documentation</title>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <style>
    body { font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; margin: 2rem; line-height: 1.5; color: #111; }
    h1 { font-size: 1.8rem; margin-bottom: 0.5rem; }
    h2 { font-size: 1.4rem; margin-top: 1.2rem; }
    pre, code { background:#f6f8fa; padding: 0.15rem 0.35rem; border-radius:4px; }
    .type { margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #eee; }
    .arg { margin-left: 1rem; }
    nav { position: fixed; right: 1rem; top: 1rem; max-width: 220px; border-left: 1px solid #eee; padding-left: 0.5rem; }
    main { max-width: 900px; }
    @media (max-width: 900px) { nav { display:none; } }
  </style>
</head>
<body>
  <nav>
    <strong>Types</strong>
    <ul>
      {% for t in types %}
      <li><a href="#{{ t.name }}">{{ t.name }}</a></li>
      {% endfor %}
    </ul>
  </nav>
  <main>
    <h1>GraphQL API Documentation</h1>
    {% for t in types %}
    <section id="{{ t.name }}" class="type">
      <h2>{{ t.name }}</h2>
      {% if t.description %}<p>{{ t.description }}</p>{% endif %}
      {% if t.fields %}
        <h3>Fields</h3>
        <ul>
        {% for f in t.fields %}
          <li><strong>{{ f.name }}</strong>: <code>{{ f.type }}</code>
            {% if f.description %}<div>{{ f.description }}</div>{% endif %}
            {% if f.args %}
              <div class="arg"><em>Arguments:</em>
                <ul>
                  {% for a in f.args %}
                    <li><strong>{{ a.name }}</strong>: <code>{{ a.type }}</code>{% if a.default %} = {{ a.default }}{% endif %}</li>
                  {% endfor %}
                </ul>
              </div>
            {% endif %}
          </li>
        {% endfor %}
        </ul>
      {% endif %}
      {% if t.enumValues %}
        <h3>Enum Values</h3>
        <ul>
          {% for ev in t.enumValues %}
            <li><code>{{ ev.name }}</code>{% if ev.description %} — {{ ev.description }}{% endif %}</li>
          {% endfor %}
        </ul>
      {% endif %}
    </section>
    {% endfor %}
  </main>
</body>
</html>
"""

def generate_html(schema: Dict[str, Any]) -> str:
    # Build a trimmed representation suitable for template rendering
    types_clean = []
    for t in schema["__schema"]["types"]:
        if t["name"].startswith("__"):
            continue
        fc = {
            "name": t["name"],
            "description": t.get("description"),
            "fields": [],
            "enumValues": t.get("enumValues") or []
        }
        for f in t.get("fields") or []:
            fc["fields"].append({
                "name": f["name"],
                "type": _unwrap_type(f["type"]),
                "description": f.get("description"),
                "args": [{"name": a["name"], "type": _unwrap_type(a["type"]), "default": a.get("defaultValue")} for a in (f.get("args") or [])]
            })
        types_clean.append(fc)
    tpl = Template(HTML_TEMPLATE)
    return tpl.render(types=types_clean)

def generate_pdf(html: str, output_path: str):
    try:
        from weasyprint import HTML
    except ImportError:
        raise RuntimeError(
            "PDF output requires the 'weasyprint' dependency.\n"
            "Install it with:\n\n"
            "    pip install graphql-doc-gen[pdf]\n"
        )
    HTML(string=html).write_pdf(output_path)
