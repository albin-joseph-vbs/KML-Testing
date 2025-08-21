import re
import pandas as pd
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework_simplejwt.tokens import RefreshToken


ROLE_CHOICES = [
    ('developer', 'Developer'),
    ('management', 'Management'),
    ('admin', 'Admin'),
    ('instructor', 'Instructor'),
    ('operator', 'Operator')
]

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, employeeid, first_name, last_name, role, hq, factory, department, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            employeeid=employeeid,
            first_name=first_name,
            last_name=last_name,
            role=role,
            hq=hq,
            factory=factory,
            department=department,
            is_active=True  
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, employeeid, first_name, last_name, role, hq, factory, department, password=None):
        user = self.create_user(
            email=email,
            employeeid=employeeid,
            first_name=first_name,
            last_name=last_name,
            role=role,
            hq=hq,
            factory=factory,
            department=department,
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True  
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    employeeid = models.CharField(max_length=10, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='') 

    hq = models.CharField(max_length=50, blank=True, null=True)
    factory = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True)

    status = models.BooleanField(default=True)  

    # Required Django Fields
    is_active = models.BooleanField(default=True)  
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['employeeid', 'first_name', 'last_name', 'role', 'hq', 'factory', 'department']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }




from django.db import models
# Level Choices
LEVEL_CHOICES = [
    ('level_1', 'Level 1'),
    ('level_2', 'Level 2'),
    ('level_3', 'Level 3'),
    ('level_4', 'Level 4'),
]


class HQ(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Factory(models.Model):
    hq = models.ForeignKey(HQ, on_delete=models.CASCADE, related_name='factories')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.hq.name})"


class Department(models.Model):
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.factory.name})"


class Line(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='lines')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.department.name})"


class Level(models.Model):
    line = models.ForeignKey(Line, on_delete=models.CASCADE, related_name='levels')
    name = models.CharField(max_length=20, choices=LEVEL_CHOICES)

    def __str__(self):
        return f"{self.get_name_display()} ({self.line.name})"






class Days(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='days')
    day = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.day} - {self.level.get_name_display()}"
    


















class EmployeeMaster(models.Model):
    pay_code = models.CharField(max_length=20, unique=True)
    card_no = models.CharField(max_length=20, unique=True)
    sex = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    birth_date = models.DateField()
    name = models.CharField(max_length=100)
    guardian_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    section = models.CharField(max_length=100)
    desig_category = models.CharField(max_length=100, blank=True, null=True)
    joining_date = models.DateField()
    auth_shift = models.CharField(max_length=50)
    shift_type = models.CharField(max_length=50)
    shift_pattern = models.CharField(max_length=50)
    first_weekly_off = models.CharField(max_length=10)
    second_weekly_off = models.CharField(max_length=10, blank=True, null=True)
    second_weekly_off_fh = models.CharField(max_length=10, blank=True, null=True)
    ot_allowed_rate = models.BooleanField(default=False)
    round_the_clock = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    





# class Operator(models.Model):
#     name = models.CharField(max_length=100)
#     code = models.CharField(max_length=50, unique=True)
#     date_of_joining = models.DateField()

#     def __str__(self):
#         return f"{self.name} ({self.code})"


# Top Level: Departments (like Production, Quality)
class MainDepartment(models.Model):
    name = models.CharField(max_length=100)  # Example: 'Production', 'Quality'

    def __str__(self):
        return self.name


# Second Level: Main Lines (like Weld Shop Line-1, Assembly Line-1)
class MainLine(models.Model):
    name = models.CharField(max_length=100)  # Example: 'Weld Shop Line-1 (Y17)'
    department = models.ForeignKey(MainDepartment, on_delete=models.CASCADE, related_name='main_lines')

    def __str__(self):
        return self.name


# Third Level: Sub Lines (like Bending Line, RSB Line)
class SubLine(models.Model):
    name = models.CharField(max_length=100)  # Example: 'Bending Line', 'FSB Line'
    main_line = models.ForeignKey(MainLine, on_delete=models.CASCADE, related_name='sub_lines')

    def __str__(self):
        return self.name



