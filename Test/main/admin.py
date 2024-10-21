from django.contrib import admin
from .models import UserProfiles, TradingData, DataEntry, DateLog, Task, Template

class UserProfilesAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'api_key')
    search_fields = ('name', 'api_key')

class TradingDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'uploaded_file')
    search_fields = ('user__username',)

class DataEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'symbol', 'amount_usdt', 'is_completed')
    list_filter = ('is_completed',)
    search_fields = ('symbol', 'user__username')

class DateLogAdmin(admin.ModelAdmin):
    list_display = ('date', 'task_id')
    search_fields = ('task_id',)

class TaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_running')
    list_filter = ('is_running',)
    search_fields = ('user__username',)

class TemplateAdmin(admin.ModelAdmin):
    list_display = ('user', 'name_exchange', 'name', 'symbol', 'start_date', 'end_date')
    search_fields = ('name', 'symbol', 'user__username')
    list_filter = ('name_exchange', 'asset_type')

admin.site.register(UserProfiles, UserProfilesAdmin)
admin.site.register(TradingData, TradingDataAdmin)
admin.site.register(DataEntry, DataEntryAdmin)
admin.site.register(DateLog, DateLogAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Template, TemplateAdmin)