import os
import shutil
from datetime import datetime, timedelta
from string import Template

from cmlutils.constants import ApiV1Endpoints
from cmlutils.utils import call_api_v1



class BaseWorkspaceInteractor(object):
    def __init__(
        self,
        host: str,
        username: str,
        project_name: str,
        api_key: str,
        ca_path: str,
        project_slug: str,
        apiv2_key: str = None,
        skip_tls_verification: bool = False,
    ) -> None:
        self.host = host
        self.username = username
        self.project_name = project_name
        self.api_key = api_key
        self.ca_path = ca_path
        self.project_slug = project_slug
        self._apiv2_key = apiv2_key  # V2 API key (may be None)
        self.skip_tls_verification = skip_tls_verification

    @property
    def apiv2_key(self) -> str:
        # If we already have a V2 key, use it directly
        if self._apiv2_key:
            return self._apiv2_key
        
        # If we only have V1 key, generate V2 key from it (legacy behavior)
        if self.api_key:
            endpoint = Template(ApiV1Endpoints.API_KEY.value).substitute(
                owner=self.username
            )
            json_data = {
                "expiryDate": (datetime.now() + timedelta(weeks=1)).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                )
            }
            response = call_api_v1(
                host=self.host,
                endpoint=endpoint,
                method="POST",
                api_key=self.api_key,
                json_data=json_data,
                ca_path=self.ca_path,
                skip_tls_verification=self.skip_tls_verification,
            )
            response_dict = response.json()
            _apiv2_key = response_dict["apiKey"]
            return _apiv2_key
        
        raise ValueError("No V2 API key available and cannot generate from V1 key")

    def remove_cdswctl_dir(self, file_path: str):
        if os.path.exists(file_path):
            dirname = os.path.dirname(file_path)
            shutil.rmtree(dirname, ignore_errors=True)
