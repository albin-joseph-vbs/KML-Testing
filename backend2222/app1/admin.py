from django.contrib import admin
from .models import (
    HQ, Factory, Department, HanContent, HanTrainingContent, Line, Level, Days,
    EmployeeMaster, MultiSkilling, RefreshmentTraining, Score, ShoContent, ShoTrainingContent, Station, OperatorSkill, TestSession, TrainingReport, TrainingTopic, OperatorTraining,
    MonthlyAssignment, OperatorLevelTracking, OperatorLevelEmailTracking, TrackingEmail,
    Machine, MachineAllocation, MachineAllocationTrackingEmail,
    SkillTraining, SubTopic, SubTopicContent, TrainingContent,
    LevelTwoProduction, LevelTwoLine, LevelTwoSubStation, EmployeeLevelAssignment,
    LevelTwoTraineeInfo, LevelTwoTrainingTopic, LevelTwoOJTDay, LevelTwoOJTScore,
    LevelTwoQuality, LevelTwoQualityLine, LevelTwoQATraineeInfo,
    LevelTwoQATrainingTopic, LevelTwoQAOJTDay, LevelTwoQAOJTScore,
    LevelThreeProduction, LevelThreeLine, LevelThreeSubStation,
    LevelThreeTraineeInfo, LevelThreeTrainingTopic, LevelThreeOJTDay, LevelThreeOJTScore,
    LevelThreeQuality, LevelThreeQualityLine, LevelThreeQATraineeInfo,
    LevelThreeQATrainingTopic, LevelThreeQAOJTDay, LevelThreeQAOJTScore,
    ARVRTrainingContent, MCQQuestion, BiometricAttendance, UnifiedDefectReport
)

# Basic registrations
admin.site.register(HQ)
admin.site.register(Factory)
admin.site.register(Department)
admin.site.register(Line)
admin.site.register(Level)
admin.site.register(Days)

admin.site.register(EmployeeMaster)
admin.site.register(Station)
admin.site.register(OperatorSkill)
admin.site.register(TrainingTopic)
admin.site.register(OperatorTraining)
admin.site.register(MonthlyAssignment)

admin.site.register(OperatorLevelTracking)
admin.site.register(OperatorLevelEmailTracking)
admin.site.register(TrackingEmail)

admin.site.register(Machine)
admin.site.register(MachineAllocation)
admin.site.register(MachineAllocationTrackingEmail)

admin.site.register(SkillTraining)
admin.site.register(SubTopic)
admin.site.register(SubTopicContent)
admin.site.register(TrainingContent)

admin.site.register(LevelTwoProduction)
admin.site.register(LevelTwoLine)
admin.site.register(LevelTwoSubStation)
admin.site.register(EmployeeLevelAssignment)

admin.site.register(LevelTwoTraineeInfo)
admin.site.register(LevelTwoTrainingTopic)
admin.site.register(LevelTwoOJTDay)
admin.site.register(LevelTwoOJTScore)

admin.site.register(LevelTwoQuality)
admin.site.register(LevelTwoQualityLine)
admin.site.register(LevelTwoQATraineeInfo)
admin.site.register(LevelTwoQATrainingTopic)
admin.site.register(LevelTwoQAOJTDay)
admin.site.register(LevelTwoQAOJTScore)

admin.site.register(LevelThreeProduction)
admin.site.register(LevelThreeLine)
admin.site.register(LevelThreeSubStation)

admin.site.register(LevelThreeTraineeInfo)
admin.site.register(LevelThreeTrainingTopic)
admin.site.register(LevelThreeOJTDay)
admin.site.register(LevelThreeOJTScore)

admin.site.register(LevelThreeQuality)
admin.site.register(LevelThreeQualityLine)
admin.site.register(LevelThreeQATraineeInfo)
admin.site.register(LevelThreeQATrainingTopic)
admin.site.register(LevelThreeQAOJTDay)
admin.site.register(LevelThreeQAOJTScore)

admin.site.register(ARVRTrainingContent)
admin.site.register(MCQQuestion)
admin.site.register(BiometricAttendance)


admin.site.register(MultiSkilling)
admin.site.register(RefreshmentTraining)


admin.site.register(TrainingReport)
admin.site.register(UnifiedDefectReport)


admin.site.register(Score)
admin.site.register(TestSession)



admin.site.register(HanContent)
admin.site.register(HanTrainingContent)
admin.site.register(ShoContent)
admin.site.register(ShoTrainingContent)






from django.contrib import admin
from .models import QuestionPaper, Question

@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    list_display = ('name','id')
    search_fields = ('name',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'question_paper', 'correct_index')
    list_filter = ('question_paper',)
    search_fields = ('question_text',)


from django.contrib import admin
from .models import MainDepartment, MainLine, SubLine

# Inline for SubLine (Third level)
class SubLineInline(admin.TabularInline):
    model = SubLine
    extra = 1

# Inline for MainLine (Second level)
class MainLineInline(admin.TabularInline):
    model = MainLine
    extra = 1

# Admin for MainDepartment with inline MainLine
class MainDepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [MainLineInline]

# Admin for MainLine with inline SubLine
class MainLineAdmin(admin.ModelAdmin):
    list_display = ['name', 'department']
    list_filter = ['department']
    inlines = [SubLineInline]

# Admin for SubLine
class SubLineAdmin(admin.ModelAdmin):
    list_display = ['name', 'main_line']
    list_filter = ['main_line']

# Register all
admin.site.register(MainDepartment, MainDepartmentAdmin)
admin.site.register(MainLine, MainLineAdmin)
admin.site.register(SubLine, SubLineAdmin)


from django.contrib import admin
from .models import UploadedFile

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_at']




from .models import User
admin.site.register(User)







from django.contrib import admin
from .models import ManagementReview

@admin.register(ManagementReview)
class ManagementReviewAdmin(admin.ModelAdmin):
    list_display = (
        'month_year',
        'new_operators_joined',
        'new_operators_trained',
        'total_training_plans',
        'total_trainings_actual',
        'total_defects_msil',
        'ctq_defects_msil',
        'total_defects_tier1',
        'ctq_defects_tier1',
        'total_internal_rejection',
        'ctq_internal_rejection',
    )
    list_filter = ('month_year',)
    search_fields = ('month_year',)
    ordering = ('-month_year',)
