import base64
from functools import cache

from django.conf import settings
from docusign_esign import ApiClient, EnvelopesApi, RecipientViewRequest
from docusign_esign.models import (
    Document,
    EnvelopeDefinition,
    Recipients,
    Signer,
    SignHere,
    Tabs,
    Text,
)
from ninja import Router

from envelope.schema import CreateEnvelopeIn
from sign_it.jwt import get_access_token

router = Router()


def get_api_client():
    """Creates the API client using base path and access token."""
    access_token = get_access_token()
    api_client = ApiClient(
        host=settings.DOCUSIGN_BASE_PATH,
        header_name="Authorization",
        header_value=f"Bearer {access_token}",
    )
    return api_client


def create_envelope_definition(envelopes_api, first_signer, second_signer, document):
    envelope_definition = EnvelopeDefinition(
        email_subject="Please sign this document",
        documents=[document],
        recipients=Recipients(signers=[first_signer, second_signer]),
        status="sent",
    )
    results = envelopes_api.create_envelope(
        account_id=settings.DOCUSIGN_ACCOUNT_ID, envelope_definition=envelope_definition
    )

    return results.envelope_id


def create_recipient_view_request(
    envelopes_api, envelope_id, user_id, username, email, return_url
):
    recipient_view_request = RecipientViewRequest(
        authentication_method="None",
        client_user_id=user_id,
        recipient_id="1",
        return_url=return_url,
        user_name=username,
        email=email,
    )
    results = envelopes_api.create_recipient_view(
        account_id=settings.DOCUSIGN_ACCOUNT_ID,
        envelope_id=envelope_id,
        recipient_view_request=recipient_view_request,
    )
    return results


@router.post("/", response=dict)
def create_embedded_envelope(request, schema_in: CreateEnvelopeIn):
    """Create the envelope for DocuSign"""
    html = html_generator()

    document = Document(
        document_base64=html,
        name="Agreement",
        file_extension="html",
        document_id="1",
    )

    first_signer = Signer(
        email=schema_in.first_party.email,
        name=schema_in.first_party.name,
        recipient_id="1",
        routing_order="1",
        tabs=Tabs(
            sign_here_tabs=[
                SignHere(
                    anchor_string="/signer1sig/",
                    anchor_units="pixels",
                    anchor_x_offset="0",
                    anchor_y_offset="0",
                )
            ],
            text_tabs=[
                Text(
                    anchor_string="/fullname/",
                    anchor_units="pixels",
                    anchor_x_offset="0",
                    anchor_y_offset="-2",
                    tab_label="Full Name",
                ),
                Text(
                    anchor_string="/date/",
                    anchor_units="pixels",
                    anchor_x_offset="0",
                    anchor_y_offset="-2",
                    tab_label="Date",
                ),
            ],
        ),
        client_user_id=request.user.id,
    )

    second_signer = Signer(
        email=schema_in.second_party.email,
        name=schema_in.second_party.name,
        recipient_id="2",
        routing_order="2",
        tabs=Tabs(
            sign_here_tabs=[
                SignHere(
                    anchor_string="/signer2sig/",
                    anchor_units="pixels",
                    anchor_x_offset="0",
                    anchor_y_offset="0",
                )
            ],
            text_tabs=[
                Text(
                    anchor_string="/fullname2/",
                    anchor_units="pixels",
                    anchor_x_offset="0",
                    anchor_y_offset="-2",
                    tab_label="Full Name - Second signer",
                ),
                Text(
                    anchor_string="/date2/",
                    anchor_units="pixels",
                    anchor_x_offset="0",
                    anchor_y_offset="-2",
                    tab_label="Date - Second signer",
                ),
            ],
        ),
    )

    api_client = get_api_client()
    envelopes_api = EnvelopesApi(api_client)

    envelope_id = create_envelope_definition(
        envelopes_api,
        first_signer=first_signer,
        second_signer=second_signer,
        document=document,
    )
    recipient_view = create_recipient_view_request(
        envelopes_api,
        envelope_id=envelope_id,
        user_id=request.user.id,
        username=schema_in.first_party.name,
        email=schema_in.first_party.email,
        return_url="http://localhost:5173/envelope/create/success",
    )
    return {"signing_url": recipient_view.url}


@cache
def html_generator():
    html = """
    <!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agreement</title>
</head>

<body>
    <h1>Agreement</h1>

    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.Ut enim ad minim veniam, quis
        nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat Sed do eius
        mod tempor incididunt ut labore et dolore magna aliqua.
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut
        labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco
        laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in
        voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupid
        atat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
    </p>

    <h3>First Signer</h3>
    <p>● Full Name: <span style="color:white">/fullname/</span> </p>
    <p>● Date: <span style="color:white">/date/</span></p>
    <p>● Signature: <span style="color:white; font-size:48px">/signer1sig/</span></p>

    <p style="font-size: medium;">Lorem ipsum odor amet, consectetuer adipiscing elit. Vestibulum pr
        etium potenti molestie luctus turpis etiam fermentum odio. Himenaeos senectus gravida sed et
        iam ut. Ullamcorper in convallis mauris libero taciti platea ipsum tellus proin. Condimentum
        id vel pharetra integer ligula, primis tristique ridiculus.
    </p>

    <h3>Second Signer</h3>
    <p>● Full Name: <span style="color:white">/fullname2/</span></p>
    <p>● Date: <span style="color:white">/date2/</span></p>
    <p>● Signature: <span style="color:white; font-size:48px">/signer2sig/</span></p>

</body>
</html>
"""
    return base64.b64encode(bytes(html, "utf-8")).decode("ascii")