class Station(models.Model):
    sub_line = models.ForeignKey(SubLine, on_delete=models.CASCADE, related_name='stations',default='')
    station_number = models.IntegerField(unique=True)
    skill = models.CharField(max_length=100,default='')
    minimum_skill_required = models.CharField(max_length=100)
    min_operator_required = models.IntegerField()

    def __str__(self):
        return f" {self.skill}"


class OperatorSkill(models.Model):
    operator = models.ForeignKey(EmployeeMaster, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    skill_level = models.CharField(max_length=100)
    sequence = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('operator', 'station')

    def __str__(self):
        return f"{self.operator} - {self.station} ({self.skill_level})"



class TrainingTopic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class OperatorTraining(models.Model):
    operator = models.ForeignKey(EmployeeMaster, on_delete=models.CASCADE)
    topic = models.ForeignKey(TrainingTopic, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('operator', 'topic')

    def __str__(self):
        return f"{self.operator} - {self.topic}"


class MonthlyAssignment(models.Model):
    operator = models.ForeignKey(EmployeeMaster, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    skill_level = models.CharField(max_length=10)
    month = models.DateField()

    class Meta:
        unique_together = ('operator', 'station', 'month')

    def __str__(self):
        return f"{self.operator} assigned to {self.station} ({self.month})"
    





from django.db import models
from datetime import timedelta, date

class OperatorLevelTracking(models.Model):
    operator = models.ForeignKey(EmployeeMaster, on_delete=models.CASCADE, related_name='level_trackings')
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    day = models.PositiveIntegerField()  # e.g., Day 11, Day 15

    @property
    def milestone_date(self):
        if self.operator.joining_date:
            return self.operator.joining_date + timedelta(days=self.day)
        return None

    def is_today_milestone(self):
        return self.milestone_date == date.today()

    def __str__(self):
        return f"{self.operator.name} - {self.level.name} - Day {self.day}"







from django.db import models
from datetime import timedelta, date

class OperatorLevelEmailTracking(models.Model):
    operator = models.ForeignKey(EmployeeMaster, on_delete=models.CASCADE, related_name='email_level_trackings')
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    day = models.PositiveIntegerField()

    @property
    def milestone_date(self):
        if self.operator.joining_date:
            return self.operator.joining_date + timedelta(days=self.day)
        return None

    def is_today_milestone(self):
        return self.milestone_date == date.today()

    def __str__(self):
        return f"{self.operator.name} - {self.level.name} - Day {self.day}"


class TrackingEmail(models.Model):
    tracking = models.ForeignKey(OperatorLevelEmailTracking, on_delete=models.CASCADE, related_name='emails')
    email = models.EmailField()

    def __str__(self):
        return self.email









class Machine(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='machines/', null=True, blank=True)
    level = models.IntegerField()
    process = models.CharField(max_length=100, null=True, blank=True)  # Skill required
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return self.name 
    



class MachineAllocationTrackingEmail(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email




from django.core.exceptions import ValidationError

class MachineAllocation(models.Model):
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    employee = models.ForeignKey(EmployeeMaster, on_delete=models.CASCADE)
    allocated_at = models.DateTimeField(auto_now_add=True)
    approval_status = models.CharField(
        max_length=10,
        choices=APPROVAL_STATUS_CHOICES,
        default='approved'
    )

    def __str__(self):
        return f"{self.machine.name} → {self.employee.name}"

    











class SkillTraining(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='skill_trainings')
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.title} - {self.level.get_name_display()}"


class SubTopic(models.Model):
    skill_training = models.ForeignKey(SkillTraining, on_delete=models.CASCADE, related_name='subtopics')
    day = models.ForeignKey(Days, on_delete=models.CASCADE, related_name='subtopics')
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class SubTopicContent(models.Model):
    subtopic = models.ForeignKey(SubTopic, on_delete=models.CASCADE, related_name='subtopiccontents')
    title = models.CharField(max_length=100,default='')


class TrainingContent(models.Model):
    subtopic_content = models.ForeignKey(SubTopicContent, on_delete=models.CASCADE, related_name='contents',default='')
    description = models.TextField()
    training_file = models.FileField(upload_to='training_files/', blank=True, null=True)
    url_link = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"Content for {self.subtopic_content.title}"
    



from django.db import models

class LevelTwoProduction(models.Model):
    name = models.CharField(max_length=100, default="Production")

    def __str__(self):
        return self.name


class LevelTwoLine(models.Model):
    name = models.CharField(max_length=100)
    production = models.ForeignKey(LevelTwoProduction, on_delete=models.CASCADE, related_name='leveltwolines')

    def __str__(self):
        return self.name
    

class LevelTwoSubStation(models.Model):
    name = models.CharField(max_length=100)
    line = models.ForeignKey(LevelTwoLine, on_delete=models.CASCADE, related_name='substations')

    def __str__(self):
        return self.name




class EmployeeLevelAssignment(models.Model):
    operator = models.ForeignKey(EmployeeMaster, on_delete=models.CASCADE)
    line = models.ForeignKey(LevelTwoLine, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.operator.name} assigned to {self.level}"

# ----- OJT MONITORING SHEET LEVEL 2 --------#

class LevelTwoTraineeInfo(models.Model):
    traineeId = models.CharField(max_length=100)
    trainee_name = models.CharField(max_length=100)
    station = models.ForeignKey(LevelTwoSubStation, on_delete=models.SET_NULL, null=True, related_name='trainees')
    trainer_name = models.CharField(max_length=100)
    line = models.ForeignKey(LevelTwoLine, on_delete=models.SET_NULL, null=True, related_name='trainees')

    # ✅ New field to store training status
    training_status = models.CharField(max_length=10, default='No Data')

    def __str__(self):
        return self.trainee_name

    def calculate_and_save_training_status(self):
        last_day = LevelTwoOJTDay.objects.order_by('-id').first()
        if not last_day:
            self.training_status = "No Data"
            self.save()
            return self.training_status

        total_topics = LevelTwoTrainingTopic.objects.count()
        expected_score = total_topics * 10

        actual_score = LevelTwoOJTScore.objects.filter(
            trainee=self, day=last_day
        ).aggregate(total=models.Sum('score'))['total'] or 0

        self.training_status = "Pass" if actual_score == expected_score else "Fail"
        self.save()
        return self.training_status

        

class LevelTwoTrainingTopic(models.Model):
    sl_no = models.PositiveIntegerField()
    topic = models.CharField(max_length=255)
    date = models.CharField(max_length=255)

    def _str_(self):
        return f"{self.sl_no}. {self.topic}"


class LevelTwoOJTDay(models.Model):
    name = models.CharField(max_length=20)  

    def _str_(self):
        return self.name


class LevelTwoOJTScore(models.Model):
    trainee = models.ForeignKey(LevelTwoTraineeInfo, on_delete=models.CASCADE,related_name='ojtscores')
    topic = models.ForeignKey(LevelTwoTrainingTopic, on_delete=models.CASCADE)
    day = models.ForeignKey(LevelTwoOJTDay, on_delete=models.CASCADE)
    
    SCORE_CHOICES = [
        (10, 'OK'),
        (0, 'Not OK'),
    ]
    score = models.IntegerField(choices=SCORE_CHOICES)

    def _str_(self):
        return f"{self.trainee.trainee_name} | {self.day.name} | {self.topic.topic} | Score: {self.score}"
    






class LevelTwoQuality(models.Model):
    name = models.CharField(max_length=100, default="Quality")

    def _str_(self):
        return self.name


class LevelTwoQualityLine(models.Model):
    name = models.CharField(max_length=100)
    quality = models.ForeignKey(LevelTwoQuality, on_delete=models.CASCADE, related_name='qualityleveltwolines')

    def _str_(self):
        return self.name




class LevelTwoQATraineeInfo(models.Model):
    traineeId = models.CharField(max_length=100)
    trainee_name = models.CharField(max_length=100)
    trainer_name = models.CharField(max_length=100)
    line = models.ForeignKey(LevelTwoQualityLine, on_delete=models.SET_NULL, null=True, related_name='qualitytrainees')

    training_status = models.CharField(max_length=10, default='No Data')

    def __str__(self):
        return self.trainee_name

    def calculate_and_save_training_status(self):
        last_day = LevelTwoQAOJTDay.objects.order_by('-id').first()
        if not last_day:
            self.training_status = "No Data"
            self.save()
            return self.training_status

        total_topics = LevelTwoQATrainingTopic.objects.count()
        expected_score = total_topics * 10

        actual_score = LevelTwoQAOJTScore.objects.filter(
            trainee=self, day=last_day
        ).aggregate(total=models.Sum('score'))['total'] or 0

        self.training_status = "Pass" if actual_score == expected_score else "Fail"
        self.save()
        return self.training_status

        

class LevelTwoQATrainingTopic(models.Model):
    sl_no = models.PositiveIntegerField()
    topic = models.CharField(max_length=255)
    date = models.CharField(max_length=25)

    def str(self):
        return f"{self.sl_no}.{self.topic}"


class LevelTwoQAOJTDay(models.Model):
    name = models.CharField(max_length=20)  

    def str(self):
        return self.name

from django.core.validators import MinValueValidator, MaxValueValidator
class LevelTwoQAOJTScore(models.Model):
    trainee = models.ForeignKey(LevelTwoQATraineeInfo, on_delete=models.CASCADE, related_name='ojtscores')
    topic = models.ForeignKey(LevelTwoQATrainingTopic, on_delete=models.CASCADE)
    day = models.ForeignKey(LevelTwoQAOJTDay, on_delete=models.CASCADE)
    score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])

    def _str_(self):
        return f"{self.trainee.trainee_name} | {self.day.name} | {self.topic.topic} | Score: {self.score}"





















class LevelThreeProduction(models.Model):
    name = models.CharField(max_length=100, default="Production")

    def __str__(self):
        return self.name


class LevelThreeLine(models.Model):
    name = models.CharField(max_length=100)
    production = models.ForeignKey(LevelThreeProduction, on_delete=models.CASCADE, related_name='level_three_lines')

    def __str__(self):
        return self.name


class LevelThreeSubStation(models.Model):
    name = models.CharField(max_length=100)
    line = models.ForeignKey(LevelThreeLine, on_delete=models.CASCADE, related_name='level_three_substations')

    def __str__(self):
        return self.name











class LevelThreeTraineeInfo(models.Model):
    trainee_Id = models.CharField(max_length=100, default='')
    trainee_name = models.CharField(max_length=100)
    station = models.ForeignKey(LevelThreeSubStation, on_delete=models.SET_NULL, null=True, related_name='levelthree_trainees')
    trainer_name = models.CharField(max_length=100)
    line = models.ForeignKey(LevelThreeLine, on_delete=models.SET_NULL, null=True, related_name='levelthree_trainees')

    training_status = models.CharField(max_length=10, default='No Data')

    def __str__(self):
        return self.trainee_name

    def calculate_and_save_training_status(self):
        training_days = LevelThreeOJTDay.objects.all().order_by('id')
        total_topics = LevelThreeTrainingTopic.objects.count()

        if not training_days.exists() or total_topics == 0:
            self.training_status = "No Data"
            self.save()
            return self.training_status

        for day in training_days:
            scores = LevelThreeOJTScore.objects.filter(trainee=self, day=day)

            # Check that trainee has a score for each topic
            if scores.count() != total_topics:
                self.training_status = "Fail"
                self.save()
                return self.training_status

            # Check that each score is exactly 10
            if not all(score.score == 10 for score in scores):
                self.training_status = "Fail"
                self.save()
                return self.training_status

        self.training_status = "Pass"
        self.save()
        return self.training_status
    


class LevelThreeTrainingTopic(models.Model):
    sl_no = models.PositiveIntegerField()
    topic = models.CharField(max_length=255)
    date = models.CharField(max_length=25)

    def str(self):
        return f"{self.sl_no}.{self.topic}"


class LevelThreeOJTDay(models.Model):
    name = models.CharField(max_length=20)  # Example: 'Day-19', 'Day-20'

    def _str_(self):
        return self.name



class LevelThreeOJTScore(models.Model):
    trainee = models.ForeignKey(LevelThreeTraineeInfo, on_delete=models.CASCADE, related_name='ojtscores')
    topic = models.ForeignKey(LevelThreeTrainingTopic, on_delete=models.CASCADE)
    day = models.ForeignKey(LevelThreeOJTDay, on_delete=models.CASCADE)
    
    SCORE_CHOICES = [
        (10, 'OK'),
        (0, 'Not OK'),
    ]
    score = models.IntegerField(choices=SCORE_CHOICES)

    def _str_(self):
        return f"{self.trainee.trainee_name} | {self.day.name} | {self.topic.topic} | Score: {self.score}"
    






# -----QA OJT MONITORING SHEET LEVEL 3 --------

class LevelThreeQATrainingTopic(models.Model):
    sl_no = models.PositiveIntegerField()
    topic = models.CharField(max_length=255)
    date = models.CharField(max_length=25)

    def str(self):
        return f"{self.sl_no}.{self.topic}"


class LevelThreeQAOJTDay(models.Model):
    name = models.CharField(max_length=20)  

    def str(self):
        return self.name


class LevelThreeQuality(models.Model):
    name = models.CharField(max_length=100, default="QualityLevelThree")

    def __str__(self):
        return self.name


class LevelThreeQualityLine(models.Model):
    name = models.CharField(max_length=100)
    quality = models.ForeignKey(LevelThreeQuality, on_delete=models.CASCADE, related_name='qualitylevelthreelines')

    def __str__(self):
        return self.name




class LevelThreeQATraineeInfo(models.Model):
    traineeId = models.CharField(max_length=100)
    trainee_name = models.CharField(max_length=100)
    trainer_name = models.CharField(max_length=100)
    line = models.ForeignKey(LevelThreeQualityLine, on_delete=models.SET_NULL, null=True, related_name='levelthreequalitytrainees')

    training_status = models.CharField(max_length=10, default='No Data')

    def __str__(self):
        return self.trainee_name

    def calculate_and_save_training_status(self):
        training_days = LevelThreeOJTDay.objects.all().order_by('id')
        total_topics = LevelThreeTrainingTopic.objects.count()

        if not training_days.exists() or total_topics == 0:
            self.training_status = "No Data"
            self.save()
            return self.training_status

        for day in training_days:
            scores = LevelThreeOJTScore.objects.filter(trainee=self, day=day)

            # Check that trainee has a score for each topic
            if scores.count() != total_topics:
                self.training_status = "Fail"
                self.save()
                return self.training_status

            # Check that each score is exactly 10
            if not all(score.score == 10 for score in scores):
                self.training_status = "Fail"
                self.save()
                return self.training_status

        self.training_status = "Pass"
        self.save()
        return self.training_status

        



from django.core.validators import MinValueValidator, MaxValueValidator

class LevelThreeQAOJTScore(models.Model):
    trainee = models.ForeignKey(LevelThreeQATraineeInfo, on_delete=models.CASCADE, related_name='ojtscores')
    topic = models.ForeignKey(LevelThreeQATrainingTopic, on_delete=models.CASCADE)
    day = models.ForeignKey(LevelThreeQAOJTDay, on_delete=models.CASCADE)

    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])

    def _str_(self):
        return f"{self.trainee.trainee_name} | {self.day.name} | {self.topic.topic} | Score: {self.score}"























    from django.db import models

