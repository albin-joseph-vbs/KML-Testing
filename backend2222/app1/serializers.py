

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _


from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    employeeid = serializers.CharField(max_length=10)
    role = serializers.CharField(max_length=50)
    email = serializers.EmailField(max_length=100)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    hq = serializers.CharField(max_length=50)
    factory = serializers.CharField(max_length=50)
    department = serializers.CharField(max_length=50)
    status = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'password', 'employeeid', 'first_name', 'last_name',
            'role', 'hq', 'factory', 'department', 'status'
        ]

    def validate_email(self, value):
        """
        Validate email is not already in use.
        Accepts any valid email domain like gmail.com, yahoo.in, etc.
        """
        if User.objects.filter(email=value).exists():
            raise ValidationError("Email is already in use.")
        return value

    def validate_password(self, value):
        """
        Validate password strength:
        - Minimum 6 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(value) < 6:
            raise ValidationError("Password must be at least 6 characters long.")
        if not any(char.isupper() for char in value):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in value):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not any(char.isdigit() for char in value):
            raise ValidationError("Password must contain at least one number.")
        if not any(char in "!@#$%^&*()-_=+[]{}|;:',.<>?/" for char in value):
            raise ValidationError("Password must contain at least one special character (!@#$%^&*()-_=+[]{}|;:',.<>?/).")
        return value

    def create(self, validated_data):
        """
        Create a new user using create_user method from the User model.
        """
        try:
            return User.objects.create_user(
                email=validated_data['email'],
                employeeid=validated_data['employeeid'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                role=validated_data['role'],
                hq=validated_data['hq'],
                factory=validated_data['factory'],
                department=validated_data['department'],
                password=validated_data['password']
            )
        except Exception as e:
            raise serializers.ValidationError({'error': str(e)})


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email', '').strip()
        password = attrs.get('password', '')

        if not email or not password:
            raise ValidationError({'error': _('Email and password are required.')})

        user = authenticate(request=self.context.get('request'), email=email, password=password)

        if user is None:
            raise ValidationError({'error': _('Invalid email or password.')})

        if not user.is_active:
            raise ValidationError({'error': _('This account is inactive. Please contact support.')})

        attrs['user'] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate_refresh_token(self, value):
        if not value:
            raise serializers.ValidationError("Refresh token is required for logout.")
        return value













from rest_framework import serializers
from .models import EmployeeMaster, MonthlyAssignment,  OperatorSkill, OperatorTraining, Station, TrainingTopic

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeMaster
        fields = '__all__'



from rest_framework import serializers
from .models import HQ,Factory,Department,Level,Line

class HQSerializer(serializers.ModelSerializer):
    class Meta:
        model = HQ
        fields = ['id', 'name']


class FactorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Factory
        fields = ['id', 'name', 'hq']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'factory']


class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields = ['id', 'name', 'department']


class LevelSerializer(serializers.ModelSerializer):
    name_display = serializers.CharField(source='get_name_display', read_only=True)

    class Meta:
        model = Level
        fields = ['id', 'name', 'name_display', 'line']




# class OperatorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Operator
#         fields = ['id', 'name', 'code', 'date_of_joining']




from rest_framework import serializers
from .models import MainDepartment, MainLine, SubLine, Station, OperatorSkill
from .models import EmployeeMaster  # Update the path if EmployeeMaster is in another app


class MainDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainDepartment
        fields = ['id', 'name']


class MainLineSerializer(serializers.ModelSerializer):
    department = MainDepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(queryset=MainDepartment.objects.all(), source='department', write_only=True)

    class Meta:
        model = MainLine
        fields = ['id', 'name', 'department', 'department_id']


class SubLineSerializer(serializers.ModelSerializer):
    main_line = MainLineSerializer(read_only=True)
    main_line_id = serializers.PrimaryKeyRelatedField(queryset=MainLine.objects.all(), source='main_line', write_only=True)

    class Meta:
        model = SubLine
        fields = ['id', 'name', 'main_line', 'main_line_id']


class StationSerializer(serializers.ModelSerializer):
    sub_line = SubLineSerializer(read_only=True)
    sub_line_id = serializers.PrimaryKeyRelatedField(queryset=SubLine.objects.all(), source='sub_line', write_only=True)

    class Meta:
        model = Station
        fields = [
            'id',
            'sub_line', 'sub_line_id',
            'station_number',
            'skill',
            'minimum_skill_required',
            'min_operator_required'
        ]


class OperatorSkillSerializer(serializers.ModelSerializer):
    operator = serializers.PrimaryKeyRelatedField(queryset=EmployeeMaster.objects.all())
    station = serializers.PrimaryKeyRelatedField(queryset=Station.objects.all())

    class Meta:
        model = OperatorSkill
        fields = ['id', 'operator', 'station', 'skill_level', 'sequence']


class TrainingTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingTopic
        fields = ['id', 'name']


class OperatorTrainingSerializer(serializers.ModelSerializer):
    operator = serializers.PrimaryKeyRelatedField(queryset=EmployeeMaster.objects.all())
    topic = serializers.PrimaryKeyRelatedField(queryset=TrainingTopic.objects.all())

    class Meta:
        model = OperatorTraining
        fields = ['id', 'operator', 'topic', 'completed']


class MonthlyAssignmentSerializer(serializers.ModelSerializer):
    operator = serializers.PrimaryKeyRelatedField(queryset=EmployeeMaster.objects.all())
    station = serializers.PrimaryKeyRelatedField(queryset=Station.objects.all())

    class Meta:
        model = MonthlyAssignment
        fields = ['id', 'operator', 'station', 'skill_level', 'month']







from rest_framework import serializers
from .models import OperatorLevelTracking

class OperatorLevelTrackingSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    level_name = serializers.CharField(source='level.name', read_only=True)
    milestone_date = serializers.DateField(read_only=True)
    message = serializers.SerializerMethodField()

    class Meta:
        model = OperatorLevelTracking
        fields = ['id', 'operator_name', 'level_name', 'day', 'milestone_date', 'message']

    def get_message(self, obj):
        return f"{obj.operator.name} {obj.level.name} is going to complete today"








from rest_framework import serializers
from .models import OperatorLevelEmailTracking, TrackingEmail

class TrackingEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingEmail
        fields = ['email']

class OperatorLevelEmailTrackingSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    level_name = serializers.CharField(source='level.name', read_only=True)
    milestone_date = serializers.DateField(read_only=True)
    message = serializers.SerializerMethodField()
    emails = TrackingEmailSerializer(many=True, read_only=True)

    class Meta:
        model = OperatorLevelEmailTracking
        fields = ['id', 'operator_name', 'level_name', 'day', 'milestone_date', 'message', 'emails']

    def get_message(self, obj):
        return f"{obj.operator.name} {obj.level.name} is going to complete today"












from rest_framework import serializers
from .models import Machine, MachineAllocation, EmployeeMaster

class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ['id', 'name', 'image', 'level', 'process', 'created_at', 'updated_at']


from rest_framework import serializers
from .models import MachineAllocation, Machine, EmployeeMaster, OperatorSkill
from .serializers import MachineSerializer  # Assuming you already have this

class MachineAllocationSerializer(serializers.ModelSerializer):
    machine = MachineSerializer(read_only=True)
    machine_id = serializers.PrimaryKeyRelatedField(
        queryset=Machine.objects.all(),
        source='machine',
        write_only=True
    )
    employee = serializers.StringRelatedField(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=EmployeeMaster.objects.all(),
        source='employee',
        write_only=True
    )

    class Meta:
        model = MachineAllocation
        fields = [
            'id',
            'machine', 'machine_id',
            'employee', 'employee_id',
            'allocated_at', 'approval_status'
        ]

    def validate(self, data):
        machine = data['machine']
        employee = data['employee']

        required_process = machine.process
        required_level = machine.level
        approval_status = 'pending'  # default

        operator_skills = OperatorSkill.objects.filter(operator=employee, station__skill=required_process)

        for skill in operator_skills:
            try:
                # Extract numeric level from "Level 2" etc.
                level_str = skill.skill_level.strip().lower().replace("level ", "")
                operator_level = int(level_str)
                if operator_level >= required_level:
                    approval_status = 'approved'
                    break
            except:
                continue

        data['approval_status'] = approval_status
        return data

    def create(self, validated_data):
        allocation = MachineAllocation(**validated_data)
        allocation.save()
        return allocation

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance







from rest_framework import serializers
from .models import Days

class DaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Days
        fields = ['id', 'level', 'day']



from rest_framework import serializers
from .models import SkillTraining

class SkillTrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillTraining
        fields = ['id', 'level', 'title']




from rest_framework import serializers
from .models import SubTopic

class SubTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTopic
        fields = ['id', 'skill_training','day','title']



from rest_framework import serializers
from .models import SubTopic

class SubTopicDaySerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='day.day', read_only=True)  # This accesses the `day` field of the related `Days` model

    class Meta:
        model = SubTopic
        fields = ['id', 'skill_training', 'day', 'day_name', 'title']



from .models import SubTopicContent

class SubTopicContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTopicContent
        fields = ['id', 'subtopic', 'title']





from .models import TrainingContent

class TrainingContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingContent
        fields = ['id', 'subtopic_content', 'training_file', 'url_link', 'description']






from rest_framework import serializers
from .models import LevelTwoProduction, LevelTwoLine, LevelTwoSubStation

class LevelTwoSubStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelTwoSubStation
        fields = ['id', 'name', 'line']

class LevelTwoLineSerializer(serializers.ModelSerializer):
    substations = LevelTwoSubStationSerializer(many=True, read_only=True)

    class Meta:
        model = LevelTwoLine
        fields = ['id', 'name', 'production', 'substations']

class LevelTwoProductionSerializer(serializers.ModelSerializer):
    leveltwolines = LevelTwoLineSerializer(many=True, read_only=True)

    class Meta:
        model = LevelTwoProduction
        fields = ['id', 'name', 'leveltwolines']








from rest_framework import serializers
from .models import (
    LevelTwoTraineeInfo,
    LevelTwoTrainingTopic,
    LevelTwoOJTDay,
    LevelTwoOJTScore,
    LevelTwoLine,
)

class LevelTwoTraineeInfoSerializer(serializers.ModelSerializer):
    line_name = serializers.CharField(source='line.name', read_only=True)
    station_name = serializers.CharField(source='station.name', read_only=True)

    class Meta:
        model = LevelTwoTraineeInfo
        fields = ['id','traineeId', 'trainee_name', 'station', 'station_name', 'trainer_name', 'line', 'line_name','training_status']


class LevelTwoTrainingTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelTwoTrainingTopic
        fields = '__all__'


class LevelTwoOJTDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelTwoOJTDay
        fields = '__all__'


class LevelTwoOJTScoreSerializer(serializers.ModelSerializer):
    trainee = serializers.PrimaryKeyRelatedField(queryset=LevelTwoTraineeInfo.objects.all())
    topic = serializers.PrimaryKeyRelatedField(queryset=LevelTwoTrainingTopic.objects.all())
    day = serializers.PrimaryKeyRelatedField(queryset=LevelTwoOJTDay.objects.all())

    class Meta:
        model = LevelTwoOJTScore
        fields = '__all__'






from rest_framework import serializers
from .models import EmployeeLevelAssignment, LevelTwoTraineeInfo

class EmployeeLevelAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeLevelAssignment
        fields = '__all__'

    def create(self, validated_data):
        assignment = super().create(validated_data)

        # Check if the level assigned is "level_2"
        if assignment.level.name == 'level_2':
            LevelTwoTraineeInfo.objects.create(
                traineeId=assignment.operator.pay_code,          # from EmployeeMaster
                trainee_name=assignment.operator.name,           # from EmployeeMaster
                linename=assignment.line.name                    # from LevelTwoLine
            )

        return assignment








class NestedLevelTwoOJTScoreSerializer(serializers.ModelSerializer):
    topic_id = serializers.PrimaryKeyRelatedField(queryset=LevelTwoTrainingTopic.objects.all(), source='topic')
    day_id = serializers.PrimaryKeyRelatedField(queryset=LevelTwoOJTDay.objects.all(), source='day')

    class Meta:
        model = LevelTwoOJTScore
        fields = ['topic_id', 'day_id', 'score']


class NestedLevelTwoTraineeInfoSerializer(serializers.ModelSerializer):
    ojtscores = NestedLevelTwoOJTScoreSerializer(many=True, read_only=True)
    
    station = serializers.PrimaryKeyRelatedField(queryset=LevelTwoSubStation.objects.all())
    line = serializers.PrimaryKeyRelatedField(queryset=LevelTwoLine.objects.all())

    station_name = serializers.CharField(source='station.name', read_only=True)
    line_name = serializers.CharField(source='line.name', read_only=True)

    class Meta:
        model = LevelTwoTraineeInfo
        fields = [
            'id',
            'traineeId',
            'trainee_name',
            'station',
            'station_name',
            'trainer_name',
            'line',
            'line_name',
            'training_status', 
            'ojtscores'
        ]

    def create(self, validated_data):
        # If ojtscores is included via custom input (not read_only), handle it
        scores_data = self.initial_data.get('ojtscores')
        trainee = LevelTwoTraineeInfo.objects.create(**validated_data)
        if scores_data:
            for score_data in scores_data:
                LevelTwoOJTScore.objects.create(trainee=trainee, **score_data)
        return trainee

    def update(self, instance, validated_data):
        scores_data = self.initial_data.get('ojtscores')

        # Update trainee fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if scores_data:
            LevelTwoOJTScore.objects.filter(trainee=instance).delete()
            for score_data in scores_data:
                LevelTwoOJTScore.objects.create(trainee=instance, **score_data)

        return instance









#quality level two



from rest_framework import serializers
from .models import LevelTwoQuality, LevelTwoQualityLine


class LevelTwoQualityLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelTwoQualityLine
        fields = ['id', 'name', 'quality']


class LevelTwoQualitySerializer(serializers.ModelSerializer):
    qualityleveltwolines = LevelTwoQualityLineSerializer(many=True, read_only=True)

    class Meta:
        model = LevelTwoQuality
        fields = ['id', 'name', 'qualityleveltwolines']








from rest_framework import serializers
from .models import (
    LevelTwoQATraineeInfo,
    LevelTwoQATrainingTopic,
    LevelTwoQAOJTDay,
    LevelTwoQAOJTScore,
    LevelTwoLine,
)

class LevelTwoQATraineeInfoSerializer(serializers.ModelSerializer):
    line_name = serializers.CharField(source='line.name', read_only=True)

    class Meta:
        model = LevelTwoQATraineeInfo
        fields = ['traineeId', 'trainee_name', 'station', 'trainer_name', 'line', 'line_name']


class LevelTwoQATrainingTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelTwoQATrainingTopic
        fields = '__all__'


class LevelTwoQAOJTDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelTwoQAOJTDay
        fields = '__all__'


class LevelTwoQAOJTScoreSerializer(serializers.ModelSerializer):
    trainee = serializers.PrimaryKeyRelatedField(queryset=LevelTwoQATraineeInfo.objects.all())
    topic = serializers.PrimaryKeyRelatedField(queryset=LevelTwoQATrainingTopic.objects.all())
    day = serializers.PrimaryKeyRelatedField(queryset=LevelTwoQAOJTDay.objects.all())

    class Meta:
        model = LevelTwoQAOJTScore
        fields = '__all__'






from rest_framework import serializers
from .models import (
    LevelTwoQATraineeInfo,
    LevelTwoQATrainingTopic,
    LevelTwoQAOJTDay,
    LevelTwoQAOJTScore,
    LevelTwoLine,
)

class LevelTwoQATraineeInfoSerializer(serializers.ModelSerializer):
    line_name = serializers.CharField(source='line.name', read_only=True)

    class Meta:
        model = LevelTwoQATraineeInfo
        fields = ['traineeId', 'trainee_name', 'trainer_name', 'line', 'line_name']


class LevelTwoQATrainingTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelTwoQATrainingTopic
        fields = '__all__'


class LevelTwoQAOJTDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelTwoQAOJTDay
        fields = '__all__'


class LevelTwoQAOJTScoreSerializer(serializers.ModelSerializer):
    trainee = serializers.PrimaryKeyRelatedField(queryset=LevelTwoQATraineeInfo.objects.all())
    topic = serializers.PrimaryKeyRelatedField(queryset=LevelTwoQATrainingTopic.objects.all())
    day = serializers.PrimaryKeyRelatedField(queryset=LevelTwoQAOJTDay.objects.all())

    class Meta:
        model = LevelTwoQAOJTScore
        fields = '__all__'








from rest_framework import serializers
from .models import (
    LevelTwoQATraineeInfo,
    LevelTwoQATrainingTopic,
    LevelTwoQAOJTDay,
    LevelTwoQAOJTScore,
    LevelTwoLine
)


class NestedLevelTwoQAOJTScoreSerializer(serializers.ModelSerializer):
    topic_id = serializers.PrimaryKeyRelatedField(queryset=LevelTwoQATrainingTopic.objects.all(), source='topic')
    day_id = serializers.PrimaryKeyRelatedField(queryset=LevelTwoQAOJTDay.objects.all(), source='day')

    class Meta:
        model = LevelTwoQAOJTScore
        fields = ['topic_id', 'day_id', 'score']


class NestedLevelTwoQATraineeInfoSerializer(serializers.ModelSerializer):
    ojtscores = NestedLevelTwoQAOJTScoreSerializer(many=True)

    line = serializers.PrimaryKeyRelatedField(queryset=LevelTwoQualityLine.objects.all())
    line_name = serializers.CharField(source='line.name', read_only=True)

    class Meta:
        model = LevelTwoQATraineeInfo
        fields = [
            'id',
            'traineeId',
            'trainee_name',
            'trainer_name',
            'line',
            'line_name',
            'training_status',
            'ojtscores'
        ]

    def create(self, validated_data):
        scores_data = validated_data.pop('ojtscores', [])
        trainee = LevelTwoQATraineeInfo.objects.create(**validated_data)

        for score_data in scores_data:
            LevelTwoQAOJTScore.objects.create(trainee=trainee, **score_data)

        return trainee

    def update(self, instance, validated_data):
        scores_data = validated_data.pop('ojtscores', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if scores_data is not None:
            LevelTwoQAOJTScore.objects.filter(trainee=instance).delete()
            for score_data in scores_data:
                LevelTwoQAOJTScore.objects.create(trainee=instance, **score_data)

        return instance






from rest_framework import serializers
from .models import LevelThreeProduction, LevelThreeLine, LevelThreeSubStation


class LevelThreeLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelThreeLine
        fields = ['id', 'name', 'production']


class LevelThreeProductionSerializer(serializers.ModelSerializer):
    level_three_lines = LevelThreeLineSerializer(many=True, read_only=True)

    class Meta:
        model = LevelThreeProduction
        fields = ['id', 'name', 'level_three_lines']


class LevelThreeSubStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelThreeSubStation
        fields = ['id', 'name', 'line']




from rest_framework import serializers
from .models import LevelThreeTraineeInfo, LevelThreeTrainingTopic, LevelThreeOJTDay, LevelThreeOJTScore

class LevelThreeTraineeInfoSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source='station.name', read_only=True)
    line_name = serializers.CharField(source='line.name', read_only=True)

    class Meta:
        model = LevelThreeTraineeInfo
        fields = [
            'id',
            'trainee_Id',
            'trainee_name',
            'station',
            'station_name',
            'trainer_name',
            'line',
            'line_name',
            'training_status',
        ]

class LevelThreeTrainingTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelThreeTrainingTopic
        fields = '__all__'

class LevelThreeOJTDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelThreeOJTDay
        fields = '__all__'

class LevelThreeOJTScoreSerializer(serializers.ModelSerializer):
    trainee = serializers.PrimaryKeyRelatedField(queryset=LevelThreeTraineeInfo.objects.all())
    topic = serializers.PrimaryKeyRelatedField(queryset=LevelThreeTrainingTopic.objects.all())
    day = serializers.PrimaryKeyRelatedField(queryset=LevelThreeOJTDay.objects.all())

    class Meta:
        model = LevelThreeOJTScore
        fields = '__all__'







from rest_framework import serializers
from .models import (
    LevelThreeTraineeInfo,
    LevelThreeTrainingTopic,
    LevelThreeOJTDay,
    LevelThreeOJTScore,
    LevelThreeSubStation,
    LevelThreeLine,
)



class NestedLevelThreeOJTScoreSerializer(serializers.ModelSerializer):
    topic_id = serializers.PrimaryKeyRelatedField(source='topic', queryset=LevelThreeTrainingTopic.objects.all())
    day_id = serializers.PrimaryKeyRelatedField(source='day', queryset=LevelThreeOJTDay.objects.all())

    class Meta:
        model = LevelThreeOJTScore
        fields = ['topic_id', 'day_id', 'score']





class NestedLevelThreeTraineeInfoSerializer(serializers.ModelSerializer):
    ojtscores = NestedLevelThreeOJTScoreSerializer(many=True, read_only=True)

    station = serializers.PrimaryKeyRelatedField(queryset=LevelThreeSubStation.objects.all())
    line = serializers.PrimaryKeyRelatedField(queryset=LevelThreeLine.objects.all())

    station_name = serializers.CharField(source='station.name', read_only=True)
    line_name = serializers.CharField(source='line.name', read_only=True)
    traineeId = serializers.CharField(source='trainee_Id')  # Use alias here

    class Meta:
        model = LevelThreeTraineeInfo
        fields = [
             'id',
            'traineeId',
            'trainee_name',
            'station',
            'station_name',
            'trainer_name',
            'line',
            'line_name',
            'training_status',
            'ojtscores'
        ]


    def create(self, validated_data):
        scores_data = self.initial_data.get('ojtscores')
        trainee = LevelThreeTraineeInfo.objects.create(**validated_data)
        if scores_data:
            for score_data in scores_data:
                LevelThreeOJTScore.objects.create(trainee=trainee, **score_data)
        return trainee

    def update(self, instance, validated_data):
        scores_data = self.initial_data.get('ojtscores')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if scores_data:
            LevelThreeOJTScore.objects.filter(trainee=instance).delete()
            for score_data in scores_data:
                LevelThreeOJTScore.objects.create(trainee=instance, **score_data)

        return instance






























from rest_framework import serializers
from .models import LevelThreeQuality, LevelThreeQualityLine


class LevelThreeQualityLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelThreeQualityLine
        fields = ['id', 'name', 'quality']


class LevelThreeQualitySerializer(serializers.ModelSerializer):
    qualitylevelthreelines = LevelThreeQualityLineSerializer(many=True, read_only=True)

    class Meta:
        model = LevelThreeQuality
        fields = ['id', 'name', 'qualitylevelthreelines']



from rest_framework import serializers
from .models import (
    LevelThreeQATraineeInfo,
    LevelThreeQATrainingTopic,
    LevelThreeQAOJTDay,
    LevelThreeQAOJTScore,
    LevelThreeLine,
)

class LevelThreeQATraineeInfoSerializer(serializers.ModelSerializer):
    line_name = serializers.CharField(source='line.name', read_only=True)

    class Meta:
        model = LevelThreeQATraineeInfo
        fields = ['traineeId', 'trainee_name', 'trainer_name', 'line', 'line_name']


class LevelThreeQATrainingTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelThreeQATrainingTopic
        fields = '__all__'


class LevelThreeQAOJTDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelThreeQAOJTDay
        fields = '__all__'


class LevelThreeQAOJTScoreSerializer(serializers.ModelSerializer):
    trainee = serializers.PrimaryKeyRelatedField(queryset=LevelThreeQATraineeInfo.objects.all())
    topic = serializers.PrimaryKeyRelatedField(queryset=LevelThreeQATrainingTopic.objects.all())
    day = serializers.PrimaryKeyRelatedField(queryset=LevelThreeQAOJTDay.objects.all())

    class Meta:
        model = LevelThreeQAOJTScore
        fields = '__all__'







from rest_framework import serializers
from .models import (
    LevelThreeQATraineeInfo,
    LevelThreeQATrainingTopic,
    LevelThreeQAOJTDay,
    LevelThreeQAOJTScore,
    LevelThreeLine
)


class NestedLevelThreeQAOJTScoreSerializer(serializers.ModelSerializer):
    topic_id = serializers.PrimaryKeyRelatedField(queryset=LevelThreeQATrainingTopic.objects.all(), source='topic')
    day_id = serializers.PrimaryKeyRelatedField(queryset=LevelThreeQAOJTDay.objects.all(), source='day')

    class Meta:
        model = LevelThreeQAOJTScore
        fields = ['topic_id', 'day_id', 'score']


class NestedLevelThreeQATraineeInfoSerializer(serializers.ModelSerializer):
    ojtscores = NestedLevelThreeQAOJTScoreSerializer(many=True)

    line = serializers.PrimaryKeyRelatedField(queryset=LevelThreeQualityLine.objects.all())
    line_name = serializers.CharField(source='line.name', read_only=True)

    class Meta:
        model = LevelThreeQATraineeInfo
        fields = [
            'id',
            'traineeId',
            'trainee_name',
            'trainer_name',
            'line',
            'line_name',
            'training_status',
            'ojtscores'
        ]

    def create(self, validated_data):
        scores_data = validated_data.pop('ojtscores', [])
        trainee = LevelThreeQATraineeInfo.objects.create(**validated_data)

        for score_data in scores_data:
            LevelThreeQAOJTScore.objects.create(trainee=trainee, **score_data)

        return trainee

    def update(self, instance, validated_data):
        scores_data = validated_data.pop('ojtscores', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if scores_data is not None:
            LevelThreeQAOJTScore.objects.filter(trainee=instance).delete()
            for score_data in scores_data:
                LevelThreeQAOJTScore.objects.create(trainee=instance, **score_data)

        return instance

from rest_framework import serializers
from .models import ARVRTrainingContent

class ARVRTrainingContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ARVRTrainingContent
        # fields = ['id', 'description', 'arvr_file']
        fields = '__all__'







from rest_framework import serializers
from .models import MCQQuestion

class MCQQuestionSerializer(serializers.ModelSerializer):
    # Optional: Display subtopic content title instead of just ID
    subtopic_content_title = serializers.CharField(source='subtopic_content.title', read_only=True)

    class Meta:
        model = MCQQuestion
        fields = [
            'id',
            'subtopic_content',         # ForeignKey field (write access)
            'subtopic_content_title',   # Read-only title (optional)
            'question',
            'option_a',
            'option_b',
            'option_c',
            'option_d',
            'correct_answer'
        ]

    def validate(self, data):
        options = [
            data.get('option_a'),
            data.get('option_b'),
            data.get('option_c'),
            data.get('option_d')
        ]
        if data.get('correct_answer') not in options:
            raise serializers.ValidationError("Correct answer must match one of the options.")
        return data




from rest_framework import serializers
from .models import BiometricAttendance

class BiometricAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiometricAttendance
        fields = '__all__'





from rest_framework import serializers
from .models import MultiSkilling

from rest_framework import serializers
from .models import MultiSkilling

class NewMultiSkillingSerializer(serializers.ModelSerializer):
    card_no = serializers.CharField(source='employee.card_no', read_only=True)

    class Meta:
        model = MultiSkilling
        fields = [
            'id',
            'employee',
            'card_no',
            'station',
            'skill_level',
            'start_date',
            'end_date',
            'notes',
            'status'
]

class RefreshMultiSkillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiSkilling
        fields = [
            'id',
            'employee',
            'skill',
            'notes',
            'status',
            'reason',
            'refreshment_date',
        ]




from rest_framework import serializers
from .models import TrainingReport

class TrainingReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingReport
        fields = '__all__'




from rest_framework import serializers
from .models import UnifiedDefectReport

class UnifiedDefectReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnifiedDefectReport
        fields = '__all__'

from rest_framework import serializers

class ExcelUploadSerializer(serializers.Serializer):
    file = serializers.FileField()








# serializers.py
from rest_framework import serializers
from .models import EmployeeMaster

class EmployeeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeMaster
        fields = ['id', 'name']  # Include 'id' optionally


# serializers.py
from rest_framework import serializers
from .models import EmployeeMaster

class EmployeeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeMaster
        fields = ['id', 'name']  # Include 'id' optionally


# easy test


from rest_framework import serializers
from .models import  *


class KeyEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyEvent
        fields = '__all__'

class ConnectEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectEvent
        fields = '__all__'




class VoteEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteEvent
        fields = '__all__'

# dynamic questions



class QuestionPaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionPaper
        fields = ['id', 'name']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_index', 'question_paper']




class TestSessionSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    level_name = serializers.CharField(source='level', read_only=True)  # ✅ directly from string
    skill_name = serializers.CharField(source='skill.skill', default='', read_only=True)

    class Meta:
        model = TestSession
        fields = ['id', 'key_id', 'employee', 'employee_name', 'level', 'level_name', 'skill', 'skill_name']






class ScoreSerializer(serializers.ModelSerializer):
    employee_id = serializers.IntegerField(source='employee.id')
    name = serializers.CharField(source='employee.name')
    section = serializers.CharField(source='employee.section', default='')
    total_questions = serializers.SerializerMethodField()
    
    class Meta:
        model = Score
        fields = [
            'employee_id', 'name', 'section',
            'marks', 'percentage', 'total_questions', 'passed', 'test_name', 'created_at'
        ]

    def get_percentage(self, obj):
        total = self.get_total_questions(obj)
        return (obj.marks / total) * 100 if total > 0 else 0

    def get_total_questions(self, obj):
        if obj.test:
            return obj.test.questions.count()
        return 0





class SimpleScoreSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    name = serializers.CharField()
    marks = serializers.IntegerField()
    percentage = serializers.FloatField()
    level_name = serializers.CharField()
    skill_name = serializers.CharField()
    section = serializers.CharField()


    





#Employee Card 


class OperatorCardSkillSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    station_skill = serializers.CharField(source='station.skill', read_only=True)

    class Meta:
        model = OperatorSkill
        fields = ['id', 'operator_name', 'station_skill', 'skill_level', 'sequence']






from rest_framework import serializers
from .models import Score

class CardScoreSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)

    class Meta:
        model = Score
        fields = [
            'id',
            'employee_name',
            'test_name',     # just use directly if it's a model field
            'marks',
            'percentage',    # must exist in model
            'passed',        # must exist in model
            'created_at'
        ]







from rest_framework import serializers
from .models import MultiSkilling

class CardMultiSkillingSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    station_number = serializers.IntegerField(source='station.station_number', read_only=True)
    skill_level_value = serializers.CharField(source='skill_level.skill_level', read_only=True)

    class Meta:
        model = MultiSkilling
        fields = [
            'id',
            'employee_name',
            'station_number',
            'skill',
            'skill_level_value',
            'start_date',
            'end_date',
            'notes',
            'status',
            'reason',
            'refreshment_date'
        ]







from rest_framework import serializers
from .models import RefreshmentTraining

class CardRefreshmentTrainingSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    card_no = serializers.CharField(source='employee.card_no', read_only=True)
    station_number = serializers.IntegerField(source='station.station_number', read_only=True)
    skill_name = serializers.CharField(source='skill.skill', read_only=True)
    skill_level_value = serializers.CharField(source='skill_level.skill_level', read_only=True)

    class Meta:
        model = RefreshmentTraining
        fields = [
            'id',
            'employee_name',
            'card_no',
            'station_number',
            'skill_name',
            'skill_level_value',
            'start_date',
            'end_date',
            'reason_for_refreshment',
        ]







from rest_framework import serializers
from .models import EmployeeMaster

class CardEmployeeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeMaster
        fields = [
            'id', 'pay_code', 'card_no', 'name', 'guardian_name', 'sex', 'birth_date',
            'department', 'section', 'desig_category', 'joining_date',
            'auth_shift', 'shift_type', 'shift_pattern',
            'first_weekly_off', 'second_weekly_off', 'second_weekly_off_fh',
            'ot_allowed_rate', 'round_the_clock'
        ]










from .models import HanContent
from .models import HanTrainingContent

class HanContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HanContent
        fields = ['id', 'title']


class HanTrainingContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HanTrainingContent
        fields = ['id', 'han_content', 'training_file', 'url_link', 'description']

from .models import ShoContent, ShoTrainingContent
from rest_framework import serializers


class ShoContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoContent
        fields = ['id', 'title']


class ShoTrainingContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoTrainingContent
        fields = ['id', 'sho_content', 'training_file', 'url_link', 'description']

class StationByLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'




class SubLineByMainLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubLine
        fields = '__all__'





class MainLineByDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainLine
        fields = '__all__'







from .models import ManagementReview

class TrainingDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementReview
        fields = ['month_year', 'new_operators_joined', 'new_operators_trained', 
                 'total_training_plans', 'total_trainings_actual']

class DefectsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementReview
        fields = ['month_year', 'total_defects_msil', 'ctq_defects_msil', 
                 'total_defects_tier1', 'ctq_defects_tier1', 
                 'total_internal_rejection', 'ctq_internal_rejection']

class OperatorsChartSerializer(serializers.ModelSerializer):
    year = serializers.SerializerMethodField()
    operators_joined = serializers.IntegerField(source='new_operators_joined')
    operators_trained = serializers.IntegerField(source='new_operators_trained')
    
    class Meta:
        model = ManagementReview
        fields = ['year', 'month_year', 'operators_joined', 'operators_trained']
    
    def get_year(self, obj):
        return obj.month_year.year

class TrainingPlansChartSerializer(serializers.ModelSerializer):
    year = serializers.SerializerMethodField()
    training_plans = serializers.IntegerField(source='total_training_plans')
    trainings_actual = serializers.IntegerField(source='total_trainings_actual')
    
    class Meta:
        model = ManagementReview
        fields = ['year', 'month_year', 'training_plans', 'trainings_actual']
    
    def get_year(self, obj):
        return obj.month_year.year
    


    
from rest_framework import serializers
from .models import ManagementReview

class DefectsChartSerializer(serializers.ModelSerializer):
    year = serializers.SerializerMethodField()
    defects_msil = serializers.IntegerField(source='total_defects_msil')  # renaming, valid
    ctq_defects_msil = serializers.IntegerField()  # FIXED: no need for source

    class Meta:
        model = ManagementReview
        fields = ['year', 'month_year', 'defects_msil', 'ctq_defects_msil']

    def get_year(self, obj):
        return obj.month_year.year



from rest_framework import serializers

class ManagementReviewUploadSerializer(serializers.Serializer):
    file = serializers.FileField()





# serializers.py

from rest_framework import serializers
from .models import ManagementReview

class ManagementReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementReview
        fields = '__all__'


from rest_framework import serializers
from .models import CompanyLogo

class CompanyLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyLogo
        fields = ['id', 'name', 'logo', 'uploaded_at']








from rest_framework import viewsets
from .models import CompanyLogo
from .serializers import CompanyLogoSerializer

class CompanyLogoViewSet(viewsets.ModelViewSet):
    queryset = CompanyLogo.objects.all()
    serializer_class = CompanyLogoSerializer



from rest_framework import serializers
from .models import MachineAllocation

class MachineAllocationApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineAllocation
        fields = ['id', 'approval_status']

# serializers.py

from rest_framework import serializers
from .models import EmployeeMaster, MachineAllocation

class EmployeeWithStatusSerializer(serializers.ModelSerializer):
    approval_status = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeMaster
        fields = ['id', 'name', 'approval_status']  # include fields as needed

    def get_approval_status(self, obj):
        machine_id = self.context.get('machine_id')
        if machine_id:
            allocation = MachineAllocation.objects.filter(machine_id=machine_id, employee=obj).first()
            if allocation:
                return allocation.approval_status
        return None
    
from rest_framework import serializers
from .models import Department

class FactoryWiseDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']



from rest_framework import serializers
from .models import AdvancedManpowerCTQ, Factory, Department

class NewAdvancedManpowerCTQSerializer(serializers.ModelSerializer):
    factory_name = serializers.CharField(source='factory.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = AdvancedManpowerCTQ
        fields = [
            'id',
            'month_year_ctq',
            'total_stations_ctq',
            'operator_required_ctq',
            'operator_availability_ctq',
            'buffer_manpower_required_ctq',
            'buffer_manpower_availability_ctq',
            'attrition_trend_ctq',
            'absentee_trend_ctq',
            'planned_units_ctq',
            'actual_production_ctq',
            'factory',             # writeable field (ID)
            'department',          # writeable field (ID)
            'factory_name',        # read-only field for display
            'department_name'      # read-only field for display
        ]


# serializers.py


from rest_framework import serializers
from .models import AdvancedManpowerCTQ

class OperatorTrendSerializer(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()

    class Meta:
        model = AdvancedManpowerCTQ
        fields = ['month', 'operator_required_ctq', 'operator_availability_ctq']

    def get_month(self, obj):
        return obj.month_year_ctq.strftime('%B %Y')  # Example: "July 2025"







# serializers.py

class BufferManpowerTrendSerializer(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()

    class Meta:
        model = AdvancedManpowerCTQ
        fields = ['month', 'buffer_manpower_required_ctq', 'buffer_manpower_availability_ctq']

    def get_month(self, obj):
        return obj.month_year_ctq.strftime('%B %Y')  # e.g., "July 2025"





# serializers.py

class AttritionTrendSerializer(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()

    class Meta:
        model = AdvancedManpowerCTQ
        fields = ['month', 'attrition_trend_ctq']

    def get_month(self, obj):
        return obj.month_year_ctq.strftime('%B %Y')  # Example: "July 2025"





# serializers.py

class AbsenteeTrendSerializer(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()

    class Meta:
        model = AdvancedManpowerCTQ
        fields = ['month', 'absentee_trend_ctq']

    def get_month(self, obj):
        return obj.month_year_ctq.strftime('%B %Y')  # e.g., "July 2025"




# serializers.py

from rest_framework import serializers
from .models import AdvancedManpowerCTQ

class AdvancedManpowerCTQSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvancedManpowerCTQ
        fields = [
            'month_year_ctq',
            'total_stations_ctq',
            'operator_required_ctq',
            'operator_availability_ctq',
            'buffer_manpower_required_ctq',
            'buffer_manpower_availability_ctq',
        ]




# serializers.py

from rest_framework import serializers
from .models import AdvancedManpowerCTQ

class OperatorTrendSerializer(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()

    class Meta:
        model = AdvancedManpowerCTQ
        fields = ['month', 'operator_required_ctq', 'operator_availability_ctq']

    def get_month(self, obj):
        return obj.month_year_ctq.strftime('%B %Y')  # Example: "July 2025"







# serializers.py

class BufferManpowerTrendSerializer(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()

    class Meta:
        model = AdvancedManpowerCTQ
        fields = ['month', 'buffer_manpower_required_ctq', 'buffer_manpower_availability_ctq']

    def get_month(self, obj):
        return obj.month_year_ctq.strftime('%B %Y')  # e.g., "July 2025"





# serializers.py

class AttritionTrendSerializer(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()

    class Meta:
        model = AdvancedManpowerCTQ
        fields = ['month', 'attrition_trend_ctq']

    def get_month(self, obj):
        return obj.month_year_ctq.strftime('%B %Y')  # Example: "July 2025"





# serializers.py

class AbsenteeTrendSerializer(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()

    class Meta:
        model = AdvancedManpowerCTQ
        fields = ['month', 'absentee_trend_ctq']

    def get_month(self, obj):
        return obj.month_year_ctq.strftime('%B %Y')  # e.g., "July 2025"
    

from rest_framework import serializers
from .models import OperatorRequirement, Factory, Department

class OperatorRequirementSerializer(serializers.ModelSerializer):
    factory_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()

    class Meta:
        model = OperatorRequirement
        fields = [
            'id',
            'factory',
            'department',
            'month',
            'level',
            'operator_required',
            'operator_available',
            'factory_name',
            'department_name',
        ]

    def get_factory_name(self, obj):
        return obj.factory.name if obj.factory else None

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def validate(self, data):
        factory = data.get('factory')
        department = data.get('department')

        # Optional: Validate department belongs to the selected factory
        if department and factory and department.factory_id != factory.id:
            raise serializers.ValidationError("The selected department does not belong to the given factory.")
        return data
    



from rest_framework import serializers
from .models import UploadedFile

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['id', 'title', 'file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']







from rest_framework import serializers
from .models import Score, EmployeeMaster

class LevelOneEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeMaster
        fields = '__all__'

class LevelOneScoreSerializer(serializers.ModelSerializer):
    employee = LevelOneEmployeeSerializer()

    class Meta:
        model = Score
        fields = ['employee', 'marks', 'test_name', 'percentage', 'passed', 'level', 'created_at']






from rest_framework import serializers
from .models import Score, Station, LevelTwoTraineeInfo

class LevelTwoStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ['id', 'skill']

class LevelTwoScoreMiniSerializer(serializers.ModelSerializer):
    skill = StationSerializer()

    class Meta:
        model = Score
        fields = ['passed', 'skill']

class LevelTwoTraineeInfoMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelTwoTraineeInfo
        fields = ['traineeId', 'station', 'line', 'training_status']

class LevelTwoGroupedEmployeeScoreSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    employee_name = serializers.CharField()
    trainee_info = serializers.SerializerMethodField()
    scores = serializers.SerializerMethodField()

    def get_trainee_info(self, obj):
        from .models import LevelTwoTraineeInfo
        try:
            trainee = LevelTwoTraineeInfo.objects.get(trainee_name=obj['employee_name'])
            return LevelTwoTraineeInfoMiniSerializer(trainee).data
        except LevelTwoTraineeInfo.DoesNotExist:
            return None

    def get_scores(self, obj):
        scores = obj['scores']
        return LevelTwoScoreMiniSerializer(scores, many=True).data








from rest_framework import serializers
from .models import Score, Station, LevelThreeTraineeInfo  # <-- Make sure this model exists

class LevelThreeStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ['id', 'skill']

class LevelThreeScoreMiniSerializer(serializers.ModelSerializer):
    skill = LevelThreeStationSerializer()

    class Meta:
        model = Score
        fields = ['passed', 'skill']

class LevelThreeTraineeInfoMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelThreeTraineeInfo
        fields = ['traineeId', 'station', 'line', 'training_status']

class LevelThreeGroupedEmployeeScoreSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    employee_name = serializers.CharField()
    trainee_info = serializers.SerializerMethodField()
    scores = serializers.SerializerMethodField()

    def get_trainee_info(self, obj):
        try:
            trainee = LevelThreeTraineeInfo.objects.get(trainee_name=obj['employee_name'])
            return LevelThreeTraineeInfoMiniSerializer(trainee).data
        except LevelThreeTraineeInfo.DoesNotExist:
            return None

    def get_scores(self, obj):
        scores = obj['scores']
        return LevelThreeScoreMiniSerializer(scores, many=True).data
