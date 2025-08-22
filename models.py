from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Dict, List, Optional, Any
from typing_extensions import Literal

class GoogleLoginRequest(BaseModel):
    email: EmailStr
    role: Literal["patient", "doctor", "admin"]

class LoginRequest(BaseModel):
    identifier: str  # email OR uhid OR phone number
    password: str
    role: str  # "admin", "doctor", "patient"

class Doctor(BaseModel):
    doctor_name: str
    gender: Literal["male", "female", "other"]
    dob: str
    email: EmailStr
    designation: str
    uhid : str
    phone_number : str
    blood_group: str
    password: str
    admin_created: str

    class Config:
        schema_extra = {
            "example": {
                "doctor_name": "Dr. John Smith",
                "gender": "male",
                "dob": "02-02-1995",
                "uhid" : "UH123456",
                "admin_created": "APM",
                "designation": "leg surgeon",
                "phone_number": "1234567890",
                "blood_group": "A+",
                "email": "dr.john@example.com",
                "password": "securePass123",
            }
        }

class Admin(BaseModel):
    admin_name: str
    gender: Literal["male", "female", "other"]
    dob: str
    password: str
    uhid : str
    phone_number : str
    email: EmailStr

    class Config:
        schema_extra = {
            "example": {
                "admin_name": "Alice Admin",
                "gender": "female",
                "dob": "02-02-1995",
                "phone_number": "1234567890",
                "password": "adminSecure@456",
                "email": "alice.admin@example.com",
            }
        }

# class Patient(BaseModel):
#     uhid: str
#     first_name: str
#     last_name: str
#     password: str
#     vip: Literal[0, 1]
#     dob: str
#     blood_grp: str
#     gender: Literal["male", "female", "other"]
#     height: float
#     weight: float
#     email: EmailStr
#     phone_number: str
#     alternate_phone: str = Field(..., alias="alternatenumber")
#     address: str
#     doctor_uhid: str
#     admin_uhid: str
#     opd_appointment_date: str
#     activation_status: bool
#     activation_comment: Optional[List[Dict[str, Any]]] = []
#     operation_funding: str = Field(..., alias="operationfundion")
#     id_proof: Optional[Dict[str, str]] = Field(default_factory=dict, alias="idproof")

class QuestionnaireAssignment(BaseModel):
    uhid: str
    side: Literal["left", "right"]
    name: str
    period: str
    assigned_date: str
    deadline: str
    completed: int

class QuestionnaireScore(BaseModel):
    uhid: str
    side: Literal["left", "right"]
    name: str
    score: List[int]
    period: str
    timestamp: str
    others: Optional[List[str]] = []

class PostSurgeryDetail(BaseModel):
    uhid: str
    side: Literal["left", "right"]
    patient_records: List["PostSurgeryRecord"]

class ROM(BaseModel):
    period: str
    flexion: str
    extension: str

class ComponentDetail(BaseModel):
    MANUFACTURER: str
    MODEL: str
    SIZE: str

class ComponentDetails(BaseModel):
    FEMUR: ComponentDetail
    TIBIA: ComponentDetail
    INSERT: ComponentDetail
    PATELLA: ComponentDetail

class ThicknessDetail(BaseModel):
    thickness: int
    numOfTicks: str
    extensionExtOrient: str
    flexionIntOrient: str
    liftOff: str

class BoneResection(BaseModel):
    acl: str
    distal_medial: Dict[str, str]
    distal_lateral: Dict[str, str]
    posterial_medial: Dict[str, str]
    posterial_lateral: Dict[str, str]
    tibial_resection_left: Dict[str, str]
    tibial_resection_right: Dict[str, str]
    pcl: str
    tibialvvrecut: Dict[str, str]
    tibialsloperecut: Dict[str, str]
    final_check: str
    thickness_table: List[ThicknessDetail]
    pfj_resurfacing: str
    trachela_resection: str
    patella: str
    preresurfacing: str
    postresurfacing: str

class PostSurgeryRecord(BaseModel):
    patuhid: str
    hospital_name: str
    anaesthetic_type: str
    asa_grade: str
    rom: List[ROM]
    consultant_incharge: str
    operating_surgeon: str
    first_assistant: str
    second_assistant: str
    mag_proc: str
    side: str
    surgery_indication: str
    tech_assist: str
    align_phil: str
    torq_used: str
    op_date: str
    op_time: str
    components_details: ComponentDetails
    bone_resection: BoneResection
    posting_timestamp: str

class PatientBase(BaseModel):
    uhid: str
    first_name: str
    last_name: str
    password: str
    vip: Literal[0, 1]
    dob: str
    gender: Literal["male", "female", "other"]

class PatientContact(BaseModel):
    uhid: str
    email: EmailStr
    phone_number: str
    alternate_phone: str = Field(..., alias="alternatenumber")
    address: str
    doctor_uhid_left: str
    doctor_uhid_right: str
    admin_uhid: str
    opd_appointment_date: str
    profile_picture_url: Optional[str] = None  # Add this line