# class ARVRTrainingContent(models.Model):
#     description = models.TextField()
#     arvr_file = models.FileField(upload_to='arvr_files/', blank=True, null=True)

#     def __str__(self):
#         return f"AR/VR Content - {self.description[:30]}..."
class ARVRTrainingContent(models.Model):
    description = models.TextField()
    arvr_file = models.FileField(upload_to='arvr_files/', blank=True, null=True)
    url_link = models.TextField(max_length=500, blank=True, null=True)
    def __str__(self):
        return f"AR/VR Content - {self.description[:30]}..." 











from django.db import models
from django.core.exceptions import ValidationError

class MCQQuestion(models.Model):
    subtopic_content = models.ForeignKey(
        'SubTopicContent', on_delete=models.CASCADE, related_name='mcq_questions', null=True, blank=True
    )
    question = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)

    def _str_(self):
        return self.question

    def clean(self):
        if self.correct_answer not in [
            self.option_a, self.option_b, self.option_c, self.option_d
        ]:
            raise ValidationError("Correct answer must match one of the options.")







from django.db import models

from django.db import models

class BiometricAttendance(models.Model):
    sr_no = models.IntegerField(verbose_name="Sr.No.")
    pay_code = models.CharField(max_length=20, verbose_name="PayCode")
    card_no = models.CharField(max_length=20, verbose_name="Card No")
    employee_name = models.CharField(max_length=100, verbose_name="Employee Name")
    department = models.CharField(max_length=100, verbose_name="Department")
    designation = models.CharField(max_length=100, verbose_name="Designation")
    shift = models.CharField(max_length=10, verbose_name="Shift")
    start = models.TimeField(verbose_name="Start")
    in_time = models.TimeField(verbose_name="In")
    out_time = models.TimeField(verbose_name="Out")
    hrs_works = models.TimeField(null=True, blank=True, verbose_name="Hrs Works")
    status = models.CharField(max_length=10, verbose_name="Status")
    early_arrival = models.CharField(max_length=100, null=True, blank=True, verbose_name="Early Arriv.")
    late_arrival = models.CharField(max_length=100, null=True, blank=True, verbose_name="Late Arriv.")
    shift_early = models.CharField(max_length=100, null=True, blank=True, verbose_name="Shift Early")
    excess_lunch = models.CharField(max_length=100, null=True, blank=True, verbose_name="Excess Lunch")
    ot = models.CharField(max_length=100, null=True, blank=True, verbose_name="Ot")
    ot_amount = models.CharField(max_length=100, null=True, blank=True, verbose_name="Ot Amount")
    manual = models.CharField(max_length=100, null=True, blank=True, verbose_name="Manual")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('card_no', 'created_at')  # ensure one entry per card per upload date

    def __str__(self):
        return f"{self.employee_name} ({self.card_no}) on {self.created_at} - {self.status}"










