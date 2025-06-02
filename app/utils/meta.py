import time
import hashlib
from facebook_business.adobjects.serverside.action_source import ActionSource
from facebook_business.adobjects.serverside.user_data import UserData
from facebook_business.adobjects.serverside.custom_data import CustomData
from facebook_business.adobjects.serverside.event import Event
from facebook_business.adobjects.serverside.event_request import EventRequest

from utils.hashing import hash_data

class MetaEventService:
    def __init__(self, access_token: str, pixel_id: str):
        self.access_token = access_token
        self.pixel_id = pixel_id

    def send_event(self, lead_id: str, email: str, phone: str, full_name: str, country: str, status: str, title: str):
        event_time = int(time.time())

        user_data = UserData(
            emails=[hash_data(email)] if email else [],
            phones=[hash_data(phone)] if phone else [],
            first_names=[hash_data(full_name)] if full_name else [],
            country_codes=[hash_data(country)],
            lead_id=lead_id
        )

        custom_data = CustomData(custom_properties={
            "lead_event_source": "CRM",
            "event_source": "bitrix",
            "lead_status": status,
            "lead_title": title
        })

        event = Event(
            event_name="Lead",
            event_time=event_time,
            user_data=user_data,
            custom_data=custom_data,
            action_source=ActionSource.SYSTEM_GENERATED
        )

        event_request = EventRequest(events=[event], pixel_id=self.pixel_id)
        return event_time, event_request.execute()
