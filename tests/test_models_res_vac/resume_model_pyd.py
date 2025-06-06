from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime, date

# ... (все остальные ваши модели остаются без изменений) ...

class Area(BaseModel):
    id: str
    name: str
    url: HttpUrl

class Gender(BaseModel):
    id: str
    name: str

class Salary(BaseModel):
    amount: int
    currency: str

class Photo(BaseModel):
    id: str
    small: HttpUrl
    medium: HttpUrl
    forty: HttpUrl = Field(alias="40")
    one_hundred: HttpUrl = Field(alias="100")
    five_hundred: HttpUrl = Field(alias="500")

class TotalExperience(BaseModel):
    months: int

class Certificate(BaseModel):
    owner: Optional[Any] = None
    type: str
    title: str
    achieved_at: date
    url: HttpUrl

class DownloadURL(BaseModel):
    url: HttpUrl

class DownloadOptions(BaseModel):
    pdf: DownloadURL
    rtf: DownloadURL

class Actions(BaseModel):
    download: DownloadOptions

class Platform(BaseModel):
    id: str

class ResumeLocale(BaseModel):
    id: str
    name: str

class IdNameUrlPair(BaseModel): # Reusable for Citizenship, WorkTicket
    id: str
    name: str
    url: HttpUrl

class AccessType(BaseModel):
    id: str
    name: str

class Access(BaseModel):
    type: AccessType

class ContactValuePhone(BaseModel):
    country: str
    city: str
    number: str
    formatted: str

class ContactType(BaseModel):
    id: str
    name: str

class ContactItem(BaseModel):
    value: Union[ContactValuePhone, str]
    type: ContactType
    preferred: bool
    comment: Optional[str] = None
    need_verification: Optional[bool] = None
    verified: Optional[bool] = None

class EducationLevel(BaseModel):
    id: str
    name: str

class EducationPrimaryItem(BaseModel):
    id: str
    name: str
    organization: Optional[str] = None
    result: Optional[str] = None
    year: int
    university_acronym: Optional[str] = None
    name_id: Optional[str] = None
    organization_id: Optional[str] = None
    result_id: Optional[Any] = None
    education_level: EducationLevel

class EducationAdditionalItem(BaseModel):
    id: str
    name: str
    organization: str
    result: Optional[str] = None
    year: int

class Education(BaseModel):
    level: EducationLevel
    primary: List[EducationPrimaryItem]
    additional: List[EducationAdditionalItem]
    attestation: List[Any]
    elementary: List[Any]

class IdNamePair(BaseModel): # Reusable for Employment, Employments item, Schedule, etc.
    id: str
    name: str

class Industry(BaseModel):
    id: str
    name: str

class EmployerLogoUrls(BaseModel):
    ninety: Optional[HttpUrl] = Field(default=None, alias="90")
    two_hundred_forty: Optional[HttpUrl] = Field(default=None, alias="240")
    original: Optional[HttpUrl] = None

class Employer(BaseModel):
    id: str
    name: str
    url: Optional[HttpUrl] = None
    alternate_url: Optional[HttpUrl] = None
    logo_urls: Optional[EmployerLogoUrls] = None

class ExperienceItem(BaseModel):
    start: date
    end: Optional[date] = None
    company: str
    company_id: Optional[str] = None
    industry: Optional[Any] = None
    industries: List[Industry]
    area: Optional[Area] = None
    company_url: Optional[HttpUrl] = None
    employer: Optional[Employer] = None
    position: str
    description: str

class LanguageLevel(BaseModel):
    id: str
    name: str

class LanguageItem(BaseModel):
    id: str
    name: str
    level: LanguageLevel

class RelocationType(BaseModel):
    id: str
    name: str

class Relocation(BaseModel):
    type: RelocationType
    area: List[Any]
    district: List[Any]

class SiteType(BaseModel):
    id: str
    name: str

class SiteItem(BaseModel):
    type: SiteType
    url: Union[HttpUrl, str] # Can be a URL or a string (e.g. GitHub link for Skype)

class PaidService(BaseModel):
    id: str
    name: str
    active: bool

class DriverLicenseType(BaseModel):
    id: str

