---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
---


{% assign image_files = site.static_files | where: "infojson", true %}
{% for myimage in image_files %}
  {{ myimage.path }} =
  <p>{{ myimage.content }}</p>
{% endfor %}

aaaaa
a

====

{{ site.collections }}

xxx

{% for x in site.audio %}
 {{ x.path }}
 {{ x.title }}
 {{ x.audio }}
 
 {% assign m4a_files = site.static_files | where_exp: "item", "item.path == x.audio" %}
 {% for m4a_file in m4a_files %}
   {{ m4a_file.path }} = {{ m4a_file | inspect }}
 {% endfor %}

{% endfor %}

bbb

{{ site.static_files }}