class PatientMedical(BaseModel):
    uhid: str
    blood_grp: str
    height: float
    weight: float
    activation_status: bool
    activation_comment: Optional[List[Dict[str, Any]]] = []
    operation_funding: str = Field(..., alias="operationfundion")
    id_proof: Optional[Dict[str, str]] = Field(default_factory=dict, alias="idproof")


###extra stuff for deletion (maybe)


# class QuestionnaireUpdateRequest(BaseModel):
#     uhid: str
#     name: str
#     period: str
#     completed: int = 1  # Default is 1 (completed)
#     leg: str

# class QuestionnaireAssignedLeft(BaseModel):
#     name: str
#     period: str
#     assigned_date: str
#     deadline: str
#     completed: Literal[0, 1]

# class QuestionnaireScoreLeft(BaseModel):
#     name: str
#     score: List[float]
#     period: str
#     timestamp: datetime
#     others: List[str]

# class QuestionnaireAssignedRight(BaseModel):
#     name: str
#     period: str
#     assigned_date: str
#     deadline: str
#     completed: Literal[0, 1]

# class QuestionnaireScoreRight(BaseModel):
#     name: str
#     score: List[float]
#     period: str
#     timestamp: datetime
#     others: List[str]

# class SurgeryScheduledLeft(BaseModel):
#     date: str
#     time: str  # or use datetime if you prefer combining date & time

# class SurgeryScheduledRight(BaseModel):
#     date: str
#     time: str  # or use datetime if you prefer combining date & time

# class PostSurgeryDetailsLeft(BaseModel):
#     date_of_surgery: datetime
#     surgeon: str
#     surgery_name: str
#     sub_doctor: str
#     procedure: str
#     implant: str
#     technology: str

# class PostSurgeryDetailsRight(BaseModel):
#     date_of_surgery: datetime
#     surgeon: str
#     surgery_name: str
#     sub_doctor: str
#     procedure: str
#     implant: str
#     technology: str

# class Patient1(BaseModel):
#     uhid: str
#     first_name: str
#     last_name: str
#     password: str
#     vip: Literal[0, 1]
#     dob: str  # or `datetime.date` with parsing
#     age: int
#     blood_grp: str
#     gender: Literal["male", "female", "other"]
#     height: float
#     weight: float
#     bmi: float
#     email: EmailStr
#     phone_number: str
#     alternate_phone: str = Field(..., alias="alternatenumber")
#     address: str
#     doctor_assigned: Optional[str] = None
#     doctor_name: Optional[str] = None
#     admin_assigned: Optional[str] = None
#     admin_name: Optional[str] = None
#     questionnaire_assigned_left: Optional[List[QuestionnaireAssignedLeft]] = []
#     questionnaire_scores_left: Optional[List[QuestionnaireScoreLeft]] = []
#     questionnaire_assigned_right: Optional[List[QuestionnaireAssignedRight]] = []
#     questionnaire_scores_right: Optional[List[QuestionnaireScoreRight]] = []
#     surgery_scheduled_left: Optional[SurgeryScheduledLeft] = None
#     surgery_scheduled_right: Optional[SurgeryScheduledRight] = None
#     post_surgery_details_left: Optional[PostSurgeryDetailsLeft] = None
#     post_surgery_details_right: Optional[PostSurgeryDetailsRight] = None
#     opd_appointment_date: str
#     activation_status: bool
#     activation_comment: Optional[List[Dict[str, Any]]] = []
#     operation_funding: str = Field(..., alias="operationfundion")
#     id_proof: Optional[Dict[str, str]] = Field(default_factory=dict, alias="idproof")

    
#     class Config:
#         schema_extra = {
#             "example": {
#                 "uhid": "UH123456",
#                 "first_name": "John",
#                 "last_name": "Doe",
#                 "password": "password123",
#                 "vip": 0,
#                 "dob": "1990-05-15",
#                 "blood_grp": "O+",
#                 "gender": "male",
#                 "height": 175.0,
#                 "weight": 70.0,
#                 "bmi": 22.86,
#                 "email": "john.doe@example.com",
#                 "phone_number": "1234567890",
#                 "doctor_assigned": "doctor_01",
#                 "admin_assigned": "admin_01",
#                 "doctor_name": "doctor_01",
#                 "admin_name": "admin_01",
#                 "questionnaire_assigned_left": [
#                     {
#                         "name": "Mobility Survey",
#                         "period": "weekly",
#                         "assigned_date": "2025-04-01T10:00:00",
#                         "deadline": "2025-04-01T10:00:00",
#                         "completed": 0
#                     },
#                     {
#                         "name": "Pain Assessment",
#                         "period": "daily",
#                         "assigned_date": "2025-04-02T08:00:00",
#                         "deadline": "2025-04-01T10:00:00",
#                         "completed": 1
#                     }
#                 ],
#                 "questionnaire_scores_left": [
#                     {
#                         "name": "Mobility Survey",
#                         "score": 85.5,
#                         "period": "weekly",
#                         "timestamp": "2025-04-01T10:30:00"
#                     },
#                     {
#                         "name": "Pain Assessment",
#                         "score": 92.0,
#                         "period": "weekly",
#                         "timestamp": "2025-04-02T08:30:00"
#                     }
#                 ],
#                 "questionnaire_assigned_right": [
#                     {
#                         "name": "Mobility Survey",
#                         "period": "weekly",
#                         "assigned_date": "2025-04-01T10:00:00",
#                         "deadline": "2025-04-01T10:00:00",
#                         "completed": 0
#                     },
#                     {
#                         "name": "Pain Assessment",
#                         "period": "daily",
#                         "assigned_date": "2025-04-02T08:00:00",
#                         "deadline": "2025-04-01T10:00:00",
#                         "completed": 1
#                     }
#                 ],
#                 "questionnaire_scores_right": [
#                     {
#                         "name": "Mobility Survey",
#                         "score": 85.5,
#                         "period": "weekly",
#                         "timestamp": "2025-04-01T10:30:00"
#                     },
#                     {
#                         "name": "Pain Assessment",
#                         "score": 92.0,
#                         "period": "weekly",
#                         "timestamp": "2025-04-02T08:30:00"
#                     }
#                 ],
#                 "surgery_scheduled": {
#                     "date": "2025-05-10",
#                     "time": "08:00"
#                 },
#                 "post_surgery_details_left": {
#                     "date_of_surgery": "2025-05-10",
#                     "surgeon": "Dr. Strange",
#                     "surgery_name": "knee replacement",
#                     "procedure": "Knee Replacement is a part of leg helping",
#                     "implant": "Titanium",
#                     "technology": "Robotic Assisted"
#                 },
#                 "post_surgery_details_right": {
#                     "date_of_surgery": "2025-05-10",
#                     "surgeon": "Dr. Strange",
#                     "surgery_name": "knee replacement",
#                     "procedure": "Knee Replacement is a part of leg helping",
#                     "implant": "Titanium",
#                     "technology": "Robotic Assisted"
#                 },
#                 "current_status": "pre_op",
#             }
#         }