from django.utils import timezone

from django.utils import timezone

from django.utils import timezone

class MultiSkilling(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('scheduled', 'Scheduled'),
        ('inprogress', 'In Progress'),
        ('rescheduled', 'Rescheduled'),
        ('completed', 'Completed'),
    ]

    employee = models.ForeignKey(EmployeeMaster, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE,blank=True, null=True)
    skill_level = models.ForeignKey(Level, on_delete=models.CASCADE,blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')


    reason = models.TextField(blank=True, null=True)
    refreshment_date = models.DateField(blank=True, null=True)

    def _str_(self):
     return f"{self.skill} - Level {self.skill_level.skill_level if self.skill_level else 'N/A'}"


    def update_status_by_date(self):
        today = timezone.now().date()
        if today < self.start_date:
            self.status = 'scheduled'
        elif self.start_date <= today <= self.end_date:
            self.status = 'inprogress'
        elif today > self.end_date:
            self.status = 'completed'
        self.save()

    
class RefreshmentTraining(models.Model):
    employee = models.ForeignKey(EmployeeMaster, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='refreshment_trainings')
    skill = models.ForeignKey(MultiSkilling, on_delete=models.CASCADE)
    skill_level = models.ForeignKey(OperatorSkill, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason_for_refreshment = models.TextField(blank=True, null=True)

    @property
    def card_no(self):
        return self.employee.card_no






from django.db import models

class TrainingReport(models.Model):
    month = models.DateField()  # e.g., 2024-01-01 for January 2024
    new_operators_joined = models.PositiveIntegerField(default=0)
    new_operators_trained = models.PositiveIntegerField(default=0)
    total_trainings_planned = models.PositiveIntegerField(default=0)
    total_trainings_actual = models.PositiveIntegerField(default=0)

    def _str_(self):
        return f"{self.month.strftime('%B %Y')} - Joined: {self.new_operators_joined}, Trained: {self.new_operators_trained}"






from django.db import models

class UnifiedDefectReport(models.Model):
    CATEGORY_CHOICES = [
        ('MSIL', 'MSIL'),
        ('Tier-1', 'Tier-1'),
        ('All Plants', 'All Plants'),
        ('CTQ', 'CTQ'),
    ]

    month = models.DateField()  # First day of the month
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)

    # Defect data
    total_defects = models.PositiveIntegerField(default=0)
    ctq_defects = models.PositiveIntegerField(default=0)

    # Internal rejection data (optional if category is 'Internal')
    total_internal_rejection = models.PositiveIntegerField(default=0)
    ctq_internal_rejection = models.PositiveIntegerField(default=0)

    # Tier-1 specific defect data
    tier1_total_defects = models.PositiveIntegerField(default=0)
    tier1_ctq_defects = models.PositiveIntegerField(default=0)

    def _str_(self):
        return (
            f"{self.category} - {self.month.strftime('%B %Y')} | "
            f"Total: {self.total_defects}, CTQ: {self.ctq_defects}, "
            f"Internal: {self.total_internal_rejection}, CTQ Internal: {self.ctq_internal_rejection}, "
            f"Tier-1 Total: {self.tier1_total_defects}, Tier-1 CTQ: {self.tier1_ctq_defects}"
        )
    

#test part integration

from django.db import models

class KeyEvent(models.Model):
    base_id = models.IntegerField()
    key_id = models.IntegerField()
    key_sn = models.CharField(max_length=255, default='unknown')
    mode = models.IntegerField()
    timestamp = models.DateTimeField()
    info = models.CharField(max_length=255)
    client_timestamp = models.DateTimeField()
    event_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class ConnectEvent(models.Model):
    base_id = models.IntegerField()
    mode = models.IntegerField()
    info = models.CharField(max_length=255)
    timestamp = models.DateTimeField()




class VoteEvent(models.Model):
    base_id = models.IntegerField()
    mode = models.IntegerField()
    info = models.CharField(max_length=255)
    timestamp = models.DateTimeField()

# dynamic quesitions 

# models.py

class QuestionPaper(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    question_paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    question_text = models.CharField(max_length=255)
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_index = models.IntegerField(choices=[(i, chr(65+i)) for i in range(4)])

    def __str__(self):
        return self.question_text

    def get_options(self):
        return [self.option_a, self.option_b, self.option_c, self.option_d]


class TestSession(models.Model):
    test_name = models.CharField(max_length=100)  # ← Make sure this exists
    key_id = models.CharField(max_length=10)
    employee = models.ForeignKey('EmployeeMaster', on_delete=models.CASCADE)
    level = models.CharField(max_length=100, null=True)  # 🆕
    skill = models.ForeignKey('Station', on_delete=models.SET_NULL, null=True, blank=True)
    question_paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE, related_name='test_sessions', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('test_name', 'key_id')

    def __str__(self):
        return f"{self.test_name} - {self.key_id} ({self.employee.name})"



# models.py
class Score(models.Model):
    employee = models.ForeignKey(EmployeeMaster, on_delete=models.CASCADE)
    marks = models.IntegerField()
    test_name = models.CharField(max_length=100, blank=True)
    test = models.ForeignKey(TestSession, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    percentage = models.FloatField(default=0)
    passed = models.BooleanField(default=False)
    level = models.CharField(max_length=100, null=True, blank=True)
    skill = models.ForeignKey('Station', on_delete=models.SET_NULL, null=True, blank=True)




    def __str__(self):
        return f"{self.employee.name} - {self.marks} marks"





class HanContent(models.Model):
    title = models.CharField(max_length=100, default='')

    def _str_(self):
        return self.title


class HanTrainingContent(models.Model):
    han_content = models.ForeignKey(HanContent, on_delete=models.CASCADE, related_name='contents')
    description = models.TextField()
    training_file = models.FileField(upload_to='training_files/', blank=True, null=True)
    url_link = models.URLField(max_length=500, blank=True, null=True)

    def _str_(self):
        return f"Training Content for {self.han_content.title}"
    

class ShoContent(models.Model):
    title = models.CharField(max_length=100, default='')

    def _str_(self):
        return self.title


class ShoTrainingContent(models.Model):
    sho_content = models.ForeignKey(ShoContent, on_delete=models.CASCADE, related_name='contents', default='')
    description = models.TextField()
    training_file = models.FileField(upload_to='training_files/', blank=True, null=True)
    url_link = models.URLField(max_length=500, blank=True, null=True)

    def _str_(self):
        return f"Content for {self.sho_content.title}"




class ManagementReview(models.Model):
    month_year = models.DateField()
    new_operators_joined = models.IntegerField()
    new_operators_trained = models.IntegerField()
    total_training_plans = models.IntegerField()
    total_trainings_actual = models.IntegerField()
    total_defects_msil = models.IntegerField()
    ctq_defects_msil = models.IntegerField()
    total_defects_tier1 = models.IntegerField()
    ctq_defects_tier1 = models.IntegerField()
    total_internal_rejection = models.IntegerField()
    ctq_internal_rejection = models.IntegerField()

    def _str_(self):
        return self.month_year.strftime('%b %y')
    


from django.db import models

class CompanyLogo(models.Model):
    name = models.CharField(max_length=100)  # Optional: Name of the logo (e.g., company name)
    logo = models.ImageField(upload_to='logos/',blank=True,null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return self.name or f"Logo {self.id}"
    

class AdvancedManpowerCTQ(models.Model):
    month_year_ctq = models.DateField()
    total_stations_ctq = models.IntegerField()
    operator_required_ctq = models.IntegerField()
    operator_availability_ctq = models.IntegerField()
    buffer_manpower_required_ctq = models.IntegerField()
    buffer_manpower_availability_ctq = models.IntegerField()
    attrition_trend_ctq = models.IntegerField()
    absentee_trend_ctq = models.IntegerField()
    planned_units_ctq = models.IntegerField()
    actual_production_ctq = models.IntegerField()
    

    # New relations
    factory = models.ForeignKey('Factory', on_delete=models.CASCADE, related_name='ctq_records', null=True, blank=True)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name='ctq_records', null=True, blank=True)

    def _str_(self):
        return f"{self.month_year_ctq.strftime('%b %y')} - {self.factory.name} - {self.department.name}"



class OperatorRequirement(models.Model):
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE, related_name='operator_requirements')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='operator_requirements')
    month = models.DateField(help_text="Any date in the month (used for month tracking)")
    level = models.IntegerField(help_text="Skill level or grade")
    operator_required = models.PositiveIntegerField()
    operator_available = models.PositiveIntegerField()

    def _str_(self):
        return f"{self.factory.name} - {self.department.name} | Level {self.level} - {self.month.strftime('%B %Y')}"
    


from django.db import models

class UploadedFile(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')  # stores in MEDIA_ROOT/uploads/
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
