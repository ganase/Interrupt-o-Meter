from __future__ import annotations

from typing import Any

import msal

from app.config import settings


class GraphAuthError(RuntimeError):
    pass


def acquire_graph_access_token() -> str:
    if not settings.ms_client_id or not settings.ms_tenant_id:
        raise GraphAuthError("Microsoft Graph credentials are not configured")

    authority = f"https://login.microsoftonline.com/{settings.ms_tenant_id}"
    app = msal.PublicClientApplication(settings.ms_client_id, authority=authority)
    scopes = [settings.graph_scope]

    accounts = app.get_accounts()
    result: dict[str, Any] | None = None
    if accounts:
        result = app.acquire_token_silent(scopes=scopes, account=accounts[0])

    if not result:
        flow = app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            raise GraphAuthError("Device code flow could not be initiated")
        print(flow.get("message"))
        result = app.acquire_token_by_device_flow(flow)

    if not result or "access_token" not in result:
        raise GraphAuthError(f"Graph auth failed: {result}")
    return str(result["access_token"])