class ProfessionalRole(BaseModel):
    id: str
    name: str

class ProgressRecommendedItem(BaseModel):
    id: str
    name: str

class ProgressModel(BaseModel):
    percentage: int
    mandatory: List[Any]
    recommended: List[ProgressRecommendedItem]

class UnderscoreProgress(BaseModel): # Это модель для поля "_progress"
    percentage: int
    mandatory: List[Any]
    recommended: List[str]

# Main Resume Model
class Resume(BaseModel):
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    title: str
    created_at: datetime
    updated_at: datetime
    area: Area
    age: Optional[int] = None
    gender: Gender
    salary: Optional[Salary] = None
    photo: Optional[Photo] = None
    total_experience: Optional[TotalExperience] = None
    certificate: List[Certificate]
    hidden_fields: List[Any]
    actions: Actions
    alternate_url: HttpUrl
    id: str
    download: DownloadOptions
    platform: Platform
    employment_form: Optional[Any] = None
    fly_in_fly_out_duration: List[Any]
    internship: Optional[Any] = None
    night_shifts: Optional[Any] = None
    ready_for_temporary_job: Optional[Any] = None
    work_format: List[Any]
    working_hours: List[Any]
    work_schedule_by_days: List[Any]
    resume_locale: ResumeLocale
    skills: Optional[str] = None
    citizenship: List[IdNameUrlPair]
    work_ticket: List[IdNameUrlPair]
    access: Access
    birth_date: Optional[date] = None
    contact: List[ContactItem]
    education: Education
    employment: Optional[IdNamePair] = None
    employments: List[IdNamePair]
    experience: List[ExperienceItem]
    language: List[LanguageItem]
    metro: Optional[Any] = None
    moderation_note: List[Any]
    recommendation: List[Any]
    relocation: Relocation
    schedule: IdNamePair
    schedules: List[IdNamePair]
    site: List[SiteItem]
    travel_time: IdNamePair
    business_trip_readiness: IdNamePair
    next_publish_at: Optional[datetime] = None
    can_publish_or_update: Optional[bool] = None
    publish_url: Optional[HttpUrl] = None
    paid_services: List[PaidService]
    finished: bool
    blocked: bool
    status: IdNamePair
    portfolio: List[Any]
    skill_set: List[str]
    has_vehicle: Optional[bool] = None
    driver_license_types: List[DriverLicenseType]
    specialization: List[Any]
    professional_roles: List[ProfessionalRole]
    tags: List[Any]
    progress: ProgressModel # Используем ProgressModel без alias, т.к. имя поля совпадает
    # Исправленное поле:
    progress_alternative_name: UnderscoreProgress = Field(alias="_progress") # Имя поля в Python изменено, alias сохранен

    total_views: Optional[int] = None
    new_views: Optional[int] = None
    views_url: Optional[HttpUrl] = None

