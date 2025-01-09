import os
from common.util.postgres_connection_pool import PostgresConnectionPool
from common.util.mongo_session_pool import MongoSessionPool
from common.serialized_event.deserializer import Deserializer
from common.serialized_event.serializer import Serializer
from common.event_store.postgres_transactional_event_store import PostgresTransactionalEventStore
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from common.util.mongo_initializer import MongoInitializer
from common.util.postgres_initializer import PostgresInitializer
from domain.cooking_club.membership.command.submit_application.submit_application_command_controller import \
    SubmitApplicationCommandController
from domain.cooking_club.membership.command.submit_application.submit_application_command_handler import \
    SubmitApplicationCommandHandler
from domain.cooking_club.membership.projection.members_by_cuisine.members_by_cuisine_projection_controller import \
    MembersByCuisineProjectionController
from domain.cooking_club.membership.reaction.evaluate_application.evaluate_application_reaction_handler import \
    EvaluateApplicationReactionHandler
from domain.cooking_club.membership.reaction.evaluate_application.evaluate_application_reaction_controller import \
    EvaluateApplicationReactionController
from domain.cooking_club.membership.projection.members_by_cuisine.members_by_cuisine_projection_handler import \
    MembersByCuisineProjectionHandler
from domain.cooking_club.membership.projection.members_by_cuisine.membership_application_repository import \
    MembershipApplicationRepository
from domain.cooking_club.membership.projection.members_by_cuisine.cuisine_repository import CuisineRepository
from domain.cooking_club.membership.query.members_by_cuisine.members_by_cuisine_query_controller import \
    MembersByCuisineQueryController
from domain.cooking_club.membership.query.members_by_cuisine.members_by_cuisine_query_handler import \
    MembersByCuisineQueryHandler


class SharedContainer:
    def __init__(self):
        # Connection strings
        postgres_connection_string = f"postgresql://{os.getenv('EVENT_STORE_USER')}:{os.getenv('EVENT_STORE_PASSWORD')}@{os.getenv('EVENT_STORE_HOST')}:{os.getenv('EVENT_STORE_PORT')}/{os.getenv('EVENT_STORE_DATABASE_NAME')}"
        mongo_connection_string = f"mongodb://{os.getenv('MONGODB_PROJECTION_DATABASE_USERNAME')}:{os.getenv('MONGODB_PROJECTION_DATABASE_PASSWORD')}@{os.getenv('MONGODB_PROJECTION_HOST')}:{os.getenv('MONGODB_PROJECTION_PORT')}/{os.getenv('MONGODB_PROJECTION_DATABASE_NAME')}?authSource=admin"

        # Core services
        self.postgres_connection_pool = PostgresConnectionPool(
            connection_string=postgres_connection_string
        )
        self.mongo_session_pool = MongoSessionPool(
            connection_string=mongo_connection_string
        )
        self.serializer = Serializer()
        self.deserializer = Deserializer()

        # Initializers
        self.postgres_initializer = PostgresInitializer(
            connection_pool=self.postgres_connection_pool,
            event_store_database_name=os.getenv('EVENT_STORE_DATABASE_NAME'),
            event_store_table=os.getenv('EVENT_STORE_CREATE_TABLE_WITH_NAME'),
            replication_username=os.getenv('EVENT_STORE_CREATE_REPLICATION_USER_WITH_USERNAME'),
            replication_password=os.getenv('EVENT_STORE_CREATE_REPLICATION_USER_WITH_PASSWORD'),
            replication_publication=os.getenv('EVENT_STORE_CREATE_REPLICATION_PUBLICATION')
        )
        self.mongo_initializer = MongoInitializer(
            session_pool=self.mongo_session_pool,
            database_name=os.getenv('MONGODB_PROJECTION_DATABASE_NAME')
        )


class RequestContainer:
    def __init__(self, shared_container: SharedContainer):
        self.shared_container = shared_container

        self._postgres_transactional_event_store = PostgresTransactionalEventStore(
            connection_pool=self.shared_container.postgres_connection_pool,
            serializer=self.shared_container.serializer,
            deserializer=self.shared_container.deserializer,
            event_store_table=os.getenv('EVENT_STORE_CREATE_TABLE_WITH_NAME')
        )

        self._mongo_transactional_projection_operator = MongoTransactionalProjectionOperator(
            session_pool=self.shared_container.mongo_session_pool,
            database_name=os.getenv('MONGODB_PROJECTION_DATABASE_NAME')
        )

        self._cuisine_repository = CuisineRepository(
            mongo_operator=self._mongo_transactional_projection_operator
        )

        self._membership_application_repository = MembershipApplicationRepository(
            mongo_operator=self._mongo_transactional_projection_operator
        )

        self._submit_application_command_handler = SubmitApplicationCommandHandler(
            postgres_transactional_event_store=self._postgres_transactional_event_store
        )

        self._evaluate_application_reaction_handler = EvaluateApplicationReactionHandler(
            postgres_transactional_event_store=self._postgres_transactional_event_store
        )

        self._members_by_cuisine_projection_handler = MembersByCuisineProjectionHandler(
            cuisine_repository=self._cuisine_repository,
            membership_application_repository=self._membership_application_repository
        )

        self._members_by_cuisine_query_handler = MembersByCuisineQueryHandler(
            mongo_operator=self._mongo_transactional_projection_operator,
            cuisine_repository=self._cuisine_repository
        )

        self._submit_application_command_controller = SubmitApplicationCommandController(
            event_store=self._postgres_transactional_event_store,
            mongo_operator=self._mongo_transactional_projection_operator,
            submit_application_command_handler=self._submit_application_command_handler
        )

        self._evaluate_application_reaction_controller = EvaluateApplicationReactionController(
            event_store=self._postgres_transactional_event_store,
            mongo_operator=self._mongo_transactional_projection_operator,
            deserializer=self.shared_container.deserializer,
            evaluate_application_reaction_handler=self._evaluate_application_reaction_handler
        )

        self._members_by_cuisine_query_controller = MembersByCuisineQueryController(
            mongo_operator=self._mongo_transactional_projection_operator,
            members_by_cuisine_query_handler=self._members_by_cuisine_query_handler
        )

        self._members_by_cuisine_projection_controller = MembersByCuisineProjectionController(
            mongo_operator=self._mongo_transactional_projection_operator,
            deserializer=self.shared_container.deserializer,
            members_by_cuisine_projection_handler=self._members_by_cuisine_projection_handler
        )

    def submit_application_controller(self):
        return self._submit_application_command_controller

    def evaluate_application_controller(self):
        return self._evaluate_application_reaction_controller

    def members_by_cuisine_query_controller(self):
        return self._members_by_cuisine_query_controller

    def members_by_cuisine_projection_controller(self):
        return self._members_by_cuisine_projection_controller