import asyncio
import aiohttp
from datetime import datetime
from typing_extensions import Self
from typing import TypeAlias, Optional
from exceptions import APIException

JsonData: TypeAlias = dict
Url: TypeAlias = str
BitlinkHash:  TypeAlias = str
ApiResponse: TypeAlias = JsonData

class APIResponse:
    def __init__(self, **attrs):
        self.__dict__.update(attrs)

class BitlyAPI:
  api_url = 'https://api-ssl.bitly.com'

  def __init__(self, token: str) -> None:
    self.token = token
    self.link = Link(api=self)
    self.organization = Organization(api=self)
    self.group = Group(api=self)

  async def __aenter__(self) -> Self:
    headers = {"Authorization": f"Bearer {self.token}"}
    self._session = aiohttp.ClientSession(self.api_url, headers=headers)
    return self

  async def __aexit__(self, *err) -> None:
    await self._session.close()
    self._session = None

  async def _return_api_response(self, resp: aiohttp.ClientResponse) -> APIResponse:
    try:
      data = await resp.json()
      resp.raise_for_status()
    except aiohttp.ClientResponseError as e:
      raise APIException(f'[{resp.status}] {e.message}')
    json_response = await resp.json()
    return APIResponse(**json_response)

  async def post(self, url: str, headers: Optional[dict]=None, json: Optional[JsonData]=None) -> APIResponse:
    if headers is None:
      headers = {}
    headers.setdefault('Content-Type', 'application/json')
    async with self._session.post(url, headers=headers, json=json) as resp:
      return await self._return_api_response(resp)

  async def get(self, url: str, headers: Optional[dict]=None, params: Optional[dict]=None) -> APIResponse:
    async with self._session.get(url, headers=headers, params=params) as resp:
      return await self._return_api_response(resp)
    
  async def delete(self, url: str, headers: Optional[dict]=None, params: Optional[dict]=None) -> APIResponse:
    async with self._session.delete(url, headers=headers, params=params) as resp:
      return await self._return_api_response(resp)

class Organization:
  def __init__(self, api: BitlyAPI) -> None:
    self.api = api
  async def retrieve(self) -> ApiResponse:
    return await self.api.get('/v4/organizations')

class Group:
  def __init__(self, api: BitlyAPI) -> None:
    self.api = api
  
  async def retrieve(self, organization_guid: str) -> ApiResponse:
    return await self.api.get('/v4/groups', params={'organization_guid': organization_guid})
  
class Link:
  def __init__(self, api: BitlyAPI) -> None:
    self.api = api
  
  def _get_domain_and_hash(self, link: str) -> tuple[str, str]:
    if '/' in link:
      link_parts = link.split('/')
      domain = link_parts[-2]
      link_hash = link_parts[-1]
    else:
      domain = 'bit.ly'
      link_hash = link
    return (domain, link_hash)

  async def shorten(self, long_url: str, group_guid: str) -> ApiResponse:
    return await self.api.post('/v4/shorten', json={
      'long_url': long_url,
      'group_guid': group_guid
    })

  async def delete(self, link: str) -> ApiResponse:
    domain, link_hash = self._get_domain_and_hash(link)
    return await self.api.delete(f'/v4/bitlinks/{domain}/{link_hash}')

  async def clicks(self, link: str, unit: str='day', unit_count: int=-1, last_unit_datetime: Optional[datetime]=None) -> ApiResponse:
    '''
    Получаем количество кликов по ссылке за заданный период
    Шаг периода unit - "minute","hour","day","week","month"
    Количество запрашиваемых периодов unit_count, по умолчанию 10, а при указании -1 все периоды
    Время окончания последнего получаемого периода last_unit_datetime, по умолчанию текущее время
    '''
    domain, link_hash = self._get_domain_and_hash(link)
    request_params = {
      'unit': unit,
      'units': unit_count
    }
    if last_unit_datetime:
      request_params['unit_reference'] = last_unit_datetime.isoformat()
    clicks_response = await self.api.get(f'/v4/bitlinks/{domain}/{link_hash}/clicks', params=request_params)
    clicks_response.__dict__['link_clicks_periods'] = clicks_response.link_clicks
    total_clicks = 0
    for period_data in clicks_response.link_clicks_periods:
      total_clicks += period_data['clicks']
    clicks_response.link_clicks = total_clicks
    return clicks_response