# class Patient(BaseModel):
#     key: str
#     value: Any


# class PatientResponse(Patient):
#     age: int  # override to make it visible

#     @classmethod
#     def from_patient(cls, patient: Patient):
#         return cls(**patient.dict(), age=patient.age)


# class ReminderAlertMessage(BaseModel):
#     message: str
#     timestamp: datetime
#     read: Literal[0, 1]

# class Notification(BaseModel):
#     uhid: str
#     notifications: List[ReminderAlertMessage] = []

#     class Config:
#         schema_extra = {
#             "example": {
#                 "uhid": "UH123456",
#                 "notifications": [
#                     {
#                         "message": "Please complete your questionnaire.",
#                         "timestamp": "2025-04-05T12:00:00",
#                         "read": 0
#                     },
#                     {
#                         "message": "Your surgery is scheduled for May 10 at 08:00.",
#                         "timestamp": "2025-04-07T09:00:00",
#                         "read": 1
#                     }
#                 ]
#             }
#         }

# class MarkReadRequest(BaseModel):
#     uhid: str
#     message: str  

# class DoctorAssignRequest(BaseModel):
#     uhid: str
#     doctor_assigned: str


# class QuestionnaireAppendRequestLeft(BaseModel):
#     uhid: str
#     questionnaire_assigned_left: List[QuestionnaireAssignedLeft]

# class QuestionnaireScoreAppendRequestLeft(BaseModel):
#     uhid: str
#     questionnaire_scores_left: List[QuestionnaireScoreLeft]

# class QuestionnaireAppendRequestRight(BaseModel):
#     uhid: str
#     questionnaire_assigned_right: List[QuestionnaireAssignedRight]

# class QuestionnaireScoreAppendRequestRight(BaseModel):
#     uhid: str
#     questionnaire_scores_right: List[QuestionnaireScoreRight]

# class SurgeryScheduleUpdateRequestLeft(BaseModel):
#     uhid: str
#     surgery_scheduled_left: SurgeryScheduledLeft

# class SurgeryScheduleUpdateRequestRight(BaseModel):
#     uhid: str
#     surgery_scheduled_right: SurgeryScheduledRight

# class PostSurgeryDetailsUpdateRequestLeft(BaseModel):
#     uhid: str
#     post_surgery_details_left: PostSurgeryDetailsLeft

# class PostSurgeryDetailsUpdateRequestRight(BaseModel):
#     uhid: str
#     post_surgery_details_right: PostSurgeryDetailsRight

# class PasswordResetRequest(BaseModel):
#     uhid: str
#     new_password: str

# class EmailRequest(BaseModel):
#     name: str
#     email: str
#     subject: str
#     message: str

# class QuestionnaireResetRequest(BaseModel):
#     period: str
#     questionnaires: list[str]


# class WhatsappMessageRequest(BaseModel):
#     user_name: str
#     phone_number: str
#     message: str
#     flag: int


# class Patientregisterdynamic(BaseModel):
#     key: str
#     value: Any


# class ProfilePic(BaseModel):
#     uhid: str
#     profile_image_url: HttpUrl

#     class Config:
#         schema_extra = {
#             "example": {
#                 "uhid": "UH123456",
#                 "profile_image_url": "https://your-bucket.s3.ap-south-1.amazonaws.com/doctor_abc123.png"
#             }
#         }