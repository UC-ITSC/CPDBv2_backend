from django.contrib import admin
from .models import DocumentCrawler, DocumentCloudSearchQuery


class DocumentCrawlerAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'num_documents', 'num_new_documents', 'num_updated_documents', 'timestamp')
    list_display = ('id', 'num_documents', 'num_new_documents', 'num_updated_documents', 'timestamp')

    def has_add_permission(self, request):
        return False  # pragma: no cover

    def has_delete_permission(self, request, obj=None):
        return False  # pragma: no cover


admin.site.register(DocumentCrawler, DocumentCrawlerAdmin)
admin.site.register(DocumentCloudSearchQuery)
