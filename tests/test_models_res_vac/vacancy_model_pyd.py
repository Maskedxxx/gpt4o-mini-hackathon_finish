from typing import List, Optional, Union
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from datetime import datetime

# Basic reusable model for objects with 'id' and 'name'
class VacancyIdNamePair(BaseModel):
    id: str
    name: str

class VacancyArea(BaseModel):
    id: str
    name: str
    url: HttpUrl

# Address related models
class MetroStation(BaseModel):
    lat: float
    line_id: str
    line_name: str
    lng: float
    station_id: str
    station_name: str

class Address(BaseModel):
    building: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    metro_stations: List[MetroStation] = Field(default_factory=list)
    street: Optional[str] = None
    # raw: Optional[str] = None # Example: "Москва, улица Годовикова, 9с10" - Not in provided JSON
    # id: Optional[str] = None # Not in provided JSON

class BrandedTemplate(BaseModel):
    id: str
    name: str

# Contacts related models
class Phone(BaseModel):
    city: Optional[str] = None
    comment: Optional[str] = None
    country: Optional[str] = None
    number: Optional[str] = None
    # formatted: Optional[str] = None # Not in provided JSON, but often available e.g. "+7 (985) 000-00-00"

class Contacts(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    phones: List[Phone] = Field(default_factory=list)

class Department(BaseModel):
    id: str
    name: str

class DriverLicenseType(BaseModel):
    id: str

# Employer related models
class Badge(BaseModel):
    description: Optional[str] = None
    position: Optional[str] = None # e.g. "2", could be int as well
    type: Optional[str] = None
    url: Optional[HttpUrl] = None
    year: Optional[int] = None

class LogoUrls(BaseModel):
    logo_90: Optional[HttpUrl] = Field(default=None, alias="90")
    logo_240: Optional[HttpUrl] = Field(default=None, alias="240")
    original: Optional[HttpUrl] = None

class Employer(BaseModel):
    alternate_url: Optional[HttpUrl] = None
    badges: List[Badge] = Field(default_factory=list)
    blacklisted: Optional[bool] = None
    id: str
    logo_urls: Optional[LogoUrls] = None
    name: str
    trusted: bool
    url: HttpUrl
    # vacancies_url: Optional[HttpUrl] = None # Not in provided JSON
    # accredited_it_employer: Optional[bool] = None # Not in provided JSON

class InsiderInterview(BaseModel):
    id: str
    url: HttpUrl

class KeySkill(BaseModel):
    name: str

# Language related models
class LanguageLevel(BaseModel):
    id: str
    name: str

class Language(BaseModel):
    id: str
    level: LanguageLevel
    name: str

class Manager(BaseModel):
    id: str
    # name: Optional[str] = None # Not in provided JSON

class ProfessionalRole(VacancyIdNamePair): # Inherits id, name
    pass

# Salary related models
class Salary(BaseModel):
    currency: Optional[str] = None
    from_amount: Optional[int] = Field(default=None, alias="from")
    gross: Optional[bool] = None
    to_amount: Optional[int] = Field(default=None, alias="to")

class SalaryRangeFrequency(VacancyIdNamePair):
    pass

class SalaryRangeMode(VacancyIdNamePair):
    pass

class SalaryRange(BaseModel):
    currency: Optional[str] = None
    frequency: Optional[SalaryRangeFrequency] = None
    from_amount: Optional[int] = Field(default=None, alias="from")
    gross: Optional[bool] = None
    mode: Optional[SalaryRangeMode] = None
    to_amount: Optional[int] = Field(default=None, alias="to")


class Test(BaseModel):
    required: bool

# VideoVacancy related models
class CoverPicture(BaseModel):
    resized_height: Optional[int] = None
    resized_path: Optional[HttpUrl] = None
    resized_width: Optional[int] = None

class VideoVacancy(BaseModel):
    cover_picture: Optional[CoverPicture] = None
    video_url: Optional[HttpUrl] = None


# Main Vacancy Model
class Vacancy(BaseModel):
    accept_handicapped: bool
    accept_incomplete_resumes: bool
    accept_kids: bool
    accept_temporary: bool
    address: Optional[Address] = None
    allow_messages: bool
    alternate_url: HttpUrl
    apply_alternate_url: HttpUrl
    approved: bool
    archived: bool
    area: VacancyArea
    billing_type: VacancyIdNamePair
    branded_description: Optional[str] = None
    branded_template: Optional[BrandedTemplate] = None
    can_upgrade_billing_type: Optional[bool] = None
    code: Optional[str] = None
    contacts: Optional[Contacts] = None
    created_at: datetime
    department: Optional[Department] = None
    description: str
    driver_license_types: List[DriverLicenseType] = Field(default_factory=list)
    employer: Employer
    employment: VacancyIdNamePair
    experience: VacancyIdNamePair
    expires_at: Optional[datetime] = None
    has_test: bool
    hidden: Optional[bool] = None # Not in example, but often exists
    id: str
    initial_created_at: datetime
    insider_interview: Optional[InsiderInterview] = None
    internship: Optional[bool] = None # Based on example value
    key_skills: List[KeySkill] = Field(default_factory=list)
    languages: List[Language] = Field(default_factory=list)
    manager: Optional[Manager] = None
    name: str # Vacancy title
    night_shifts: Optional[bool] = None # Based on example value
    premium: bool
    professional_roles: List[ProfessionalRole] = Field(default_factory=list)
    published_at: datetime
    response_letter_required: bool
    response_notifications: Optional[bool] = None # Assuming it could be optional
    response_url: Optional[HttpUrl] = None
    salary: Optional[Salary] = None
    salary_range: Optional[SalaryRange] = None
    schedule: VacancyIdNamePair
    test: Optional[Test] = None
    type: VacancyIdNamePair # Vacancy type e.g. "Открытая"
    video_vacancy: Optional[VideoVacancy] = None
    work_format: List[VacancyIdNamePair] = Field(default_factory=list)
    work_schedule_by_days: List[VacancyIdNamePair] = Field(default_factory=list)
    working_days: List[VacancyIdNamePair] = Field(default_factory=list)
    working_hours: List[VacancyIdNamePair] = Field(default_factory=list)
    working_time_intervals: List[VacancyIdNamePair] = Field(default_factory=list)
    working_time_modes: List[VacancyIdNamePair] = Field(default_factory=list)

# Example usage (optional, for testing)
if __name__ == "__main__":
    json_data = {
      "accept_handicapped": False,
      "accept_incomplete_resumes": False,
      "accept_kids": False,
      "accept_temporary": False,
      "address": {
        "building": "9с10",
        "city": "Москва",
        "description": "На проходной потребуется паспорт",
        "lat": 55.807794,
        "lng": 37.638699,
        "metro_stations": [
          {
            "lat": 55.807794,
            "line_id": "6",
            "line_name": "Калужско-Рижская",
            "lng": 37.638699,
            "station_id": "6.8",
            "station_name": "Алексеевская"
          }
        ],
        "street": "улица Годовикова"
      },
      "allow_messages": True,
      "alternate_url": "https://hh.ru/vacancy/8331228",
      "apply_alternate_url": "https://hh.ru/applicant/vacancy_response?vacancyId=8331228",
      "approved": False,
      "archived": False,
      "area": {
        "id": "1",
        "name": "Москва",
        "url": "https://api.hh.ru/areas/1"
      },
      "billing_type": {
        "id": "standard",
        "name": "Стандарт"
      },
      "branded_description": "<style>...</style><div>...</div><script></script>",
      "branded_template": {
        "id": "1",
        "name": "test"
      },
      "can_upgrade_billing_type": True,
      "code": "HRR-3487",
      "contacts": {
        "email": "user@example.com",
        "name": "Имя",
        "phones": [
          {
            "city": "985",
            "comment": None,
            "country": "7",
            "number": "000-00-00"
          }
        ]
      },
      "created_at": "2013-07-08T16:17:21+0400",
      "department": {
        "id": "HH-1455-TECH",
        "name": "HeadHunter::Технический департамент"
      },
      "description": "Работа хороша",
      "driver_license_types": [
        { "id": "A" },
        { "id": "B" }
      ],
      "employer": {
        "alternate_url": "https://hh.ru/employer/1455",
        "badges": [
          {
            "description": "2-е место в Рейтинге работодателей России (небольшие компании)",
            "position": "2",
            "type": "employer-hh-rating",
            "url": "https://rating.hh.ru/profile/rating2020",
            "year": 2020
          }
        ],
        "blacklisted": False,
        "id": "1455",
        "logo_urls": {
          "90": "https://hh.ru/employer-logo/289027.png",
          "240": "https://hh.ru/employer-logo/289169.png",
          "original": "https://hh.ru/file/2352807.png"
        },
        "name": "HeadHunter",
        "trusted": True,
        "url": "https://api.hh.ru/employers/1455"
      },
      "employment": { "id": "full", "name": "Полная занятость" },
      "experience": { "id": "between1And3", "name": "От 1 года до 3 лет" },
      "expires_at": "2013-08-08T16:17:21+0400",
      "has_test": True,
      "hidden": False, # Example data has 'hidden', so remove Optional or ensure it's always there. For now, assuming it's like other booleans.
      "id": "8331228",
      "initial_created_at": "2013-06-08T16:17:21+0400",
      "insider_interview": {
        "id": "12345",
        "url": "https://hh.ru/interview/12345?employerId=777"
      },
      "internship": False,
      "key_skills": [
        { "name": "Прием посетителей" },
        { "name": "Первичный документооборот" }
      ],
      "languages": [
        {
          "id": "eng",
          "level": { "id": "b2", "name": "B2 — Средне-продвинутый" },
          "name": "Английский"
        }
      ],
      "manager": { "id": "1" },
      "name": "Секретарь",
      "night_shifts": True,
      "premium": True,
      "professional_roles": [ { "id": "96", "name": "Программист, разработчик" } ],
      "published_at": "2013-07-08T16:17:21+0400",
      "response_letter_required": True,
      "response_notifications": True, # Present in example
      "response_url": None,
      "salary": {
        "currency": "RUR",
        "from": 30000,
        "gross": True,
        "to": None
      },
      "salary_range": {
        "currency": "RUR",
        "frequency": { "id": "MONTHLY", "name": "Раз в месяц" },
        "from": 30000,
        "gross": True,
        "mode": { "id": "MONTH", "name": "За месяц" },
        "to": None
      },
      "schedule": { "id": "fullDay", "name": "Полный день" },
      "test": { "required": False },
      "type": { "id": "open", "name": "Открытая" },
      "video_vacancy": {
        "cover_picture": {
          "resized_height": 444,
          "resized_path": "https://img.hhcdn.ru/branding-pictures-original/2229739.png",
          "resized_width": 788
        },
        "video_url": "https://host/video/123"
      },
      "work_format": [ { "id": "ON_SITE", "name": "На месте работодателя" } ],
      "work_schedule_by_days": [ { "id": "WEEKEND", "name": "По выходным" } ],
      "working_days": [ { "id": "only_saturday_and_sunday", "name": "Работа только по сб и вс" } ],
      "working_hours": [ { "id": "HOURS_4", "name": "4 часа" } ],
      "working_time_intervals": [ { "id": "from_four_to_six_hours_in_a_day", "name": "Можно работать сменами по 4-6 часов в день" } ],
      "working_time_modes": [ { "id": "start_after_sixteen", "name": "Можно начинать работать после 16-00" } ]
    }

    # The field "hidden" was in your example as "hidden": false.
    # If it's always present, you can remove Optional from its definition in the Vacancy model.
    # If it can be missing, Optional[bool] is correct. I'll keep it Optional for now.
    if "hidden" not in json_data: # if hidden is truly optional and not in this specific snippet
        json_data["hidden"] = None


    vacancy_instance = Vacancy(**json_data)
    # print(vacancy_instance.model_dump_json(indent=2, by_alias=True, ensure_ascii=False))
    print("Pydantic model for Vacancy created successfully and validated against sample data.")