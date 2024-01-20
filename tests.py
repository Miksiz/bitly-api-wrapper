import unittest
import os
import asyncio
from dotenv import load_dotenv, find_dotenv
from bitly_api import BitlyAPI

# Загрузка переменных окружения
dotenv_file = find_dotenv()
load_dotenv(dotenv_file)

class BitlyTokenTestCase(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.bitly_token = os.getenv("BITLY_TOKEN")
  
  def test_token_exists(self):
    self.assertIsNotNone(self.bitly_token)

  def test_token_format(self):
    self.assertRegex(self.bitly_token, r'^[0-9a-f]{40}$')

class BitlyAPIClassTestCase(unittest.IsolatedAsyncioTestCase):
  async def test_context_manager(self):
    try:
      async with BitlyAPI(token=None) as bitly_api:
        pass
    except BaseException as e:
      self.assertIsNone(e)

class BitlyAPIRequestsTestCase(unittest.IsolatedAsyncioTestCase):
  @classmethod
  def setUpClass(cls):
    cls.bitly_token = os.getenv("BITLY_TOKEN")
    cls.organization_guid = os.getenv("ORGANIZATION_GUID")
    cls.organization_guid_known = asyncio.Event()
    if cls.organization_guid:
      cls.organization_guid_known.set()
    cls.group_guid = os.getenv("GROUP_GUID")
    cls.group_guid_known = asyncio.Event()
    if cls.group_guid:
      cls.group_guid_known.set()
    cls.link_bithash = None

  async def asyncSetUp(self):
    unmanaged_api = BitlyAPI(self.bitly_token)
    self.api = await unmanaged_api.__aenter__()
  
  async def asyncTearDown(self):
    await self.api.__aexit__(None, None, None)

  async def _get_organization_guid(self) -> str:
    if self.organization_guid:
      return self.organization_guid
    try:
      response = await self.api.organization.retrieve()
    except BaseException as e:
      self.assertIsNone(e)
    self.assertTrue(response)
    self.assertTrue(hasattr(response, 'organizations'))
    first_organization = response.organizations[0]
    self.assertTrue(first_organization.get('guid'))
    self.organization_guid = first_organization['guid']
    return self.organization_guid
  
  async def _get_group_guid(self, organization_guid: str) -> str:
    if self.group_guid:
      return self.group_guid
    try:
      response = await self.api.group.retrieve(organization_guid)
    except BaseException as e:
      self.assertIsNone(e)
    self.assertTrue(response)
    self.assertTrue(hasattr(response, 'groups'))
    first_group = response.groups[0]
    self.assertTrue(first_group.get('guid'))
    self.group_guid = first_group['guid']
    return self.group_guid

  def test_get_domain_and_hash(self):
    link = 'https://bit.ly/493eBBU'
    domain, link_hash = self.api.link._get_domain_and_hash(link)
    self.assertEqual(domain, 'bit.ly')
    self.assertEqual(link_hash, '493eBBU')
    link = 'https://other.ly/493eBBU'
    domain, link_hash = self.api.link._get_domain_and_hash(link)
    self.assertEqual(domain, 'other.ly')
    self.assertEqual(link_hash, '493eBBU')
    link = 'other.ly/493eBBU'
    domain, link_hash = self.api.link._get_domain_and_hash(link)
    self.assertEqual(domain, 'other.ly')
    self.assertEqual(link_hash, '493eBBU')
    link = '493eBBU'
    domain, link_hash = self.api.link._get_domain_and_hash(link)
    self.assertEqual(domain, 'bit.ly')
    self.assertEqual(link_hash, '493eBBU')

  async def test_create_get_clicks_and_remove_link(self):
    organization_guid = await self._get_organization_guid()
    group_guid = await self._get_group_guid(organization_guid)
    long_url = os.getenv('LONG_URL', 'https://github.com/Miksiz/bitly-api-wrapper')
    try:
      response = await self.api.link.shorten(long_url, group_guid)
    except BaseException as e:
      self.assertIsNone(e)
    self.assertTrue(hasattr(response, 'id'))
    short_url = response.id
    try:
      response = await self.api.link.clicks(link=short_url, unit_count=1)
    except BaseException as e:
      self.assertIsNone(e)
    self.assertTrue(response)
    self.assertTrue(hasattr(response, 'link_clicks'))
    self.assertIsNotNone(response.link_clicks)
    try:
      response = await self.api.link.delete(short_url)
    except BaseException as e:
      self.assertIsNone(e)
    self.assertTrue(hasattr(response, 'links_deleted'))
    self.assertTrue(response.links_deleted[0].get('id'))
    deleted_link = response.links_deleted[0]['id']
    self.assertEqual(short_url, deleted_link)


if __name__ == '__main__':
  unittest.main()