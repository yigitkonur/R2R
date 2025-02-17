import logging
import textwrap
from typing import Optional
from uuid import UUID

from fastapi import Body, Depends, Path, Query

from core.base import Message, R2RException
from core.base.api.models import (
    GenericBooleanResponse,
    WrappedBooleanResponse,
    WrappedConversationMessagesResponse,
    WrappedConversationResponse,
    WrappedConversationsResponse,
    WrappedMessageResponse,
)

from ...abstractions import R2RProviders, R2RServices
from .base_router import BaseRouterV3

logger = logging.getLogger()


class ConversationsRouter(BaseRouterV3):
    def __init__(
        self,
        providers: R2RProviders,
        services: R2RServices,
    ):
        super().__init__(providers, services)

    def _setup_routes(self):
        @self.router.post(
            "/conversations",
            summary="Create a new conversation",
            dependencies=[Depends(self.rate_limit_dependency)],
            openapi_extra={
                "x-codeSamples": [
                    {
                        "lang": "Python",
                        "source": textwrap.dedent(
                            """
                            from r2r import R2RClient

                            client = R2RClient("http://localhost:7272")
                            # when using auth, do client.login(...)

                            result = client.conversations.create()
                            """
                        ),
                    },
                    {
                        "lang": "JavaScript",
                        "source": textwrap.dedent(
                            """
                            const { r2rClient } = require("r2r-js");

                            const client = new r2rClient("http://localhost:7272");

                            function main() {
                                const response = await client.conversations.create();
                            }

                            main();
                            """
                        ),
                    },
                    {
                        "lang": "CLI",
                        "source": textwrap.dedent(
                            """
                            r2r conversations create
                            """
                        ),
                    },
                    {
                        "lang": "cURL",
                        "source": textwrap.dedent(
                            """
                            curl -X POST "https://api.example.com/v3/conversations" \\
                                -H "Authorization: Bearer YOUR_API_KEY"
                            """
                        ),
                    },
                ]
            },
        )
        @self.base_endpoint
        async def create_conversation(
            name: Optional[str] = Body(
                None, description="The name of the conversation", embed=True
            ),
            auth_user=Depends(self.providers.auth.auth_wrapper()),
        ) -> WrappedConversationResponse:
            """
            Create a new conversation.

            This endpoint initializes a new conversation for the authenticated user.
            """
            user_id = auth_user.id

            return await self.services.management.create_conversation(
                user_id=user_id,
                name=name,
            )

        @self.router.get(
            "/conversations",
            summary="List conversations",
            dependencies=[Depends(self.rate_limit_dependency)],
            openapi_extra={
                "x-codeSamples": [
                    {
                        "lang": "Python",
                        "source": textwrap.dedent(
                            """
                            from r2r import R2RClient

                            client = R2RClient("http://localhost:7272")
                            # when using auth, do client.login(...)

                            result = client.conversations.list(
                                offset=0,
                                limit=10,
                            )
                            """
                        ),
                    },
                    {
                        "lang": "JavaScript",
                        "source": textwrap.dedent(
                            """
                            const { r2rClient } = require("r2r-js");

                            const client = new r2rClient("http://localhost:7272");

                            function main() {
                                const response = await client.conversations.list();
                            }

                            main();
                            """
                        ),
                    },
                    {
                        "lang": "CLI",
                        "source": textwrap.dedent(
                            """
                            r2r conversations list
                            """
                        ),
                    },
                    {
                        "lang": "cURL",
                        "source": textwrap.dedent(
                            """
                            curl -X GET "https://api.example.com/v3/conversations?offset=0&limit=10" \\
                                -H "Authorization: Bearer YOUR_API_KEY"
                            """
                        ),
                    },
                ]
            },
        )
        @self.base_endpoint
        async def list_conversations(
            ids: list[str] = Query(
                [],
                description="A list of conversation IDs to retrieve. If not provided, all conversations will be returned.",
            ),
            offset: int = Query(
                0,
                ge=0,
                description="Specifies the number of objects to skip. Defaults to 0.",
            ),
            limit: int = Query(
                100,
                ge=1,
                le=1000,
                description="Specifies a limit on the number of objects to return, ranging between 1 and 100. Defaults to 100.",
            ),
            auth_user=Depends(self.providers.auth.auth_wrapper()),
        ) -> WrappedConversationsResponse:
            """
            List conversations with pagination and sorting options.

            This endpoint returns a paginated list of conversations for the authenticated user.
            """
            requesting_user_id = (
                None if auth_user.is_superuser else [auth_user.id]
            )

            conversation_uuids = [
                UUID(conversation_id) for conversation_id in ids
            ]

            conversations_response = (
                await self.services.management.conversations_overview(
                    offset=offset,
                    limit=limit,
                    conversation_ids=conversation_uuids,
                    user_ids=requesting_user_id,
                )
            )
            return conversations_response["results"], {  # type: ignore
                "total_entries": conversations_response["total_entries"]
            }

        @self.router.get(
            "/conversations/{id}",
            summary="Get conversation details",
            dependencies=[Depends(self.rate_limit_dependency)],
            openapi_extra={
                "x-codeSamples": [
                    {
                        "lang": "Python",
                        "source": textwrap.dedent(
                            """
                            from r2r import R2RClient

                            client = R2RClient("http://localhost:7272")
                            # when using auth, do client.login(...)

                            result = client.conversations.get(
                                "123e4567-e89b-12d3-a456-426614174000"
                            )
                            """
                        ),
                    },
                    {
                        "lang": "JavaScript",
                        "source": textwrap.dedent(
                            """
                            const { r2rClient } = require("r2r-js");

                            const client = new r2rClient("http://localhost:7272");

                            function main() {
                                const response = await client.conversations.retrieve({
                                    id: "123e4567-e89b-12d3-a456-426614174000",
                                });
                            }

                            main();
                            """
                        ),
                    },
                    {
                        "lang": "CLI",
                        "source": textwrap.dedent(
                            """
                            r2r conversations retrieve 123e4567-e89b-12d3-a456-426614174000
                            """
                        ),
                    },
                    {
                        "lang": "cURL",
                        "source": textwrap.dedent(
                            """
                            curl -X GET "https://api.example.com/v3/conversations/123e4567-e89b-12d3-a456-426614174000" \\
                                -H "Authorization: Bearer YOUR_API_KEY"
                            """
                        ),
                    },
                ]
            },
        )
        @self.base_endpoint
        async def get_conversation(
            id: UUID = Path(
                ..., description="The unique identifier of the conversation"
            ),
            auth_user=Depends(self.providers.auth.auth_wrapper()),
        ) -> WrappedConversationMessagesResponse:
            """
            Get details of a specific conversation.

            This endpoint retrieves detailed information about a single conversation identified by its UUID.
            """
            requesting_user_id = (
                None if auth_user.is_superuser else [auth_user.id]
            )

            conversation = await self.services.management.get_conversation(
                conversation_id=id,
                user_ids=requesting_user_id,
            )
            return conversation

        @self.router.post(
            "/conversations/{id}",
            summary="Update conversation",
            dependencies=[Depends(self.rate_limit_dependency)],
            openapi_extra={
                "x-codeSamples": [
                    {
                        "lang": "Python",
                        "source": textwrap.dedent(
                            """
                            from r2r import R2RClient

                            client = R2RClient("http://localhost:7272")
                            # when using auth, do client.login(...)

                            result = client.conversations.update("123e4567-e89b-12d3-a456-426614174000", "new_name")
                            """
                        ),
                    },
                    {
                        "lang": "JavaScript",
                        "source": textwrap.dedent(
                            """
                            const { r2rClient } = require("r2r-js");

                            const client = new r2rClient("http://localhost:7272");

                            function main() {
                                const response = await client.conversations.update({
                                    id: "123e4567-e89b-12d3-a456-426614174000",
                                    name: "new_name",
                                });
                            }

                            main();
                            """
                        ),
                    },
                    {
                        "lang": "CLI",
                        "source": textwrap.dedent(
                            """
                            r2r conversations delete 123e4567-e89b-12d3-a456-426614174000
                            """
                        ),
                    },
                    {
                        "lang": "cURL",
                        "source": textwrap.dedent(
                            """
                            curl -X POST "https://api.example.com/v3/conversations/123e4567-e89b-12d3-a456-426614174000" \
                                -H "Authorization: Bearer YOUR_API_KEY" \
                                -H "Content-Type: application/json" \
                                -d '{"name": "new_name"}'
                            """
                        ),
                    },
                ]
            },
        )
        @self.base_endpoint
        async def update_conversation(
            id: UUID = Path(
                ...,
                description="The unique identifier of the conversation to delete",
            ),
            name: str = Body(
                ...,
                description="The updated name for the conversation",
                embed=True,
            ),
            auth_user=Depends(self.providers.auth.auth_wrapper()),
        ) -> WrappedConversationResponse:
            """
            Update an existing conversation.

            This endpoint updates the name of an existing conversation identified by its UUID.
            """
            return await self.services.management.update_conversation(
                conversation_id=id,
                name=name,
            )

        @self.router.delete(
            "/conversations/{id}",
            summary="Delete conversation",
            dependencies=[Depends(self.rate_limit_dependency)],
            openapi_extra={
                "x-codeSamples": [
                    {
                        "lang": "Python",
                        "source": textwrap.dedent(
                            """
                            from r2r import R2RClient

                            client = R2RClient("http://localhost:7272")
                            # when using auth, do client.login(...)

                            result = client.conversations.delete("123e4567-e89b-12d3-a456-426614174000")
                            """
                        ),
                    },
                    {
                        "lang": "JavaScript",
                        "source": textwrap.dedent(
                            """
                            const { r2rClient } = require("r2r-js");

                            const client = new r2rClient("http://localhost:7272");

                            function main() {
                                const response = await client.conversations.delete({
                                    id: "123e4567-e89b-12d3-a456-426614174000",
                                });
                            }

                            main();
                            """
                        ),
                    },
                    {
                        "lang": "CLI",
                        "source": textwrap.dedent(
                            """
                            r2r conversations delete 123e4567-e89b-12d3-a456-426614174000
                            """
                        ),
                    },
                    {
                        "lang": "cURL",
                        "source": textwrap.dedent(
                            """
                            curl -X DELETE "https://api.example.com/v3/conversations/123e4567-e89b-12d3-a456-426614174000" \\
                                -H "Authorization: Bearer YOUR_API_KEY"
                            """
                        ),
                    },
                ]
            },
        )
        @self.base_endpoint
        async def delete_conversation(
            id: UUID = Path(
                ...,
                description="The unique identifier of the conversation to delete",
            ),
            auth_user=Depends(self.providers.auth.auth_wrapper()),
        ) -> WrappedBooleanResponse:
            """
            Delete an existing conversation.

            This endpoint deletes a conversation identified by its UUID.
            """
            requesting_user_id = (
                None if auth_user.is_superuser else [auth_user.id]
            )

            await self.services.management.delete_conversation(
                conversation_id=id,
                user_ids=requesting_user_id,
            )
            return GenericBooleanResponse(success=True)  # type: ignore

        @self.router.post(
            "/conversations/{id}/messages",
            summary="Add message to conversation",
            dependencies=[Depends(self.rate_limit_dependency)],
            openapi_extra={
                "x-codeSamples": [
                    {
                        "lang": "Python",
                        "source": textwrap.dedent(
                            """
                            from r2r import R2RClient

                            client = R2RClient("http://localhost:7272")
                            # when using auth, do client.login(...)

                            result = client.conversations.add_message(
                                "123e4567-e89b-12d3-a456-426614174000",
                                content="Hello, world!",
                                role="user",
                                parent_id="parent_message_id",
                                metadata={"key": "value"}
                            )
                            """
                        ),
                    },
                    {
                        "lang": "JavaScript",
                        "source": textwrap.dedent(
                            """
                            const { r2rClient } = require("r2r-js");

                            const client = new r2rClient("http://localhost:7272");

                            function main() {
                                const response = await client.conversations.addMessage({
                                    id: "123e4567-e89b-12d3-a456-426614174000",
                                    content: "Hello, world!",
                                    role: "user",
                                    parentId: "parent_message_id",
                                });
                            }

                            main();
                            """
                        ),
                    },
                    {
                        "lang": "cURL",
                        "source": textwrap.dedent(
                            """
                            curl -X POST "https://api.example.com/v3/conversations/123e4567-e89b-12d3-a456-426614174000/messages" \\
                                -H "Authorization: Bearer YOUR_API_KEY" \\
                                -H "Content-Type: application/json" \\
                                -d '{"content": "Hello, world!", "parent_id": "parent_message_id", "metadata": {"key": "value"}}'
                            """
                        ),
                    },
                ]
            },
        )
        @self.base_endpoint
        async def add_message(
            id: UUID = Path(
                ..., description="The unique identifier of the conversation"
            ),
            content: str = Body(
                ..., description="The content of the message to add"
            ),
            role: str = Body(
                ..., description="The role of the message to add"
            ),
            parent_id: Optional[UUID] = Body(
                None, description="The ID of the parent message, if any"
            ),
            metadata: Optional[dict[str, str]] = Body(
                None, description="Additional metadata for the message"
            ),
            auth_user=Depends(self.providers.auth.auth_wrapper()),
        ) -> WrappedMessageResponse:
            """
            Add a new message to a conversation.

            This endpoint adds a new message to an existing conversation.
            """
            if content == "":
                raise R2RException("Content cannot be empty", status_code=400)
            if role not in ["user", "assistant", "system"]:
                raise R2RException("Invalid role", status_code=400)
            message = Message(role=role, content=content)
            return await self.services.management.add_message(
                conversation_id=id,
                content=message,
                parent_id=parent_id,
                metadata=metadata,
            )

        @self.router.post(
            "/conversations/{id}/messages/{message_id}",
            summary="Update message in conversation",
            dependencies=[Depends(self.rate_limit_dependency)],
            openapi_extra={
                "x-codeSamples": [
                    {
                        "lang": "Python",
                        "source": textwrap.dedent(
                            """
                            from r2r import R2RClient

                            client = R2RClient("http://localhost:7272")
                            # when using auth, do client.login(...)

                            result = client.conversations.update_message(
                                "123e4567-e89b-12d3-a456-426614174000",
                                "message_id_to_update",
                                content="Updated content"
                            )
                            """
                        ),
                    },
                    {
                        "lang": "JavaScript",
                        "source": textwrap.dedent(
                            """
                            const { r2rClient } = require("r2r-js");

                            const client = new r2rClient("http://localhost:7272");

                            function main() {
                                const response = await client.conversations.updateMessage({
                                    id: "123e4567-e89b-12d3-a456-426614174000",
                                    messageId: "message_id_to_update",
                                    content: "Updated content",
                                });
                            }

                            main();
                            """
                        ),
                    },
                    {
                        "lang": "cURL",
                        "source": textwrap.dedent(
                            """
                            curl -X POST "https://api.example.com/v3/conversations/123e4567-e89b-12d3-a456-426614174000/messages/message_id_to_update" \\
                                -H "Authorization: Bearer YOUR_API_KEY" \\
                                -H "Content-Type: application/json" \\
                                -d '{"content": "Updated content"}'
                            """
                        ),
                    },
                ]
            },
        )
        @self.base_endpoint
        async def update_message(
            id: UUID = Path(
                ..., description="The unique identifier of the conversation"
            ),
            message_id: UUID = Path(
                ..., description="The ID of the message to update"
            ),
            content: Optional[str] = Body(
                None, description="The new content for the message"
            ),
            metadata: Optional[dict[str, str]] = Body(
                None, description="Additional metadata for the message"
            ),
            auth_user=Depends(self.providers.auth.auth_wrapper()),
        ) -> WrappedMessageResponse:
            """
            Update an existing message in a conversation.

            This endpoint updates the content of an existing message in a conversation.
            """
            return await self.services.management.edit_message(
                message_id=message_id,
                new_content=content,
                additional_metadata=metadata,
            )
