<span id="-news" class="legacy-anchor"></span>

## 🔥 News
{: #news tabindex="-1" }

{% assign recent_count = 4 %}
{% assign earlier_count = site.data.news.size | minus: recent_count %}
{% for item in site.data.news limit: recent_count -%}
- *{{ item.date }}*: {{ item.text }}
{% endfor %}

{% if earlier_count > 0 %}
<details class="news-archive" markdown="1">
<summary>Earlier news ({{ earlier_count }})</summary>

{% for item in site.data.news offset: recent_count -%}
- *{{ item.date }}*: {{ item.text }}
{% endfor %}
</details>
{% endif %}
