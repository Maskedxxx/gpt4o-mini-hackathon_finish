"""Клиент для работы с HH API"""
import re
import time
from typing import Optional
import aiohttp
from urllib.parse import urlencode
import requests

from domain.dto import Resume, Vacancy, UserToken
from domain.services import IHHClient
from config import hh_settings
from loguru import logger


class HHClient(IHHClient):
    """Реализация клиента для HH API"""
    
    def __init__(self):
        self.base_url = hh_settings.api_base_url
        self.client_id = hh_settings.client_id
        self.client_secret = hh_settings.client_secret
        self.redirect_uri = hh_settings.redirect_uri
    
    async def get_auth_url(self, state: str) -> str:
        """Получить URL для OAuth авторизации"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'scope': 'read write'  # Добавляем права на чтение и запись
        }
        return f"https://hh.ru/oauth/authorize?{urlencode(params)}"
    
    async def exchange_code(self, code: str) -> UserToken:
        """Обменять authorization code на токены"""
        # HH требует использовать обычный requests для OAuth токенов
        url = "https://hh.ru/oauth/token"
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        
        try:
            response = requests.post(url, data=data, headers=headers)
            logger.debug(f"Exchange code response: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Exchange code failed: {response.text}")
                raise Exception(f"Failed to exchange code: {response.status_code} - {response.text}")
            
            json_data = response.json()
            
            return UserToken(
                user_id=0,  # Будет установлен позже
                access_token=json_data['access_token'],
                refresh_token=json_data['refresh_token'],
                expires_at=int(time.time()) + json_data['expires_in']
            )
        except Exception as e:
            logger.error(f"Exchange code error: {e}")
            raise
    
    async def refresh_access_token(self, refresh_token: str) -> UserToken:
        """Обновить access token используя refresh token"""
        # HH требует использовать обычный requests для OAuth токенов
        url = "https://hh.ru/oauth/token"
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        
        try:
            response = requests.post(url, data=data, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Refresh token failed: {response.text}")
                raise Exception(f"Failed to refresh token: {response.status_code} - {response.text}")
            
            json_data = response.json()
            
            return UserToken(
                user_id=0,  # Будет установлен позже
                access_token=json_data['access_token'],
                refresh_token=json_data['refresh_token'],
                expires_at=int(time.time()) + json_data['expires_in']
            )
        except Exception as e:
            logger.error(f"Refresh token error: {e}")
            raise
    
    async def get_resume(self, resume_id: str, access_token: str) -> Resume:
        """Получить резюме по ID"""
        # Извлекаем ID из URL если это ссылка
        resume_id = self._extract_id_from_url(resume_id, 'resume')
        logger.debug(f"Extracted resume ID: {resume_id}")
        
        url = f"{self.base_url}/resumes/{resume_id}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Accept': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"Failed to get resume: {response.status} - {text}")
                
                try:
                    data = await response.json()
                    logger.debug(f"Resume data type: {type(data)}")
                    logger.debug(f"Resume keys: {data.keys() if isinstance(data, dict) else 'not a dict'}")
                    
                    # Парсим резюме в наш DTO
                    # Извлекаем email и телефон из списка контактов
                    email = ''
                    phone = ''
                    
                    contacts = data.get('contact', [])
                    logger.debug(f"Contacts type: {type(contacts)}, length: {len(contacts) if isinstance(contacts, list) else 'not a list'}")
                    
                    for contact in contacts:
                        logger.debug(f"Contact item: {contact}")
                        if isinstance(contact, dict) and 'type' in contact:
                            if contact['type']['id'] == 'email':
                                email = contact['value'] if isinstance(contact['value'], str) else ''
                            elif contact['type']['id'] == 'cell':
                                phone_val = contact.get('value', {})
                                phone = phone_val.get('formatted', '') if isinstance(phone_val, dict) else ''
                    
                    return Resume(
                        id=data['id'],
                        fullname=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
                        contacts={
                            'email': email,
                            'phone': phone
                        },
                        skills=data.get('skill_set', []),
                        work_experience=[{
                            'position': exp.get('position', ''),
                            'company': exp.get('company', ''),
                            'description': exp.get('description', ''),
                            'start': exp.get('start', ''),
                            'end': exp.get('end', '')
                        } for exp in data.get('experience', [])],
                        education=[{
                            'name': edu.get('name', ''),
                            'organization': edu.get('organization', ''),
                            'year': edu.get('year', 0)
                        } for edu in data.get('education', {}).get('primary', [])],
                        summary=data.get('skills', '')
                    )
                except Exception as e:
                    logger.error(f"Error parsing resume data: {e}")
                    logger.error(f"Resume response text: {await response.text()}")
                    raise
    
    async def get_vacancy(self, vacancy_id: str) -> Vacancy:
        """Получить вакансию по ID"""
        # Извлекаем ID из URL если это ссылка
        vacancy_id = self._extract_id_from_url(vacancy_id, 'vacancy')
        
        url = f"{self.base_url}/vacancies/{vacancy_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Accept': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"Failed to get vacancy: {response.status} - {text}")
                
                data = await response.json()
                
                # Парсим вакансию в наш DTO
                requirements = []
                responsibilities = []
                
                # Парсим key_skills
                if data.get('key_skills'):
                    requirements.extend([skill['name'] for skill in data['key_skills']])
                
                # Добавляем требования из опыта
                if data.get('experience'):
                    requirements.append(f"Опыт: {data['experience']['name']}")
                
                # Добавляем языки
                for lang in data.get('languages', []):
                    requirements.append(f"{lang['name']}: {lang['level']['name']}")
                
                # Простое описание как обязанности и требования
                description = data.get('description', '')
                if description:
                    # Можно попробовать разделить по ключевым словам или просто взять всё
                    responsibilities.append(description[:500])  # Берём первые 500 символов
                
                return Vacancy(
                    id=data['id'],
                    title=data['name'],
                    company=data.get('employer', {}).get('name', ''),
                    requirements=requirements or ['Не указаны'],
                    responsibilities=responsibilities or [description[:500] if description else 'Не указаны'],
                    salary=None  # Упрощаем для MVP
                )
    
    async def update_resume(self, resume_id: str, new_text: str, access_token: str) -> bool:
        """Обновить резюме"""
        # В MVP просто возвращаем успех
        # В реальной версии нужно будет реализовать обновление через API
        logger.info(f"Would update resume {resume_id} with new text")
        return True
    
    def _extract_id_from_url(self, url_or_id: str, entity_type: str) -> str:
        """Извлечь ID из URL HH"""
        if url_or_id.startswith('http'):
            # Паттерн для извлечения ID из URL
            # ID резюме может быть разной длины (обычно 32-40 символов)
            pattern = r'/(?:resume|vacancy)/([a-f0-9]+)'
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
            raise ValueError(f"Invalid {entity_type} URL: {url_or_id}")
        return url_or_id