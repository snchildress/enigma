from django.contrib import admin

from source import models


class SecretAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid', 'create_timestamp', 'update_timestamp')
    ### Do not display Messages in the admin, as they appear in plain text ###
    exclude = ('message',)

admin.site.register(models.Secret, SecretAdmin)