# Пример использования (не изменился, но теперь должен работать без ошибки)
if __name__ == "__main__":
    json_data = {
      "last_name": "Немов",
      "first_name": "Максим",
      "middle_name": "Юрьевич",
      "title": "LLM Engineer",
      "created_at": "2025-05-16T08:25:26+0300",
      "updated_at": "2025-05-16T08:26:29+0300",
      "area": {
        "id": "71",
        "name": "Пенза",
        "url": "https://api.hh.ru/areas/71"
      },
      "age": 34,
      "gender": {
        "id": "male",
        "name": "Мужской"
      },
      "salary": {
        "amount": 230000,
        "currency": "RUR"
      },
      "photo": {
        "id": "123491316",
        "small": "https://img.hhcdn.ru/photo/554741834.jpeg?t=1747635993&h=gF-9f0kmqEVkBjtUZBl_ag",
        "medium": "https://img.hhcdn.ru/photo/554741835.jpeg?t=1747635993&h=h4Wc9HAlPTZ9Zp37hR-Gow",
        "40": "https://img.hhcdn.ru/photo/554741833.jpeg?t=1747635993&h=iTpb57Ly54QRCIba8y6BYA",
        "100": "https://img.hhcdn.ru/photo/554741834.jpeg?t=1747635993&h=gF-9f0kmqEVkBjtUZBl_ag",
        "500": "https://img.hhcdn.ru/photo/554741835.jpeg?t=1747635993&h=h4Wc9HAlPTZ9Zp37hR-Gow"
      },
      "total_experience": {
        "months": 40
      },
      "certificate": [
        {
          "owner": None,
          "type": "custom",
          "title": "Специализиция \"Data Engineering\"",
          "achieved_at": "2025-01-01",
          "url": "https://coursera.org/share/14fa929b753068ffaa46c93f5162843e"
        }
      ],
      "hidden_fields": [],
      "actions": {
        "download": {
          "pdf": {
            "url": "https://api.hh.ru/resumes/6d807532ff0ed6b79f0039ed1f63386d724a62/download/%D0%9D%D0%B5%D0%BC%D0%BE%D0%B2%20%D0%9C%D0%B0%D0%BA%D1%81%D0%B8%D0%BC%20%D0%AE%D1%80%D1%8C%D0%B5%D0%B2%D0%B8%D1%87.pdf?type=pdf"
          },
          "rtf": {
            "url": "https://api.hh.ru/resumes/6d807532ff0ed6b79f0039ed1f63386d724a62/download/%D0%9D%D0%B5%D0%BC%D0%BE%D0%B2%20%D0%9C%D0%B0%D0%BA%D1%81%D0%B8%D0%BC%20%D0%AE%D1%80%D1%8C%D0%B5%D0%B2%D0%B8%D1%87.rtf?type=rtf"
          }
        }
      },
      "alternate_url": "https://hh.ru/resume/6d807532ff0ed6b79f0039ed1f63386d724a62",
      "id": "6d807532ff0ed6b79f0039ed1f63386d724a62",
      "download": {
        "pdf": {
          "url": "https://api.hh.ru/resumes/6d807532ff0ed6b79f0039ed1f63386d724a62/download/%D0%9D%D0%B5%D0%BC%D0%BE%D0%B2%20%D0%9C%D0%B0%D0%BA%D1%81%D0%B8%D0%BC%20%D0%AE%D1%80%D1%8C%D0%B5%D0%B2%D0%B8%D1%87.pdf?type=pdf"
        },
        "rtf": {
          "url": "https://api.hh.ru/resumes/6d807532ff0ed6b79f0039ed1f63386d724a62/download/%D0%9D%D0%B5%D0%BC%D0%BE%D0%B2%20%D0%9C%D0%B0%D0%BA%D1%81%D0%B8%D0%BC%20%D0%AE%D1%80%D1%8C%D0%B5%D0%B2%D0%B8%D1%87.rtf?type=rtf"
        }
      },
      "platform": {
        "id": "headhunter"
      },
      "employment_form": None,
      "fly_in_fly_out_duration": [],
      "internship": None,
      "night_shifts": None,
      "ready_for_temporary_job": None,
      "work_format": [],
      "working_hours": [],
      "work_schedule_by_days": [],
      "resume_locale": {
        "id": "RU",
        "name": "Русский"
      },
      "skills": "Я - увлеченный специалист...",
      "citizenship": [
        {
          "id": "113",
          "name": "Россия",
          "url": "https://api.hh.ru/areas/113"
        }
      ],
      "work_ticket": [
        {
          "id": "113",
          "name": "Россия",
          "url": "https://api.hh.ru/areas/113"
        }
      ],
      "access": {
        "type": {
          "id": "clients",
          "name": "Видно всем работодателям, зарегистрированным на hh.ru"
        }
      },
      "birth_date": "1990-08-14",
      "contact": [
        {
          "value": {
            "country": "7",
            "city": "987",
            "number": "5056990",
            "formatted": "+7 (987) 505-69-90"
          },
          "type": { "id": "cell", "name": "Мобильный телефон" },
          "preferred": False, "comment": None, "need_verification": False, "verified": True
        },
        {
          "type": { "id": "email", "name": "Эл. почта" },
          "value": "angers07@mail.ru",
          "preferred": True
        }
      ],
      "education": {
        "level": { "id": "higher", "name": "Высшее" },
        "primary": [
          {
            "id": "372473418", "name": "Пензенский государственный университет, Пенза",
            "organization": "Факультет приборостроения, информационных технологий и систем",
            "result": "Автоматизация технологических процессов и производств (по отраслям)",
            "year": 2016, "university_acronym": "ПГУ", "name_id": "40913",
            "organization_id": "26195", "result_id": None,
            "education_level": { "id": "higher", "name": "Высшее" }
          }
        ],
        "additional": [
          {
            "id": "105064155", "name": "Специализация \"Data Engineering\"",
            "organization": "Couresra | AWS", "result": "\"Data Engineering\"", "year": 2025
          }
        ],
        "attestation": [], "elementary": []
      },
      "employment": { "id": "full", "name": "Полная занятость" },
      "employments": [ { "id": "full", "name": "Полная занятость" } ],
      "experience": [
        {
          "start": "2024-05-01", "end": None, "company": "Союзснаб", "company_id": "2288",
          "industry": None, "industries": [ { "id": "34.417", "name": "Агрохимия (продвижение, оптовая торговля)" } ],
          "area": { "id": "1", "name": "Москва", "url": "https://api.hh.ru/areas/1" },
          "company_url": "http://www.ssnab.ru/",
          "employer": {
            "id": "2288", "name": "Союзснаб", "url": "https://api.hh.ru/employers/2288",
            "alternate_url": "https://hh.ru/employer/2288",
            "logo_urls": {
              "90": "https://img.hhcdn.ru/employer-logo/6207053.png",
              "240": "https://img.hhcdn.ru/employer-logo/6207054.png",
              "original": "https://img.hhcdn.ru/employer-logo-original/1146622.png"
            }
          },
          "position": "AI engineer", "description": "***ПРОЕКТ***: Telegram-бот..."
        }
      ],
      "language": [ { "id": "rus", "name": "Русский", "level": { "id": "l1", "name": "Родной" } } ],
      "metro": None,
      "moderation_note": [],
      "recommendation": [],
      "relocation": {
        "type": { "id": "no_relocation", "name": "не могу переехать" },
        "area": [], "district": []
      },
      "schedule": { "id": "fullDay", "name": "Полный день" },
      "schedules": [ { "id": "fullDay", "name": "Полный день" } ],
      "site": [
        { "type": { "id": "personal", "name": "Другой сайт" }, "url": "https://t.me/dizilx" }
      ],
      "travel_time": { "id": "any", "name": "Не имеет значения" },
      "business_trip_readiness": { "id": "ready", "name": "готов к командировкам" },
      "next_publish_at": "2025-05-16T12:26:29+0300",
      "can_publish_or_update": True,
      "publish_url": "https://api.hh.ru/resumes/6d807532ff0ed6b79f0039ed1f63386d724a62/publish",
      "paid_services": [ { "id": "resume_autoupdating", "name": "Автоподнятие резюме", "active": False } ],
      "finished": True, "blocked": False,
      "status": { "id": "published", "name": "опубликовано" },
      "portfolio": [],
      "skill_set": [ "ChatGPT", "AI" ],
      "has_vehicle": True,
      "driver_license_types": [ { "id": "B" } ],
      "specialization": [],
      "professional_roles": [ { "id": "165", "name": "Дата-сайентист" } ],
      "tags": [],
      "progress": { # JSON ключ "progress"
        "percentage": 88, "mandatory": [],
        "recommended": [ { "id": "internship", "name": "Стажировка" } ]
      },
      "_progress": { # JSON ключ "_progress"
        "percentage": 88, "mandatory": [], "recommended": [ "internship" ]
      },
      "total_views": 1, "new_views": 1,
      "views_url": "https://api.hh.ru/resumes/6d807532ff0ed6b79f0039ed1f63386d724a62/views"
    }
    # Уменьшаем объем данных для примера
    json_data["certificate"] = [json_data["certificate"][0]]
    json_data["experience"] = [json_data["experience"][0]]

    resume_instance = Resume(**json_data)
    # print(resume_instance.model_dump_json(indent=2, by_alias=True, ensure_ascii=False)) # Для верификации
    print("Pydantic модель успешно создана и проверена на тестовых данных.")