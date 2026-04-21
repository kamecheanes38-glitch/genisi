FROM searxng/searxng:latest

# إعداد المنفذ الخاص بـ Hugging Face
ENV SEARXNG_PORT=7860
ENV SEARXNG_SETTINGS_PATH=/etc/searxng/settings.yml

# نسخ ملف الإعدادات
COPY settings.yml /etc/searxng/settings.yml

# ضمان الصلاحيات لتجنب الـ Crash
USER root
RUN chmod -R 777 /etc/searxng

EXPOSE 7860

CMD ["searxng"]
